import importlib.metadata

from .asgi_server import ASGIServer as ASGIServer
from .websocket_server import WebsocketServer as WebsocketServer
from .websocket_server import exception_logger as exception_logger
from .yroom import YRoom as YRoom

try:
    __version__ = importlib.metadata.version("pycrdt.websocket")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"
