from __future__ import annotations

from contextlib import AsyncExitStack
from functools import partial
from logging import Logger, getLogger

from anyio import (
    TASK_STATUS_IGNORED,
    Event,
    Lock,
    create_memory_object_stream,
    create_task_group,
)
from anyio.abc import TaskGroup, TaskStatus
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from pycrdt import (
    Doc,
    Subscription,
    YMessageType,
    YSyncMessageType,
    create_sync_message,
    create_update_message,
    handle_sync_message,
)

from .websocket import Websocket
from .yutils import put_updates


class WebsocketProvider:
    """WebSocket provider."""

    _ydoc: Doc
    _update_send_stream: MemoryObjectSendStream
    _update_receive_stream: MemoryObjectReceiveStream
    _subscription: Subscription
    _started: Event | None = None
    _task_group: TaskGroup | None = None
    __start_lock: Lock | None = None

    def __init__(self, ydoc: Doc, websocket: Websocket, log: Logger | None = None) -> None:
        """Initialize the object.

        The WebsocketProvider instance should preferably be used as an async context manager:
        ```py
        async with websocket_provider:
            ...
        ```
        However, a lower-level API can also be used:
        ```py
        task = asyncio.create_task(websocket_provider.start())
        await websocket_provider.started.wait()
        ...
        await websocket_provider.stop()
        ```

        Arguments:
            ydoc: The YDoc to connect through the WebSocket.
            websocket: The WebSocket through which to connect the YDoc.
            log: An optional logger.
        """
        self._ydoc = ydoc
        self._websocket = websocket
        self.log = log or getLogger(__name__)
        self._update_send_stream, self._update_receive_stream = create_memory_object_stream(
            max_buffer_size=65536
        )

    @property
    def started(self) -> Event:
        """An async event that is set when the WebSocket provider has started."""
        if self._started is None:
            self._started = Event()
        return self._started

    @property
    def _start_lock(self) -> Lock:
        if self.__start_lock is None:
            self.__start_lock = Lock()
        return self.__start_lock

    async def _run(self):
        sync_message = create_sync_message(self._ydoc)
        self.log.debug(
            "Sending %s message to endpoint: %s",
            YSyncMessageType.SYNC_STEP1.name,
            self._websocket.path,
        )
        await self._websocket.send(sync_message)
        self._task_group.start_soon(self._send)
        async for message in self._websocket:
            if message[0] == YMessageType.SYNC:
                self.log.debug(
                    "Received %s message from endpoint: %s",
                    YSyncMessageType(message[1]).name,
                    self._websocket.path,
                )
                reply = handle_sync_message(message[1:], self._ydoc)
                if reply is not None:
                    self.log.debug(
                        "Sending %s message to endpoint: %s",
                        YSyncMessageType.SYNC_STEP2.name,
                        self._websocket.path,
                    )
                    await self._websocket.send(reply)

    async def _send(self):
        async with self._update_receive_stream:
            async for update in self._update_receive_stream:
                message = create_update_message(update)
                try:
                    await self._websocket.send(message)
                except Exception:
                    pass

    async def __aenter__(self) -> WebsocketProvider:
        async with self._start_lock:
            if self._task_group is not None:
                raise RuntimeError("WebsocketProvider already running")

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
        """Start the WebSocket provider.

        Arguments:
            task_status: The status to set when the task has started.
        """
        self._subscription = self._ydoc.observe(partial(put_updates, self._update_send_stream))

        if from_context_manager:
            task_status.started()
            self.started.set()
            assert self._task_group is not None
            self._task_group.start_soon(self._run)
            return

        async with self._start_lock:
            if self._task_group is not None:
                raise RuntimeError("WebsocketProvider already running")

            async with create_task_group() as self._task_group:
                task_status.started()
                self.started.set()
                self._task_group.start_soon(self._run)

    async def stop(self):
        """Stop the WebSocket provider."""
        if self._task_group is None:
            raise RuntimeError("WebsocketProvider not running")

        self._task_group.cancel_scope.cancel()
        self._task_group = None
        self._ydoc.unobserve(self._subscription)
