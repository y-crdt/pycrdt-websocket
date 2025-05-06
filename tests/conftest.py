import subprocess
from contextlib import asynccontextmanager
from functools import partial
from socket import socket

import pytest
from anyio import Event, create_task_group
from httpx_ws import aconnect_ws
from hypercorn import Config
from sniffio import current_async_library
from utils import StartStopContextManager, Websocket, connected_websockets, ensure_server_running

from pycrdt import Doc
from pycrdt.websocket import ASGIServer, WebsocketProvider, WebsocketServer, YRoom


@pytest.fixture(params=("websocket_server_context_manager", "websocket_server_start_stop"))
def websocket_server_api(request):
    return request.param


@pytest.fixture(params=("websocket_provider_context_manager", "websocket_provider_start_stop"))
def websocket_provider_api(request):
    return request.param


@pytest.fixture(params=("yroom_context_manager", "yroom_start_stop"))
def yroom_api(request):
    return request.param


@pytest.fixture(params=("real_websocket",))
def websocket_provider_connect(request):
    return request.param


@pytest.fixture(params=("ystore_context_manager", "ystore_start_stop"))
def ystore_api(request):
    return request.param


@pytest.fixture
async def yws_server(request, unused_tcp_port, websocket_server_api):
    async with create_task_group() as tg:
        try:
            kwargs = request.param
        except AttributeError:
            kwargs = {}
        websocket_server = WebsocketServer(**kwargs)
        app = ASGIServer(websocket_server)
        config = Config()
        config.bind = [f"localhost:{unused_tcp_port}"]
        shutdown_event = Event()
        if websocket_server_api == "websocket_server_start_stop":
            websocket_server = StartStopContextManager(websocket_server, tg)
        if current_async_library() == "trio":
            from hypercorn.trio import serve
        else:
            from hypercorn.asyncio import serve
        async with websocket_server as websocket_server:
            tg.start_soon(
                partial(serve, app, config, shutdown_trigger=shutdown_event.wait, mode="asgi")
            )
            await ensure_server_running("localhost", unused_tcp_port)
            pytest.port = unused_tcp_port
            yield unused_tcp_port, websocket_server
            shutdown_event.set()


@pytest.fixture
def yws_provider_factory(room_name, websocket_provider_api, websocket_provider_connect):
    @asynccontextmanager
    async def factory():
        ydoc = Doc()
        if websocket_provider_connect == "real_websocket":
            server_websocket = None
            connect = aconnect_ws(f"http://localhost:{pytest.port}/{room_name}")
        else:
            server_websocket, connect = connected_websockets()
        async with connect as websocket:
            async with create_task_group() as tg:
                websocket_provider = WebsocketProvider(ydoc, Websocket(websocket, room_name))
                if websocket_provider_api == "websocket_provider_start_stop":
                    websocket_provider = StartStopContextManager(websocket_provider, tg)
                async with websocket_provider as websocket_provider:
                    yield ydoc, server_websocket

    return factory


@pytest.fixture
async def yws_provider(yws_provider_factory):
    async with yws_provider_factory() as provider:
        ydoc, server_websocket = provider
        yield ydoc, server_websocket


@pytest.fixture
async def yws_providers(request, yws_provider_factory):
    number = request.param
    yield [yws_provider_factory() for idx in range(number)]


@pytest.fixture
async def yroom(request, yroom_api):
    async with create_task_group() as tg:
        try:
            kwargs = request.param
        except AttributeError:
            kwargs = {}
        room = YRoom(**kwargs)
        if yroom_api == "yroom_start_stop":
            room = StartStopContextManager(room, tg)
        async with room as room:
            yield room


@pytest.fixture
def yjs_client(request):
    client_id = request.param
    p = subprocess.Popen(["node", f"tests/yjs_client_{client_id}.js", str(pytest.port)])
    yield p
    p.kill()


@pytest.fixture
def room_name():
    return "my-roomname"


@pytest.fixture
def unused_tcp_port() -> int:
    with socket() as sock:
        sock.bind(("localhost", 0))
        return sock.getsockname()[1]
