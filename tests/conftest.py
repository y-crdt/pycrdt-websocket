import subprocess
from functools import partial

import pytest
from utils import (
    StartStopContextManager,
    create_yws_provider,
    create_yws_server,
    get_unused_tcp_port,
)

from pycrdt.websocket import YRoom


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
    try:
        kwargs = request.param
    except AttributeError:
        kwargs = {}
    async with create_yws_server(unused_tcp_port, websocket_server_api, **kwargs) as server:
        yield server


@pytest.fixture
def yws_provider_factory(room_name, websocket_provider_api, websocket_provider_connect):
    return partial(
        create_yws_provider,
        pytest.port,
        room_name,
        websocket_provider_api,
        websocket_provider_connect,
    )


@pytest.fixture
async def yws_provider(yws_provider_factory):
    async with yws_provider_factory() as provider:
        ydoc, server_websocket = provider
        yield ydoc, server_websocket


@pytest.fixture
async def yws_providers(request, yws_provider_factory):
    number = request.param
    yield [yws_provider_factory() for _ in range(number)]


@pytest.fixture
async def yroom(request, yroom_api):
    try:
        kwargs = request.param
    except AttributeError:
        kwargs = {}
    room = YRoom(**kwargs)
    if yroom_api == "yroom_start_stop":
        room = StartStopContextManager(room)
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
    return get_unused_tcp_port()
