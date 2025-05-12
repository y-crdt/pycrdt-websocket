from __future__ import annotations

from contextlib import AsyncExitStack, asynccontextmanager
from functools import partial
from socket import socket

import pytest
from anyio import (
    Event,
    Lock,
    connect_tcp,
    create_memory_object_stream,
    create_task_group,
    get_cancelled_exc_class,
)
from httpx_ws import aconnect_ws
from hypercorn import Config
from sniffio import current_async_library

from pycrdt import Array, Doc, Provider
from pycrdt.websocket import ASGIServer, WebsocketServer


class YDocTest:
    def __init__(self):
        self.ydoc = Doc()
        self.ydoc["array"] = self.array = Array()
        self.state = None
        self.value = 0

    def update(self):
        self.array.append(self.value)
        self.value += 1
        update = self.ydoc.get_update(self.state)
        self.state = self.ydoc.get_state()
        return update


class StartStopContextManager:
    def __init__(self, service):
        self._service = service

    async def __aenter__(self):
        async with AsyncExitStack() as exit_stack:
            self._task_group = await exit_stack.enter_async_context(create_task_group())
            await self._task_group.start(self._service.start)
            self._exit_stack = exit_stack.pop_all()
        await self._service.started.wait()
        return self._service

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        self._task_group.start_soon(self._service.stop)
        return await self._exit_stack.__aexit__(exc_type, exc_value, exc_tb)


class Websocket:
    def __init__(self, websocket, path: str):
        self._websocket = websocket
        self._path = path
        self._send_lock = Lock()

    @property
    def path(self) -> str:
        return self._path

    def __aiter__(self):
        return self

    async def __anext__(self) -> bytes:
        try:
            message = await self.recv()
        except Exception:
            raise StopAsyncIteration()
        return message

    async def send(self, message: bytes):
        async with self._send_lock:
            await self._websocket.send_bytes(message)

    async def recv(self) -> bytes:
        b = await self._websocket.receive_bytes()
        return bytes(b)


class ClientWebsocket:
    def __init__(self, server_websocket: ServerWebsocket):
        self.server_websocket = server_websocket
        self.send_stream, self.receive_stream = create_memory_object_stream[bytes](65536)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        pass

    async def send_bytes(self, message: bytes) -> None:
        await self.server_websocket.send_stream.send(message)

    async def receive_bytes(self) -> bytes:
        return await self.receive_stream.receive()


class ServerWebsocket:
    client_websocket: ClientWebsocket | None = None

    def __init__(self):
        self.send_stream, self.receive_stream = create_memory_object_stream[bytes](65536)

    async def send_bytes(self, message: bytes) -> None:
        assert self.client_websocket is not None
        await self.client_websocket.send_stream.send(message)

    async def receive_bytes(self) -> bytes:
        return await self.receive_stream.receive()


def connected_websockets() -> tuple[ServerWebsocket, ClientWebsocket]:
    server_websocket = ServerWebsocket()
    client_websocket = ClientWebsocket(server_websocket)
    server_websocket.client_websocket = client_websocket
    return server_websocket, client_websocket


async def ensure_server_running(host: str, port: int) -> None:
    while True:
        try:
            await connect_tcp(host, port)
        except OSError:
            pass
        else:
            break


@asynccontextmanager
async def create_yws_provider(
    port,
    room_name,
    websocket_provider_api="websocket_provider_context_manager",
    websocket_provider_connect="real_websocket",
    ydoc=None,
    log=None,
):
    ydoc = Doc() if ydoc is None else ydoc
    if websocket_provider_connect == "real_websocket":
        server_websocket = None
        connect = aconnect_ws(f"http://localhost:{port}/{room_name}")
    else:
        server_websocket, connect = connected_websockets()
    try:
        async with connect as websocket:
            websocket_provider = Provider(ydoc, Websocket(websocket, room_name), log)
            if websocket_provider_api == "websocket_provider_start_stop":
                websocket_provider = StartStopContextManager(websocket_provider)
            async with websocket_provider as websocket_provider:
                yield ydoc, server_websocket
    except get_cancelled_exc_class():
        pass


@asynccontextmanager
async def create_yws_server(
    port, websocket_server_api="websocket_server_context_manager", **kwargs
):
    async with create_task_group() as tg:
        websocket_server = WebsocketServer(**kwargs)
        app = ASGIServer(websocket_server)
        config = Config()
        config.bind = [f"localhost:{port}"]
        shutdown_event = Event()
        if websocket_server_api == "websocket_server_start_stop":
            websocket_server = StartStopContextManager(websocket_server)
        if current_async_library() == "trio":
            from hypercorn.trio import serve
        else:
            from hypercorn.asyncio import serve
        async with websocket_server as websocket_server:
            tg.start_soon(
                partial(serve, app, config, shutdown_trigger=shutdown_event.wait, mode="asgi")
            )
            await ensure_server_running("localhost", port)
            pytest.port = port
            yield port, websocket_server
            shutdown_event.set()


def get_unused_tcp_port():
    with socket() as sock:
        sock.bind(("localhost", 0))
        return sock.getsockname()[1]
