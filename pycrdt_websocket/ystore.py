from __future__ import annotations

import struct
import tempfile
import time
from abc import ABC, abstractmethod
from contextlib import AsyncExitStack
from functools import partial
from inspect import isawaitable
from logging import Logger, getLogger
from pathlib import Path
from typing import AsyncIterator, Awaitable, Callable, Literal, cast

import anyio
from anyio import TASK_STATUS_IGNORED, Event, Lock, create_task_group
from anyio.abc import TaskGroup, TaskStatus
from pycrdt import Decoder, Doc, write_var_uint
from sqlite_anyio import Connection, connect, exception_logger

from .yutils import get_new_path


class YDocNotFound(Exception):
    pass


class BaseYStore(ABC):
    metadata_callback: Callable[[], Awaitable[bytes] | bytes] | None = None
    version = 2
    _started: Event | None = None
    _stopped: Event | None = None
    _task_group: TaskGroup | None = None
    _public_start_lock: Lock | None = None
    _private_start_lock: Lock | None = None

    @abstractmethod
    def __init__(
        self,
        path: str,
        metadata_callback: Callable[[], Awaitable[bytes] | bytes] | None = None,
        log: Logger | None = None,
    ): ...

    @abstractmethod
    async def write(self, data: bytes) -> None: ...

    @abstractmethod
    async def read(self) -> AsyncIterator[tuple[bytes, bytes, float]]:
        if False:
            yield

    @property
    def started(self) -> Event:
        if self._started is None:
            self._started = Event()
        return self._started

    @property
    def stopped(self) -> Event:
        if self._stopped is None:
            self._stopped = Event()
        return self._stopped

    @property
    def start_lock(self) -> Lock:
        if self._public_start_lock is None:
            self._public_start_lock = Lock()
        return self._public_start_lock

    @property
    def _start_lock(self) -> Lock:
        if self._private_start_lock is None:
            self._private_start_lock = Lock()
        return self._private_start_lock

    async def __aenter__(self) -> BaseYStore:
        async with self._start_lock:
            if self._task_group is not None:
                raise RuntimeError("YStore already running")

            async with AsyncExitStack() as exit_stack:
                tg = create_task_group()
                self._task_group = await exit_stack.enter_async_context(tg)
                self._exit_stack = exit_stack.pop_all()
                await tg.start(partial(self.start, from_context_manager=True))

        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self.stop()
        return await self._exit_stack.__aexit__(exc_type, exc_value, exc_tb)

    async def start(
        self,
        *,
        task_status: TaskStatus[None] = TASK_STATUS_IGNORED,
        from_context_manager: bool = False,
    ):
        """Start the store.

        Arguments:
            task_status: The status to set when the task has started.
        """
        if from_context_manager:
            task_status.started()
            self.started.set()
            return

        async with self._start_lock:
            if self._task_group is not None:
                raise RuntimeError("YStore already running")

            async with create_task_group() as self._task_group:
                task_status.started()
                self.started.set()
                await self.stopped.wait()

    async def stop(self) -> None:
        """Stop the store."""
        if self._task_group is None:
            raise RuntimeError("YStore not running")

        self.stopped.set()
        self._task_group.cancel_scope.cancel()
        self._task_group = None

    async def get_metadata(self) -> bytes:
        """
        Returns:
            The metadata.
        """
        if self.metadata_callback is None:
            return b""

        metadata = self.metadata_callback()
        if isawaitable(metadata):
            metadata = await metadata
        metadata = cast(bytes, metadata)
        return metadata

    async def encode_state_as_update(self, ydoc: Doc) -> None:
        """Store a YDoc state.

        Arguments:
            ydoc: The YDoc from which to store the state.
        """
        update = ydoc.get_update()
        await self.write(update)

    async def apply_updates(self, ydoc: Doc) -> None:
        """Apply all stored updates to the YDoc.

        Arguments:
            ydoc: The YDoc on which to apply the updates.
        """
        async for update, *rest in self.read():
            ydoc.apply_update(update)


