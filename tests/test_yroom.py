import pytest
from anyio import TASK_STATUS_IGNORED, create_task_group, sleep
from anyio.abc import TaskStatus
from utils import Websocket, connected_websockets

from pycrdt import Doc, Map, Provider
from pycrdt.websocket import exception_logger
from pycrdt.websocket.yroom import YRoom

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize("websocket_provider_connect", ["fake_websocket"], indirect=True)
@pytest.mark.parametrize("yws_providers", [2], indirect=True)
async def test_yroom(yroom, yws_providers, websocket_provider_connect, room_name):
    async with create_task_group() as tg:
        yws_provider1, yws_provider2 = yws_providers
        # client 1
        async with yws_provider1 as yws_provider1:
            ydoc1, server_ws1 = yws_provider1
            tg.start_soon(yroom.serve, Websocket(server_ws1, room_name))
            ydoc1["map"] = ymap1 = Map()
            ymap1["key"] = "value"
            await sleep(0.1)

        # client 2
        async with yws_provider2 as yws_provider2:
            ydoc2, server_ws2 = yws_provider2
            tg.start_soon(yroom.serve, Websocket(server_ws2, room_name))
            ymap2 = ydoc2.get("map", type=Map)
            await sleep(0.1)

        assert str(ymap2) == '{"key":"value"}'
        tg.cancel_scope.cancel()


async def test_broadcast_not_sent_before_sync_completes(room_name):
    """Regression test: a client must not receive broadcast updates before the
    initial sync handshake finishes.

    When a new client connects, YRoom.serve() previously added it to
    self.clients immediately — before sending SYNC_STEP2. If the server-side
    document was mutated concurrently (e.g. by an MCP tool call adding cells),
    _broadcast_updates would send a SYNC_UPDATE to the un-synced client.
    The client's yjs would then throw "Unexpected case" in findIndexSS
    because the update referenced a struct the client didn't have yet.

    This test reproduces the race by:
    1. Creating a YRoom with existing data
    2. Connecting a new client
    3. Mutating the server-side doc before the client finishes syncing
    4. Asserting the client receives all data without errors
    """
    room = YRoom()
    async with room:
        # Pre-populate the room's document with data (simulates an existing notebook).
        room.ydoc["map"] = server_map = Map()
        server_map["existing"] = "data"

        # Set up a fake WebSocket pair for the new client.
        server_ws, client_ws = connected_websockets()
        ws = Websocket(server_ws, room_name)

        # Client document that will sync with the room.
        client_doc = Doc()

        async with create_task_group() as tg:
            # Start serving the new client (this begins the sync handshake).
            tg.start_soon(room.serve, ws)

            # Simulate rapid server-side mutations DURING the handshake.
            # In production this is caused by MCP add_cell calls from the AI agent.
            for i in range(20):
                server_map[f"cell_{i}"] = f"content_{i}"

            # Give the sync some time to propagate.
            await sleep(0.5)

            # Connect a Provider on the client side to process the sync messages.
            client_ws_wrapper = Websocket(client_ws, room_name)
            async with Provider(client_doc, client_ws_wrapper):
                await sleep(0.5)

            # Verify the client received all data — if the race exists,
            # the client would have crashed on "Unexpected case" and the
            # map would be incomplete or empty.
            client_map = client_doc.get("map", type=Map)
            assert client_map["existing"] == "data"
            for i in range(20):
                assert client_map[f"cell_{i}"] == f"content_{i}", (
                    f"Client missing cell_{i} — broadcast likely sent before sync completed"
                )

            tg.cancel_scope.cancel()


@pytest.mark.parametrize("websocket_server_api", ["websocket_server_start_stop"], indirect=True)
@pytest.mark.parametrize("yws_server", [{"exception_handler": exception_logger}], indirect=True)
async def test_yroom_restart(yws_server, yws_provider):
    port, server = yws_server
    yroom = YRoom(exception_handler=exception_logger)

    async def raise_error(task_status: TaskStatus[None] = TASK_STATUS_IGNORED):
        task_status.started()
        raise RuntimeError("foo")

    yroom.ydoc, _ = yws_provider
    await server.start_room(yroom)
    yroom.ydoc["map"] = ymap1 = Map()
    ymap1["key"] = "value"
    task_group_1 = yroom._task_group
    await yroom._task_group.start(raise_error)
    ymap1["key2"] = "value2"
    await sleep(0.1)
    assert yroom._task_group is not task_group_1
    assert yroom._task_group is not None
    assert not yroom._task_group.cancel_scope.cancel_called
    await yroom.stop()
