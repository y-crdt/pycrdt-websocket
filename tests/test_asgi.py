import pytest
from anyio import fail_after, sleep

from pycrdt import Map
from pycrdt.websocket import ASGIServer, WebsocketServer, YRoom

pytestmark = pytest.mark.anyio


async def test_asgi_deletes_room_after_text_frame():
    events = iter(
        [
            {"type": "websocket.connect"},
            # Uvicorn omits the bytes key for text frames, as permitted by ASGI.
            {"type": "websocket.receive", "text": "hello"},
        ]
    )
    sent: list[dict] = []
    rooms: list[YRoom] = []

    async def receive():
        return next(events)

    async def send(message):
        sent.append(message)
        if message["type"] == "websocket.send":
            rooms.append(server.rooms["/room"])

    async with WebsocketServer() as server:
        app = ASGIServer(server)
        with fail_after(5):
            with pytest.raises(ExceptionGroup) as excinfo:
                await app({"type": "websocket", "path": "/room"}, receive, send)

        assert excinfo.group_contains(KeyError, match="bytes")
        assert sent[0] == {"type": "websocket.accept"}
        assert len(rooms) == 1  # The room sent its initial binary sync message.
        assert not rooms[0].clients
        assert rooms[0]._task_group is None
        assert server.rooms == {}


@pytest.mark.parametrize("yws_server", [{"auto_clean_rooms": False}], indirect=True)
@pytest.mark.parametrize("yws_providers", [2], indirect=True)
async def test_asgi(yws_server, yws_providers):
    yws_provider1, yws_provider2 = yws_providers
    # client 1
    async with yws_provider1 as yws_provider1:
        ydoc1, _ = yws_provider1
        ydoc1["map"] = ymap1 = Map()
        ymap1["key"] = "value"
        await sleep(0.1)

    # client 2
    async with yws_provider2 as yws_provider2:
        ydoc2, _ = yws_provider2
        ymap2 = ydoc2.get("map", type=Map)
        await sleep(0.1)
        assert str(ymap2) == '{"key":"value"}'