class FileYStore(BaseYStore):
    """A YStore which uses one file per document."""

    path: str
    metadata_callback: Callable[[], Awaitable[bytes] | bytes] | None
    lock: Lock

    def __init__(
        self,
        path: str,
        metadata_callback: Callable[[], Awaitable[bytes] | bytes] | None = None,
        log: Logger | None = None,
    ) -> None:
        """Initialize the object.

        Arguments:
            path: The file path used to store the updates.
            metadata_callback: An optional callback to call to get the metadata.
            log: An optional logger.
        """
        self.path = path
        self.metadata_callback = metadata_callback
        self.log = log or getLogger(__name__)
        self.lock = Lock()

    async def check_version(self) -> int:
        """Check the version of the store format.

        Returns:
            The offset where the data is located in the file.
        """
        if not await anyio.Path(self.path).exists():
            version_mismatch = True
        else:
            version_mismatch = False
            move_file = False
            async with await anyio.open_file(self.path, "rb") as f:
                header = await f.read(8)
                if header == b"VERSION:":
                    version = int(await f.readline())
                    if version == self.version:
                        offset = await f.tell()
                    else:
                        version_mismatch = True
                else:
                    version_mismatch = True
                if version_mismatch:
                    move_file = True
            if move_file:
                new_path = await get_new_path(self.path)
                self.log.warning("YStore version mismatch, moving %s to %s", self.path, new_path)
                await anyio.Path(self.path).rename(new_path)
        if version_mismatch:
            async with await anyio.open_file(self.path, "wb") as f:
                version_bytes = f"VERSION:{self.version}\n".encode()
                await f.write(version_bytes)
                offset = len(version_bytes)
        return offset

    async def read(self) -> AsyncIterator[tuple[bytes, bytes, float]]:
        """Async iterator for reading the store content.

        Returns:
            A tuple of (update, metadata, timestamp) for each update.
        """
        async with self.lock:
            if not await anyio.Path(self.path).exists():
                raise YDocNotFound
            offset = await self.check_version()
            async with await anyio.open_file(self.path, "rb") as f:
                await f.seek(offset)
                data = await f.read()
                if not data:
                    raise YDocNotFound
        i = 0
        for d in Decoder(data).read_messages():
            if i == 0:
                update = d
            elif i == 1:
                metadata = d
            else:
                timestamp = struct.unpack("<d", d)[0]
                yield update, metadata, timestamp
            i = (i + 1) % 3

    async def write(self, data: bytes) -> None:
        """Store an update.

        Arguments:
            data: The update to store.
        """
        parent = Path(self.path).parent
        async with self.lock:
            await anyio.Path(parent).mkdir(parents=True, exist_ok=True)
            await self.check_version()
            async with await anyio.open_file(self.path, "ab") as f:
                data_len = write_var_uint(len(data))
                await f.write(data_len + data)
                metadata = await self.get_metadata()
                metadata_len = write_var_uint(len(metadata))
                await f.write(metadata_len + metadata)
                timestamp = struct.pack("<d", time.time())
                timestamp_len = write_var_uint(len(timestamp))
                await f.write(timestamp_len + timestamp)


class TempFileYStore(FileYStore):
    """A YStore which uses the system's temporary directory.
    Files are writen under a common directory.
    To prefix the directory name (e.g. /tmp/my_prefix_b4whmm7y/):

    ```py
    class PrefixTempFileYStore(TempFileYStore):
        prefix_dir = "my_prefix_"
    ```
    """

    prefix_dir: str | None = None
    base_dir: str | None = None

    def __init__(
        self,
        path: str,
        metadata_callback: Callable[[], Awaitable[bytes] | bytes] | None = None,
        log: Logger | None = None,
    ):
        """Initialize the object.

        Arguments:
            path: The file path used to store the updates.
            metadata_callback: An optional callback to call to get the metadata.
            log: An optional logger.
        """
        full_path = str(Path(self.get_base_dir()) / path)
        super().__init__(full_path, metadata_callback=metadata_callback, log=log)

    def get_base_dir(self) -> str:
        """Get the base directory where the update file is written.

        Returns:
            The base directory path.
        """
        if self.base_dir is None:
            self.make_directory()
        assert self.base_dir is not None
        return self.base_dir

    def make_directory(self):
        """Create the base directory where the update file is written."""
        type(self).base_dir = tempfile.mkdtemp(prefix=self.prefix_dir)


