import pytest
from anyio import fail_after, sleep
from utils import create_yws_provider, create_yws_server, get_unused_tcp_port

from pycrdt import Text
from pycrdt.websocket import exception_logger

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
