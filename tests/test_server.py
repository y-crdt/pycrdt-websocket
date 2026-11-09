import pytest
from anyio import (
    CancelScope,
    Event,
    create_task_group,
    fail_after,
    move_on_after,
    sleep,
    sleep_forever,
)
from utils import create_yws_provider, create_yws_server, get_unused_tcp_port

from pycrdt import Doc, Text, create_sync_message
from pycrdt.websocket import WebsocketServer, YRoom, exception_logger

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize("websocket_server_api", ["websocket_server_start_stop"], indirect=True)
@pytest.mark.parametrize("yws_server", [{"exception_handler": exception_logger}], indirect=True)
async def test_server_restart(yws_server):
    port, server = yws_server

    async def raise_error():
        raise RuntimeError("foo")

    server._task_group.start_soon(raise_error)
    await sleep(0.1)


async def test_server_provider():
    # the server that synchronizes the parallel servers
    sync_port = get_unused_tcp_port()
    sync_server = create_yws_server(sync_port)

    # the provider factory that synchronizes each parallel server with
    # the sync_server
    def provider_factory(path, doc, log):
        return create_yws_provider(sync_port, path, ydoc=doc, log=log)

    # the parallel servers
    port1 = get_unused_tcp_port()
    server1 = create_yws_server(port1, provider_factory=provider_factory)
    port2 = get_unused_tcp_port()
    server2 = create_yws_server(port2, provider_factory=provider_factory)

    # the clients connecting to the parallel servers
    client1 = create_yws_provider(port1, "myroom")
    client2 = create_yws_provider(port2, "myroom")

    async with (
        sync_server as sync_server,
        server1 as server1,
        server2 as server2,
        client1 as client1,
        client2 as client2,
    ):
        doc1, _ = client1
        doc2, _ = client2
        text1 = doc1.get("text", type=Text)
        text2 = doc2.get("text", type=Text)
        text1 += "Hello"
        with fail_after(1):
            async with text2.events() as events:
                async for event in events:
                    break

    assert str(text2) == "Hello"


async def test_stop_waits_for_start_to_return():
    # A task that is slow to unwind, so that the moment `stop()` returns is
    # observably distinct from the moment `start()` returns.
    async def slow_to_cancel():
        try:
            await sleep_forever()
        finally:
            with CancelScope(shield=True):
                await sleep(0.1)

    server = WebsocketServer()
    start_returned = Event()

    async def run_server():
        await server.start()
        start_returned.set()

    async with create_task_group() as tg:
        tg.start_soon(run_server)
        await server.started.wait()
        server._task_group.start_soon(slow_to_cancel)
        await sleep(0.1)
        await server.stop()
        assert start_returned.is_set()


async def test_stop_can_be_bounded_by_the_caller():
    # A task that cannot be cancelled, so that `stop()` has something to wait for.
    # The caller must be able to give up on it rather than block forever.
    async def never_cancels():
        with CancelScope(shield=True):
            await sleep(0.5)

    server = WebsocketServer()

    async with create_task_group() as tg:
        tg.start_soon(server.start)
        await server.started.wait()
        server._task_group.start_soon(never_cancels)
        await sleep(0.1)
        with fail_after(0.3):
            with move_on_after(0.1):
                await server.stop()


async def test_concurrent_get_room_starts_room_once():
    async with WebsocketServer() as server:
        rooms = []

        async def get_room():
            rooms.append(await server.get_room("/room"))

        with fail_after(1):
            async with create_task_group() as tg:
                tg.start_soon(get_room)
                tg.start_soon(get_room)

        assert len(rooms) == 2
        assert rooms[0] is rooms[1]


