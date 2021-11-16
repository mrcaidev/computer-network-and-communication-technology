import select
import socket

from utils.coding import decode, encode
from utils.param import Constant as const


class AbstractLayer:
    def __init__(self, port: int) -> None:
        self._addr = ("127.0.0.1", port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(self._addr)
        self._socket.settimeout(const.USER_TIMEOUT)

    @property
    def socket(self) -> socket.socket:
        return self._socket


class AppLayer(AbstractLayer):
    def __init__(self, port: int) -> None:
        super().__init__(port)

    def bind_net(self, port: int) -> None:
        self._net = ("127.0.0.1", port)

    def send(self, message: str) -> None:
        self._socket.sendto(bytes(encode(message), encoding="utf-8"), self._net)

    def receive(self, timeout: int = const.RECV_TIMEOUT) -> str:
        self._socket.settimeout(timeout)
        secret, _ = self._socket.recvfrom(const.MAX_BUFFER_SIZE)
        self._socket.settimeout(const.USER_TIMEOUT)
        return decode(str(secret)[2:])


def select_readable(sockets: list[socket.socket]) -> list[socket.socket]:
    ready_sockets, _, _ = select.select(sockets, [], [], const.SELECT_TIMEOUT)
    return ready_sockets
