from time import sleep

from utils.coding import bits_to_string, string_to_bits
from utils.constant import Network
from utils.io import get_device_map

from layer._abstract import AbstractLayer


class NetLayer(AbstractLayer):
    """主机网络层。"""

    def __init__(self, device_id: str) -> None:
        """
        初始化网络层。

        Args:
            device_id: 设备号。
        """
        config = get_device_map(device_id)
        super().__init__(config["net"])
        self._app = config["app"]
        self._phy = config["phy"]

    def __str__(self) -> str:
        """打印网络层信息。"""
        return f"<Net Layer @{self._port}>"

    @property
    def app(self) -> str:
        """将对应的应用层端口号设为只读。"""
        return self._app

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
        # 保证消息来自应用层。
        port = None
        while port != self._app:
            message, port, _ = self._receive(bufsize=Network.IN_NE_BUFSIZE)
        return message

    def send_to_phy(self, binary: str) -> int:
        """
        向物理层发送消息。

        Args:
            binary: 要发的消息。（01字符串）

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
