import socket
from select import select
from time import sleep

from utils.param import Constant as const


class AbstractLayer:
    """各网元层的抽象父类。"""

    def __init__(self, port: str) -> None:
        """
        初始化本层。

        Args:
            port: 本层所在端口。
        """
        self._addr = ("127.0.0.1", int(port))
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(self._addr)
        self._socket.settimeout(const.USER_TIMEOUT)

    @property
    def socket(self) -> socket.socket:
        """将该层套接字本体设为只读。"""
        return self._socket


class AppLayer(AbstractLayer):
    """应用层。"""

    def __init__(self, port: str) -> None:
        """
        初始化应用层。

        Args:
            port: 应用层端口号。
        """
        super().__init__(port)
        self._socket.settimeout(const.USER_TIMEOUT)

    def bind_net(self, port: str) -> None:
        """
        绑定网络层地址。

        Args:
            port: 网络层端口号。
        """
        self._net = ("127.0.0.1", int(port))

    def send(self, message: str) -> int:
        """
        向网络层发送消息。

        Args:
            message: 要发的消息。

        Returns:
            总共发送的字节数。
        """
        return self._socket.sendto(bytes(message, encoding="utf-8"), self._net)

    def receive(self) -> str:
        """
        从网络层接收消息。

        Returns:
            接收到的消息。
        """
        message, _ = self._socket.recvfrom(const.MAX_BUFFER_SIZE)
        return str(message)[2:]


class NetLayer(AbstractLayer):
    """网络层。"""

    def __init__(self, port: str) -> None:
        """
        初始化网络层。

        Args:
            port: 网络层端口号。
        """
        super().__init__(port)
        self._socket.settimeout(const.USER_TIMEOUT)

    def bind_app(self, port: str) -> None:
        """
        绑定应用层地址。

        Args:
            port: 应用层端口号。
        """
        self._app = ("127.0.0.1", int(port))

    def bind_phy(self, port: str) -> None:
        """
        绑定物理层地址。

        Args:
            port: 物理层端口号。
        """
        self._phy = ("127.0.0.1", int(port))

    def send_to_app(self, message: str) -> int:
        """
        向应用层发送消息。

        Args:
            message: 要发的消息。

        Returns:
            总共发送的字节数。
        """
        return self._socket.sendto(bytes(message, encoding="utf-8"), self._app)

    def receive_from_app(self) -> str:
        """
        从应用层接收消息。

        Returns:
            接收到的消息。
        """
        message, _ = self._socket.recvfrom(const.MAX_BUFFER_SIZE)
        return str(message)[2:-1]

    def send_to_phy(self, binary: str) -> int:
        """
        向物理层发送消息。

        Args:
            message: 要发的消息（01序列）。

        Returns:
            总共发送的字节数。
        """
        binary = "".join(list(map(lambda char: chr(ord(char) - ord("0")), binary)))
        sleep(const.FLOW_INTERVAL)
        return self._socket.sendto(bytes(binary, encoding="utf-8"), self._phy)

    def receive_from_phy(self, timeout: int = const.RECV_TIMEOUT) -> tuple[str, bool]:
        """
        从应用层接收消息。

        Args:
            timeout: 接收超时时间，单位为秒，默认为`utils.param.Constant.RECV_TIMEOUT`。

        Returns:
            一个二元元组。
            - [0] 接收到的消息。
            - [1] 是否接收成功，成功为True，失败为False。
        """
        self._socket.settimeout(timeout)
        try:
            binary, _ = self._socket.recvfrom(const.MAX_BUFFER_SIZE)
        except socket.timeout:
            return "", False
        self._socket.settimeout(const.USER_TIMEOUT)
        binary = "".join(list(map(lambda bit: chr(bit + ord("0")), binary)))
        return str(binary), True


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
