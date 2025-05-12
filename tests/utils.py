from __future__ import annotations

from anyio import Lock, connect_tcp, create_memory_object_stream

from pycrdt import Array, Doc


class YDocTest:
    def __init__(self):
        self.ydoc = Doc()
        self.ydoc["array"] = self.array = Array()
        self.state = None
        self.value = 0

    def update(self):
        self.array.append(self.value)
        self.value += 1
        update = self.ydoc.get_update(self.state)
        self.state = self.ydoc.get_state()
        return update


class StartStopContextManager:
    def __init__(self, service, task_group):
        self._service = service
        self._task_group = task_group

    async def __aenter__(self):
        await self._task_group.start(self._service.start)
        await self._service.started.wait()
        return self._service

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self._service.stop()


class Websocket:
    def __init__(self, websocket, path: str):
        self._websocket = websocket
        self._path = path
        self._send_lock = Lock()

    @property
    def path(self) -> str:
        return self._path

    def __aiter__(self):
        return self

    async def __anext__(self) -> bytes:
        try:
            message = await self.recv()
        except Exception:
            raise StopAsyncIteration()
        return message

    async def send(self, message: bytes):
        async with self._send_lock:
            await self._websocket.send_bytes(message)

    async def recv(self) -> bytes:
        b = await self._websocket.receive_bytes()
        return bytes(b)


class ClientWebsocket:
    def __init__(self, server_websocket: ServerWebsocket):
        self.server_websocket = server_websocket
        self.send_stream, self.receive_stream = create_memory_object_stream[bytes](65536)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        pass

    async def send_bytes(self, message: bytes) -> None:
        await self.server_websocket.send_stream.send(message)

    async def receive_bytes(self) -> bytes:
        return await self.receive_stream.receive()


class ServerWebsocket:
    client_websocket: ClientWebsocket | None = None

    def __init__(self):
        self.send_stream, self.receive_stream = create_memory_object_stream[bytes](65536)

    async def send_bytes(self, message: bytes) -> None:
        assert self.client_websocket is not None
        await self.client_websocket.send_stream.send(message)

    async def receive_bytes(self) -> bytes:
        return await self.receive_stream.receive()


def connected_websockets() -> tuple[ServerWebsocket, ClientWebsocket]:
    server_websocket = ServerWebsocket()
    client_websocket = ClientWebsocket(server_websocket)
    server_websocket.client_websocket = client_websocket
    return server_websocket, client_websocket


async def ensure_server_running(host: str, port: int) -> None:
    while True:
        try:
            await connect_tcp(host, port)
        except OSError:
            pass
        else:
            break
