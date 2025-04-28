import pytest
from anyio import sleep

from pycrdt import Map

pytestmark = pytest.mark.anyio


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
