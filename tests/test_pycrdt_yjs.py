from __future__ import annotations

from functools import partial

import pytest
from anyio import Event, fail_after

from pycrdt import Array, Map

pytestmark = pytest.mark.anyio


class Change:
    def __init__(self, event, timeout, ydata, subscription, key):
        self.event = event
        self.timeout = timeout
        self.ydata = ydata
        self.subscription = subscription
        self.key = key

    async def wait(self):
        with fail_after(self.timeout):
            await self.event.wait()
        self.ydata.unobserve(self.subscription)
        if self.key is None:
            return
        return self.ydata[self.key]


def callback(change_event, key, event):
    if key is None or key in event.keys:
        change_event.set()


def watch(ydata, key: str | None = None, timeout: float = 1.0):
    change_event = Event()
    subscription = ydata.observe(partial(callback, change_event, key))
    return Change(change_event, timeout, ydata, subscription, key)


@pytest.mark.parametrize("yjs_client", [0], indirect=True)
async def test_pycrdt_yjs_0(yws_server, yws_provider, yjs_client):
    ydoc, _ = yws_provider
    ydoc["map"] = ymap = Map()
    for v_in in range(10):
        ymap["in"] = float(v_in)
        v_out = await watch(ymap, "out").wait()
        assert v_out == v_in + 1.0


@pytest.mark.parametrize("yjs_client", [1], indirect=True)
async def test_pycrdt_yjs_1(yws_server, yws_provider, yjs_client):
    ydoc, _ = yws_provider
    ydoc["cells"] = ycells = Array()
    ydoc["state"] = ystate = Map()
    ycells_change = watch(ycells)
    ystate_change = watch(ystate)
    await ycells_change.wait()
    await ystate_change.wait()
    assert ycells.to_py() == [{"metadata": {"foo": "bar"}, "source": "1 + 2"}]
    assert ystate.to_py() == {"state": {"dirty": False}}


@pytest.mark.parametrize("yjs_client", [2], indirect=True)
async def test_pycrdt_yjs_2(yws_server, yws_provider, yjs_client):
    ydoc, _ = yws_provider
    ydoc["map0"] = map0 = Map()
    map0_change = watch(map0)
    await map0_change.wait()
    assert map0.get("key0") == "val0"
    # client is synced, let's make a change
    map0["key1"] = "val1"
    # wait for client to undo the change
    map0_change = watch(map0)
    await map0_change.wait()
    assert "key1" not in map0
