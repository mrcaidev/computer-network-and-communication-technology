from time import sleep

from utils.coding import bits_to_string, string_to_bits
from utils.constant import Network

from layer._abstract import AbstractLayer


class NetLayer(AbstractLayer):
    """主机网络层。"""

    def __init__(self, port: str) -> None:
        """
        初始化网络层。

        Args:
            port: 网络层端口号。
        """
        super().__init__(port)
        self._app = "-1"
        self._phy = "-1"

    def __str__(self) -> str:
        """打印网络层信息。"""
        return f"<Net Layer at 127.0.0.1:{self._port} {{App:{self._app}, Phy:{self._phy}}}>"

    def bind_app(self, port: str) -> None:
        """
        绑定应用层地址。

        Args:
            port: 应用层端口号。
        """
        self._app = port

    def send_to_app(self, message: str) -> int:
        """
        向应用层发送消息。

        Args:
            message: 要发的消息。

        Returns:
            总共发送的字节数。
        """
        return self._send(message, self._app)

    def receive_from_app(self) -> str:
        """
        从应用层接收消息。

        Returns:
            接收到的消息。
        """
        port = "-1"
        while port != self._app:
            message, port, _ = self._receive(bufsize=Network.IN_NE_BUFSIZE)
        return message

    def bind_phy(self, port: str) -> None:
        """
        绑定物理层地址。

        Args:
            port: 物理层端口号。
        """
        self._phy = port

    def send_to_phy(self, binary: str) -> int:
        """
        向物理层发送消息。

        Args:
            binary: 要发的消息（01序列）。

        Returns:
            总共发送的字节数。
        """
        sleep(Network.FLOW_INTERVAL)
        return self._send(string_to_bits(binary), self._phy)

    def receive_from_phy(self, timeout: int = Network.RECV_TIMEOUT) -> tuple[str, bool]:
        """
        从物理层接收消息。

        Args:
            timeout: 接收超时时间，单位为秒，默认为`utils.constant.Network.RECV_TIMEOUT`。

        Returns:
            一个二元元组。
            - [0] 接收到的消息。
            - [1] 是否接收成功，成功为True，失败为False。
        """
        binary, _, success = self._receive(timeout=timeout)
        binary = bits_to_string(binary) if success else binary
        return binary, success
