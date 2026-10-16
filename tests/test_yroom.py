import gc
import platform
import sys
import weakref
from threading import Thread

import pytest
from anyio import TASK_STATUS_IGNORED, create_task_group, sleep
from anyio.abc import TaskStatus
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


@pytest.mark.skipif(
    platform.python_implementation() == "PyPy", reason="relies on reference counting"
)
async def test_yroom_garbage_collected_in_another_thread(monkeypatch):
    # see https://github.com/y-crdt/pycrdt-websocket/issues/146
    # collect other tests' garbage first, so that only this room's errors are recorded
    gc.collect()
    unraisable_exceptions = []
    monkeypatch.setattr(
        sys, "unraisablehook", lambda args: unraisable_exceptions.append(args.exc_value)
    )
    # keep the room from being collected in this thread
    gc.disable()
    try:
        yroom = YRoom()
        async with yroom:
            await sleep(0.1)
        yroom_ref = weakref.ref(yroom)
        del yroom
        # the stopped room can be freed by the garbage collector in any thread
        thread = Thread(target=gc.collect)
        thread.start()
        thread.join()
    finally:
        gc.enable()
    assert yroom_ref() is None
    assert unraisable_exceptions == []
