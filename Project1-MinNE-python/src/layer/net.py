from time import sleep

from utils.coding import bits_to_string, string_to_bits
from utils.io import get_phynum
from utils.params import Network

from layer._abstract import AbstractLayer


class NetLayer(AbstractLayer):
    """主机网络层。

    实现了主机应用层-主机网络层、主机网络层-主机物理层的消息收发。
    """

    def __init__(self, device_id: str) -> None:
        """初始化主机网络层。

        Args:
            device_id: 该主机的设备号。
        """
        self.__device_id = device_id
        self.__app = f"1{device_id}300"
        self.__port = f"1{device_id}200"
        self.__phy = f"1{device_id}100"
        super().__init__(self.__port)

    def __str__(self) -> str:
        """打印设备号与端口号。"""
        return f"[Device {self.__device_id}] <Net Layer @{self.__port}>"

    @property
    def app(self) -> str:
        """将本机的应用层端口号设为只读。"""
        return self.__app

    def receive_from_app(self) -> str:
        """接收来自主机应用层的消息。

        Returns:
            接收到的消息。
        """
        port = ""
        while port != self.__app:
            message, port, _ = self._receive(bufsize=Network.IN_NE_BUFSIZE)
        return message

    def send_to_app(self, message: str) -> int:
        """向主机应用层发送消息。

        Args:
            message: 要发的消息。

        Returns:
            总共发送的字节数。
        """
        return self._send(message, self.__app)

    def receive_from_phy(self, timeout: int = Network.RECV_TIMEOUT) -> tuple[str, bool]:
        """接收来自主机物理层的消息。

        Args:
            timeout: 可选，接收超时时间，单位为秒，默认为`utils.params.Network.RECV_TIMEOUT`。

        Returns:
            - [0] 接收到的01字符串。
            - [1] 是否接收成功，成功为`True`，失败为`False`。
        """
        binary, _, success = self._receive(timeout=timeout)
        binary = bits_to_string(binary) if success else binary
        return binary, success

    def send_to_phy(self, binary: str) -> int:
        """向主机物理层发送消息。

        Args:
            binary: 要发的01字符串。

        Returns:
            总共发送的字节数。
        """
        # 流量控制。
        sleep(Network.FLOW_INTERVAL)
        return self._send(string_to_bits(binary), self.__phy)