async def test_room_startup_does_not_block_other_rooms():
    startup_entered = Event()
    allow_startup = Event()

    class SlowRoom(YRoom):
        async def start(self, *, task_status):
            startup_entered.set()
            await allow_startup.wait()
            await super().start(task_status=task_status)

    with fail_after(1):
        async with WebsocketServer() as server:
            slow_room = SlowRoom()
            server.rooms["/slow"] = slow_room

            async with create_task_group() as tg:
                tg.start_soon(server.get_room, "/slow")
                await startup_entered.wait()

                other_room = await server.get_room("/other")
                assert other_room.started.is_set()
                assert not slow_room.started.is_set()

                allow_startup.set()


async def test_context_manager_stop_does_not_stall():
    # The context manager awaits the task group itself on exit, so `stop()` has
    # nothing to wait for and must not block on its way out.
    with fail_after(1):
        async with WebsocketServer():
            pass


class FakeChannel:
    def __init__(
        self,
        path: str,
        messages: list[bytes],
        send_error: Exception | None = None,
        receive_error: Exception | None = None,
    ) -> None:
        self.path = path
        self.messages = messages
        self.send_error = send_error
        self.receive_error = receive_error

    def __aiter__(self):
        return self

    async def __anext__(self) -> bytes:
        if self.messages:
            return self.messages.pop(0)
        if self.receive_error is not None:
            raise self.receive_error
        # the client disconnected
        raise StopAsyncIteration

    async def send(self, message: bytes) -> None:
        if self.send_error is not None:
            raise self.send_error


async def test_server_deletes_room_after_error():
    # ASGIWebsocket raises KeyError when the client sends a text frame
    channel = FakeChannel("/room", [], receive_error=KeyError("bytes"))
    async with WebsocketServer() as server:
        with pytest.raises(ExceptionGroup) as excinfo:
            await server.serve(channel)

        assert excinfo.group_contains(KeyError)
        assert server.rooms == {}


@pytest.mark.parametrize("fail_on_send", [1, 2], ids=["handshake", "sync_reply"])
async def test_server_client_send_error(fail_on_send):
    error = RuntimeError("foo")

    class FailingChannel(FakeChannel):
        sends = 0

        async def send(self, message: bytes) -> None:
            self.sends += 1
            if self.sends == fail_on_send:
                raise error

        async def __anext__(self) -> bytes:
            # A send failure need not be followed by a receive-side disconnect.
            if not self.messages:
                await sleep_forever()
            return self.messages.pop(0)

    channel = FailingChannel("/room", [create_sync_message(Doc())])
    async with WebsocketServer() as server:
        room = await server.get_room(channel.path)
        with fail_after(5):
            with pytest.raises(ExceptionGroup) as excinfo:
                await server.serve(channel)

        assert excinfo.group_contains(RuntimeError, match="foo")
        assert channel.sends == fail_on_send
        assert not room.clients
        assert server.rooms == {}
        assert room._task_group is None


class IdleChannel:
    """A client that stays connected until it leaves."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.served = Event()
        self.left = Event()

    def __aiter__(self):
        return self

    async def __anext__(self) -> bytes:
        await self.left.wait()
        # the client disconnected
        raise StopAsyncIteration

    async def send(self, message: bytes) -> None:
        # the room starts serving a client by sending it SYNC_STEP1
        self.served.set()

    async def wait_until_served(self) -> None:
        with fail_after(5):
            await self.served.wait()


async def test_client_joins_room_as_its_last_client_leaves():
    client1 = IdleChannel("/room")
    client2 = IdleChannel("/room")
    client3 = IdleChannel("/room")
    async with WebsocketServer() as server:
        async with create_task_group() as tg:
            tg.start_soon(server.serve, client1)
            await client1.wait_until_served()
            # client2 joins the room as client1, its only client, leaves it
            tg.start_soon(server.serve, client2)
            client1.left.set()
            await client2.wait_until_served()
            tg.start_soon(server.serve, client3)
            await client3.wait_until_served()

            # client2 isn't left alone in a deleted room, apart from the clients joining after it
            assert server.rooms["/room"].clients == {client2, client3}
            client2.left.set()
            client3.left.set()

        assert server.rooms == {}
