from __future__ import annotations

from collections.abc import Awaitable
from contextlib import AsyncExitStack
from functools import partial
from inspect import isawaitable
from logging import Logger, getLogger
from typing import Any, Callable, Protocol

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
    Awareness,
    Channel,
    Doc,
    Provider,
    Subscription,
    YMessageType,
    YSyncMessageType,
    create_awareness_message,
    create_sync_message,
    create_update_message,
    handle_sync_message,
    is_awareness_disconnect_message,
    read_message,
)
from pycrdt.store import BaseYStore

from .yutils import put_updates


class ProviderFactory(Protocol):
    def __call__(
        self,
        doc: Doc | None = None,
        log: Logger | None = None,
        path: str | None = None,
    ) -> Provider: ...


class YRoom:
    clients: set[Channel]
    ydoc: Doc
    ystore: BaseYStore | None
    ready_event: Event
    _on_message: Callable[[bytes], Awaitable[bool] | bool] | None
    _update_send_stream: MemoryObjectSendStream
    _update_receive_stream: MemoryObjectReceiveStream
    _task_group: TaskGroup | None = None
    _started: Event | None = None
    _stopped: Event
    __start_lock: Lock | None = None
    _subscription: Subscription | None = None

    def __init__(
        self,
        ready: bool = True,
        ystore: BaseYStore | None = None,
        exception_handler: Callable[[Exception, Logger], bool] | None = None,
        log: Logger | None = None,
        ydoc: Doc | None = None,
        provider_factory: ProviderFactory | None = None,
    ):
        """Initialize the object.

        The YRoom instance should preferably be used as an async context manager:
        ```py
        async with room:
            ...
        ```
        However, a lower-level API can also be used:
        ```py
        task = asyncio.create_task(room.start())
        await room.started.wait()
        ...
        await room.stop()
        ```

        Arguments:
            ready: Whether the internal YDoc is ready to be synchronized right away.
            ystore: An optional store in which to persist document updates.
            provider_factory: An optional provider factory used to synchronize the room with
                an external document.
            exception_handler: An optional callback to call when an exception is raised, that
                returns True if the exception was handled.
            log: An optional logger.
            ydoc: An optional document for the room (a new one is created otherwise).
        """
        self.ydoc = Doc() if ydoc is None else ydoc
        self.ready_event = Event()
        self.ready = ready
        self.ystore = ystore
        self.provider_factory = provider_factory
        self.log = log or getLogger(__name__)
        self.awareness = Awareness(self.ydoc)
        self.awareness.observe(self.send_server_awareness)
        self.clients = set()
        self._on_message = None
        self.exception_handler = exception_handler
        self._stopped = Event()
        self._provider_stop_event = Event()

    @property
    def _start_lock(self) -> Lock:
        if self.__start_lock is None:
            self.__start_lock = Lock()
        return self.__start_lock

    @property
    def started(self):
        """An async event that is set when the YRoom provider has started."""
        if self._started is None:
            self._started = Event()
        return self._started

    @property
    def ready(self) -> bool:
        """
        Returns:
            True is the internal YDoc is ready to be synchronized.
        """
        return self.ready_event.is_set()

    @ready.setter
    def ready(self, value: bool) -> None:
        """
        Arguments:
            value: True if the internal YDoc is ready to be synchronized, False otherwise."""
        if value and not self.ready_event.is_set():
            self.ready_event.set()

    async def _watch_ready(self):
        await self.ready_event.wait()
        self._subscription = self.ydoc.observe(partial(put_updates, self._update_send_stream))

    @property
    def on_message(self) -> Callable[[bytes], Awaitable[bool] | bool] | None:
        """
        Returns:
            The optional callback to call when a message is received.
        """
        return self._on_message

    @on_message.setter
    def on_message(self, value: Callable[[bytes], Awaitable[bool] | bool] | None):
        """
        Arguments:
            value: An optional callback to call when a message is received.
            If the callback returns True, the message is skipped.
        """
        self._on_message = value

    async def _broadcast_updates(self):
        if self.ystore is not None:
            async with self.ystore.start_lock:
                if not self.ystore.started.is_set():
                    await self._task_group.start(self.ystore.start)

        async with self._update_receive_stream:
            async for update in self._update_receive_stream:
                if self._task_group.cancel_scope.cancel_called:
                    return
                # broadcast internal ydoc's update to all clients, that includes changes from the
                # clients and changes from the backend (out-of-band changes)
                if self.clients:
                    message = create_update_message(update)
                    for client in self.clients:
                        try:
                            self.log.debug(
                                "Sending Y update to client with endpoint: %s", client.path
                            )
                            self._task_group.start_soon(client.send, message)
                        except Exception as exception:
                            self._handle_exception(exception)
                if self.ystore:
                    try:
                        self._task_group.start_soon(self.ystore.write, update)
                        self.log.debug("Writing Y update to YStore")
                    except Exception as exception:
                        self._handle_exception(exception)

    async def __aenter__(self) -> YRoom:
        async with self._start_lock:
            if self._task_group is not None:
                raise RuntimeError("YRoom already running")

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
        """Start the room.

        Arguments:
            task_status: The status to set when the task has started.
        """
        if from_context_manager:
            await self._start(task_status)
            return

        async with self._start_lock:
            if self._task_group is not None:
                raise RuntimeError("YRoom already running")

            while True:
                try:
                    async with create_task_group() as self._task_group:
                        await self._start(task_status)
                    return
                except Exception as exception:
                    await self.awareness.stop()
                    self._provider_stop_event.set()
                    self._provider_stop_event = Event()
                    self._handle_exception(exception)

    async def _start(
        self,
        task_status: TaskStatus[None],
    ):
        if not self.started.is_set():
            task_status.started()
            self.started.set()
        self._update_send_stream, self._update_receive_stream = create_memory_object_stream(
            max_buffer_size=65536
        )
        assert self._task_group is not None
        self._task_group.start_soon(self._stopped.wait)
        self._task_group.start_soon(self._watch_ready)
        self._task_group.start_soon(self._broadcast_updates)
        await self._task_group.start(self.awareness.start)
        self._task_group.start_soon(self._run_provider)

    async def _run_provider(self):
        if self.provider_factory is not None:
            provider_factory = self.provider_factory(doc=self.ydoc, log=self.log)
            try:
                async with provider_factory:
                    await self._provider_stop_event.wait()
            except Exception as exception:
                self._handle_exception(exception)

    async def stop(self) -> None:
        """Stop the room."""
        if self._task_group is None:
            raise RuntimeError("YRoom not running")
        self._stopped.set()
        await self.awareness.stop()
        self._task_group.cancel_scope.cancel()
        self._task_group = None
        if self._subscription is not None:
            self.ydoc.unobserve(self._subscription)

    async def serve(self, channel: Channel):
        """Serve a client.

        Arguments:
            channel: The WebSocket through which to serve the client.
        """
        try:
            async with create_task_group() as tg:
                self.clients.add(channel)
                sync_message = create_sync_message(self.ydoc)
                self.log.debug(
                    "Sending %s message to endpoint: %s",
                    YSyncMessageType.SYNC_STEP1.name,
                    channel.path,
                )
                await channel.send(sync_message)
                async for message in channel:
                    # filter messages (e.g. awareness)
                    skip = False
                    if self.on_message:
                        _skip = self.on_message(message)
                        skip = await _skip if isawaitable(_skip) else _skip
                    if skip:
                        continue
                    message_type = message[0]
                    if message_type == YMessageType.SYNC:
                        # update our internal state in the background
                        # changes to the internal state are then forwarded to all clients
                        # and stored in the YStore (if any)
                        self.log.debug(
                            "Received %s message from endpoint: %s",
                            YSyncMessageType(message[1]).name,
                            channel.path,
                        )
                        reply = handle_sync_message(message[1:], self.ydoc)
                        if reply is not None:
                            self.log.debug(
                                "Sending %s message to endpoint: %s",
                                YSyncMessageType.SYNC_STEP2.name,
                                channel.path,
                            )
                            tg.start_soon(channel.send, reply)
                    elif message_type == YMessageType.AWARENESS:
                        # forward awareness messages from this client to all clients,
                        # including itself, because it's used to keep the connection alive
                        self.log.debug(
                            "Received %s message from endpoint: %s",
                            YMessageType.AWARENESS.name,
                            channel.path,
                        )

                        # Check if the message is a client  awareness disconnect.
                        disconnection = is_awareness_disconnect_message(message[1:])

                        # Propagate the message to all clients except itself if it is a
                        # disconnection from the client. This avoid an error when trying
                        # to send the message to the disconnected client.
                        for client in self.clients:
                            if disconnection and client == channel:
                                continue

                            self.log.debug(
                                "Sending Y awareness from client with endpoint "
                                "%s to client with endpoint: %s",
                                channel.path,
                                client.path,
                            )
                            tg.start_soon(client.send, message)
                        # apply awareness update to the server's awareness
                        self.awareness.apply_awareness_update(read_message(message[1:]), self)
        except Exception as exception:
            self._handle_exception(exception)
        finally:
            # remove this client
            self.clients.remove(channel)

    def send_server_awareness(self, type: str, changes: tuple[dict[str, Any], Any]) -> None:
        """
        Callback to broadcast the server awareness to clients.

        Arguments:
            type: The change type.
            changes: The awareness changes.
        """
        if type != "update" or changes[1] != "local":
            return

        if self._task_group is not None:
            updated_clients = [v for value in changes[0].values() for v in value]
            state = self.awareness.encode_awareness_update(updated_clients)
            message = create_awareness_message(state)
            self._task_group.start_soon(self._send_server_awareness, message)
        else:
            self.log.error("Cannot broadcast server awareness: YRoom not started")

    async def _send_server_awareness(self, state: bytes) -> None:
        try:
            async with create_task_group() as tg:
                for client in self.clients:
                    self.log.debug(
                        "Sending awareness from server to client with endpoint: %s",
                        client.path,
                    )
                    tg.start_soon(client.send, state)
        except Exception as e:
            self.log.error("Error while broadcasting awareness changes: %s", e)
