from __future__ import annotations

from contextlib import AsyncExitStack
from functools import partial
from logging import Logger, getLogger
from typing import Callable

from anyio import TASK_STATUS_IGNORED, Event, Lock, create_task_group
from anyio.abc import TaskGroup, TaskStatus

from .websocket import Websocket
from .yroom import YRoom


class WebsocketServer:
    """WebSocket server."""

    auto_clean_rooms: bool
    rooms: dict[str, YRoom]
    _started: Event | None = None
    _stopped: Event
    _task_group: TaskGroup | None = None
    __start_lock: Lock | None = None

    def __init__(
        self,
        rooms_ready: bool = True,
        auto_clean_rooms: bool = True,
        exception_handler: Callable[[Exception, Logger], bool] | None = None,
        log: Logger | None = None,
    ) -> None:
        """Initialize the object.

        The WebsocketServer instance should preferably be used as an async context manager:
        ```py
        async with websocket_server:
            ...
        ```
        However, a lower-level API can also be used:
        ```py
        task = asyncio.create_task(websocket_server.start())
        await websocket_server.started.wait()
        ...
        await websocket_server.stop()
        ```

        Arguments:
            rooms_ready: Whether rooms are ready to be synchronized when opened.
            auto_clean_rooms: Whether rooms should be deleted when no client is there anymore.
            exception_handler: An optional callback to call when an exception is raised, that
                returns True if the exception was handled.
            log: An optional logger.
        """
        self.rooms_ready = rooms_ready
        self.auto_clean_rooms = auto_clean_rooms
        self.exception_handler = exception_handler
        self.log = log or getLogger(__name__)
        self.rooms = {}
        self._stopped = Event()

    @property
    def started(self) -> Event:
        """An async event that is set when the WebSocket server has started."""
        if self._started is None:
            self._started = Event()
        return self._started

    @property
    def _start_lock(self) -> Lock:
        if self.__start_lock is None:
            self.__start_lock = Lock()
        return self.__start_lock

    async def get_room(self, name: str) -> YRoom:
        """Get or create a room with the given name, and start it.

        Arguments:
            name: The room name.

        Returns:
            The room with the given name, or a new one if no room with that name was found.
        """
        if name not in self.rooms.keys():
            self.rooms[name] = YRoom(ready=self.rooms_ready, log=self.log)
        room = self.rooms[name]
        await self.start_room(room)
        return room

    async def start_room(self, room: YRoom) -> None:
        """Start a room, if not already started.

        Arguments:
            room: The room to start.
        """
        if self._task_group is None:
            raise RuntimeError(
                "The WebsocketServer is not running: use `async with websocket_server:` or "
                "`await websocket_server.start()`"
            )

        if not room.started.is_set():
            await self._task_group.start(room.start)

    def get_room_name(self, room: YRoom) -> str:
        """Get the name of a room.

        Arguments:
            room: The room to get the name from.

        Returns:
            The room name.
        """
        return list(self.rooms.keys())[list(self.rooms.values()).index(room)]

    def rename_room(
        self, to_name: str, *, from_name: str | None = None, from_room: YRoom | None = None
    ) -> None:
        """Rename a room.

        Arguments:
            to_name: The new name of the room.
            from_name: The previous name of the room (if `from_room` is not passed).
            from_room: The room to be renamed (if `from_name` is not passed).
        """
        if from_name is not None and from_room is not None:
            raise RuntimeError("Cannot pass from_name and from_room")
        if from_name is None:
            assert from_room is not None
            from_name = self.get_room_name(from_room)
        self.rooms[to_name] = self.rooms.pop(from_name)

    async def delete_room(self, *, name: str | None = None, room: YRoom | None = None) -> None:
        """Delete a room.

        Arguments:
            name: The name of the room to delete (if `room` is not passed).
            room: The room to delete (if `name` is not passed).
        """
        if name is not None and room is not None:
            raise RuntimeError("Cannot pass name and room")
        if name is None:
            assert room is not None
            name = self.get_room_name(room)
        room = self.rooms.pop(name)
        await room.stop()

    async def serve(self, websocket: Websocket) -> None:
        """Serve a client through a WebSocket.

        Arguments:
            websocket: The WebSocket through which to serve the client.
        """
        if self._task_group is None:
            raise RuntimeError(
                "The WebsocketServer is not running: use `async with websocket_server:` or "
                "`await websocket_server.start()`"
            )

        try:
            async with create_task_group():
                room = await self.get_room(websocket.path)
                await self.start_room(room)
                await room.serve(websocket)
                if self.auto_clean_rooms and not room.clients:
                    await self.delete_room(room=room)
        except Exception as exception:
            self._handle_exception(exception)

    async def __aenter__(self) -> WebsocketServer:
        async with self._start_lock:
            if self._task_group is not None:
                raise RuntimeError("WebsocketServer already running")

            async with AsyncExitStack() as exit_stack:
                self._task_group = await exit_stack.enter_async_context(create_task_group())
                self._exit_stack = exit_stack.pop_all()
                await self._task_group.start(partial(self.start, from_context_manager=True))

        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self.stop()
        return await self._exit_stack.__aexit__(exc_type, exc_value, exc_tb)

    def _handle_exception(self, exception: Exception) -> None:
        exception_handled = False
        if self.exception_handler is not None:
            exception_handled = self.exception_handler(exception, self.log)
        if not exception_handled:
            raise exception

    async def start(
        self,
        *,
        task_status: TaskStatus[None] = TASK_STATUS_IGNORED,
        from_context_manager: bool = False,
    ):
        """Start the WebSocket server.

        Arguments:
            task_status: The status to set when the task has started.
        """
        if from_context_manager:
            task_status.started()
            self.started.set()
            assert self._task_group is not None
            # wait until stopped
            self._task_group.start_soon(self._stopped.wait)
            return

        async with self._start_lock:
            if self._task_group is not None:
                raise RuntimeError("WebsocketServer already running")

            while True:
                try:
                    async with create_task_group() as self._task_group:
                        if not self.started.is_set():
                            task_status.started()
                            self.started.set()
                        # wait until stopped
                        self._task_group.start_soon(self._stopped.wait)
                    return
                except Exception as exception:
                    self._handle_exception(exception)

    async def stop(self) -> None:
        """Stop the WebSocket server."""
        if self._task_group is None:
            raise RuntimeError("WebsocketServer not running")

        self._stopped.set()
        self._task_group.cancel_scope.cancel()
        self._task_group = None


def exception_logger(exception: Exception, log: Logger) -> bool:
    """An exception handler that logs the exception and discards it."""
    log.error("WebsocketServer exception", exc_info=exception)
    return True  # the exception was handled
