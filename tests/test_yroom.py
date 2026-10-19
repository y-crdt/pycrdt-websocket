import pytest
from anyio import TASK_STATUS_IGNORED, create_task_group, sleep
from anyio.abc import TaskStatus
from anyio.lowlevel import checkpoint
from utils import Websocket

from pycrdt import Map
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


class FakeClient:
    def __init__(self, path: str, error: Exception | None = None) -> None:
        self.path = path
        self.error = error
        self.messages: list[bytes] = []

    async def send(self, message: bytes) -> None:
        if self.error is not None:
            raise self.error
        # Give failing sends an opportunity to interrupt this send.
        await checkpoint()
        self.messages.append(message)


async def test_yroom_server_awareness_send_error(yroom, caplog):
    client1 = FakeClient("client1", RuntimeError("foo"))
    client2 = FakeClient("client2", ValueError("bar"))
    client3 = FakeClient("client3")
    yroom.clients.update({client1, client2, client3})
    await yroom._send_server_awareness(b"awareness")

    records = [record for record in caplog.records if record.levelname == "ERROR"]
    assert len(records) == 2
    errors = {
        record.getMessage(): record.exc_info[1] if record.exc_info else None for record in records
    }
    message = "Error while broadcasting awareness changes to client with endpoint: {}"
    assert errors == {
        message.format("client1"): client1.error,
        message.format("client2"): client2.error,
    }
    # the other clients still get the awareness update
    assert client3.messages == [b"awareness"]
