import socket
from select import select

from utils.coding import decode, encode
from utils.param import Constant as const


class AbstractLayer:
    """各网元层的抽象父类。"""

    def __init__(self, port: int) -> None:
        """
        初始化本层。

        Args:
            port: 本层所在端口。
        """
        self._addr = ("127.0.0.1", port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(self._addr)
        self._socket.settimeout(const.USER_TIMEOUT)

    @property
    def socket(self) -> socket.socket:
        """将该层套接字本体设为只读。"""
        return self._socket


class AppLayer(AbstractLayer):
    """应用层。"""

    def __init__(self, port: int) -> None:
        """
        初始化应用层。

        Args:
            port: 应用层所在端口。
        """
        super().__init__(port)

    def bind_net(self, port: int) -> None:
        """
        绑定网络层地址。

        Args:
            port: 网络层端口号。
        """
        self._net = ("127.0.0.1", port)

    def send(self, message: str) -> int:
        """
        向网络层发送消息。

        Args:
            message: 要发的消息。

        Returns:
            总共发送的字节数。
        """
        return self._socket.sendto(bytes(encode(message), encoding="utf-8"), self._net)

    def receive(self, timeout: int = const.RECV_TIMEOUT) -> str:
        """
        从网络层接收消息。

        Args:
            timeout: 可选，接收的超时时间，默认为`utils.param.Constant.RECV_TIMEOUT`。

        Returns:
            解码后的消息。
        """
        self._socket.settimeout(timeout)
        secret, _ = self._socket.recvfrom(const.MAX_BUFFER_SIZE)
        self._socket.settimeout(const.USER_TIMEOUT)
        return decode(str(secret)[2:])


def select_readable(sockets: list[socket.socket]) -> list[socket.socket]:
    """
    从列表中挑选可读的套接字。

    Args:
        sockets: 要检验的套接字列表。

    Returns:
        当前可读的套接字列表。
    """
    ready_sockets, _, _ = select(sockets, [], [], const.SELECT_TIMEOUT)
    return ready_sockets