class SQLiteYStore(BaseYStore):
    """A YStore which uses an SQLite database.
    Unlike file-based YStores, the Y updates of all documents are stored in the same database.

    Subclass to point to your database file:

    ```py
    class MySQLiteYStore(SQLiteYStore):
        db_path = "path/to/my_ystore.db"
    ```
    """

    db_path: str = "ystore.db"
    # Determines the "time to live" for all documents, i.e. how recent the
    # latest update of a document must be before purging document history.
    # Defaults to never purging document history (None).
    document_ttl: int | None = None
    # The maximum length of the history of the documents in seconds that is kept.
    history_length: int | None = None
    # The minimum interval in seconds between history cleanup operations.
    min_cleanup_interval: int = 60
    path: str
    lock: Lock
    db_initialized: Event | None
    _db: Connection

    def __init__(
        self,
        path: str,
        metadata_callback: Callable[[], Awaitable[bytes] | bytes] | None = None,
        log: Logger | None = None,
    ) -> None:
        """Initialize the object.

        Arguments:
            path: The file path used to store the updates.
            metadata_callback: An optional callback to call to get the metadata.
            log: An optional logger.
        """
        self.path = path
        self.metadata_callback = metadata_callback
        self.log = log or getLogger(__name__)
        self.lock = Lock()
        self.db_initialized = None

    async def start(
        self,
        *,
        task_status: TaskStatus[None] = TASK_STATUS_IGNORED,
        from_context_manager: bool = False,
    ):
        """Start the SQLiteYStore.

        Arguments:
            task_status: The status to set when the task has started.
        """
        self.db_initialized = Event()
        if from_context_manager:
            assert self._task_group is not None
            self._task_group.start_soon(self._init_db)
            task_status.started()
            self.started.set()
            return

        async with self._start_lock:
            if self._task_group is not None:
                raise RuntimeError("YStore already running")
            async with create_task_group() as self._task_group:
                self._task_group.start_soon(self._init_db)
                task_status.started()
                self.started.set()
                await self.stopped.wait()

    async def stop(self) -> None:
        """Stop the store."""
        if self.db_initialized is not None and self.db_initialized.is_set():
            await self._db.close()
        await super().stop()

    async def _init_db(self):
        create_db = False
        move_db = False
        if not await anyio.Path(self.db_path).exists():
            create_db = True
        else:
            async with self.lock:
                db = await connect(
                    self.db_path,
                    exception_handler=exception_logger,
                    log=self.log,
                )
                async with db:
                    cursor = await db.cursor()
                    await cursor.execute(
                        "SELECT count(name) FROM sqlite_master "
                        "WHERE type='table' and name='yupdates'"
                    )
                    table_exists = (await cursor.fetchone())[0]
                    if table_exists:
                        await cursor.execute("pragma user_version")
                        version = (await cursor.fetchone())[0]
                        if version != self.version:
                            move_db = True
                            create_db = True
                    else:
                        create_db = True
                await db.close()
        if move_db:
            new_path = await get_new_path(self.db_path)
            self.log.warning("YStore version mismatch, moving %s to %s", self.db_path, new_path)
            await anyio.Path(self.db_path).rename(new_path)
        if create_db:
            async with self.lock:
                db = await connect(
                    self.db_path,
                    exception_handler=exception_logger,
                    log=self.log,
                )
                async with db:
                    cursor = await db.cursor()
                    await cursor.execute(
                        "CREATE TABLE yupdates (path TEXT NOT NULL, yupdate BLOB, "
                        "metadata BLOB, timestamp REAL NOT NULL)"
                    )
                    await cursor.execute(
                        "CREATE INDEX idx_yupdates_path_timestamp ON yupdates (path, timestamp)"
                    )
                    await cursor.execute(f"PRAGMA user_version = {self.version}")
                await db.close()
        self._db = await connect(
            self.db_path,
            exception_handler=exception_logger,
            log=self.log,
        )
        assert self.db_initialized is not None
        self.db_initialized.set()

    async def read(self) -> AsyncIterator[tuple[bytes, bytes, float]]:
        """Async iterator for reading the store content.

        Returns:
            A tuple of (update, metadata, timestamp) for each update.
        """
        if self.db_initialized is None:
            raise RuntimeError("YStore not started")
        await self.db_initialized.wait()
        try:
            async with self.lock:
                found = False
                async with self._db:
                    cursor = await self._db.cursor()
                    await cursor.execute(
                        "SELECT yupdate, metadata, timestamp FROM yupdates WHERE path = ?",
                        (self.path,),
                    )
                    for update, metadata, timestamp in await cursor.fetchall():
                        found = True
                        yield update, metadata, timestamp
                if not found:
                    raise YDocNotFound
        except Exception:
            raise YDocNotFound

    async def write(self, data: bytes) -> None:
        """Store an update.

        Arguments:
            data: The update to store.
        """
        if self.db_initialized is None:
            raise RuntimeError("YStore not started")
        await self.db_initialized.wait()
        async with self.lock:
            async with self._db:
                # first, determine time elapsed since last update
                cursor = await self._db.cursor()

                newest_diff = await self._get_time_differential_to_entry(cursor, direction="DESC")
                oldest_diff = await self._get_time_differential_to_entry(cursor, direction="ASC")

                squashed = False
                if (self.document_ttl is not None and newest_diff > self.document_ttl) or (
                    self.history_length is not None
                    and oldest_diff > self.min_cleanup_interval + self.history_length
                ):

                newest_diff = await self._get_time_differential_to_entry(cursor, direction="DESC")
                oldest_diff = await self._get_time_differential_to_entry(cursor, direction="ASC")

                squashed = False
                if (self.document_ttl is not None and newest_diff > self.document_ttl) or (
                    self.history_length is not None
                    and oldest_diff > self.min_cleanup_interval + self.history_length
                ):
                    # squash updates
                    ydoc: Doc = Doc()

                    older_than = time.time() - (
                        self.history_length if self.history_length is not None else 0
                    )
                    older_than = time.time() - (
                        self.history_length if self.history_length is not None else 0
                    )
                    await cursor.execute(
                        "SELECT yupdate FROM yupdates WHERE path = ? AND timestamp < ? AND timestamp < ?",
                        (self.path, older_than older_than),
                    )
                    for (update,) in await cursor.fetchall():
                        ydoc.apply_update(update)
                    # delete older history
                    await cursor.execute(
                        "DELETE FROM yupdates WHERE path = ? AND timestamp < ?",
                        (self.path, older_than),
                    )
                    # delete older history
                    await cursor.execute(
                        "DELETE FROM yupdates WHERE path = ? AND timestamp < ?",
                        (self.path, older_than),
                    )
                    # insert squashed updates
                    squashed_update = ydoc.get_update()
                    metadata = await self.get_metadata()
                    await cursor.execute(
                        "INSERT INTO yupdates VALUES (?, ?, ?, ?)",
                        (self.path, squashed_update, metadata, time.time()),
                    )
                    squashed = True
                    squashed = True

                # finally, write this update to the DB
                metadata = await self.get_metadata()
                await cursor.execute(
                    "INSERT INTO yupdates VALUES (?, ?, ?, ?)",
                    (self.path, data, metadata, time.time()),
                )

                if squashed:
                    # Vacuuming database
                    await self._db.commit()
                    await cursor.execute("VACUUM")

    async def _get_time_differential_to_entry(
        self, cursor, direction: Literal["ASC", "DESC"] = "DESC"
    ) -> float:
        """Get the time differential to the newest (DESC) or oldest (ASC) entry in the database."""
        await cursor.execute(
            "SELECT timestamp FROM yupdates WHERE path = ? "
            f"ORDER BY timestamp {direction} LIMIT 1",
            (self.path,),
        )
        row = await cursor.fetchone()
        return (time.time() - row[0]) if row else 0

                if squashed:
                    # Vacuuming database
                    await self._db.commit()
                    await cursor.execute("VACUUM")

    async def _get_time_differential_to_entry(
        self, cursor, direction: Literal["ASC", "DESC"] = "DESC"
    ) -> float:
        """Get the time differential to the newest (DESC) or oldest (ASC) entry in the database."""
        await cursor.execute(
            "SELECT timestamp FROM yupdates WHERE path = ? "
            f"ORDER BY timestamp {direction} LIMIT 1",
            (self.path,),
        )
        row = await cursor.fetchone()
        return (time.time() - row[0]) if row else 0
