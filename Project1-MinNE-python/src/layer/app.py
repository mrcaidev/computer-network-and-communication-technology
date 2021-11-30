from utils.params import Network, Topology

from layer._abstract import AbstractLayer


class AppLayer(AbstractLayer):
    """主机应用层。

    实现了控制台-主机应用层、主机应用层-主机网络层的消息收发。
    """

    def __init__(self, device_id: str) -> None:
        """初始化主机应用层。

        Args:
            device_id: 该主机的设备号。
        """
        self.__device_id = device_id
        self.__port = f"1{device_id}300"
        self.__net = f"1{device_id}200"
        super().__init__(self.__port)

    def __str__(self) -> str:
        """打印设备号与端口号。"""
        return f"[Device {self.__device_id}] <App Layer @{self.__port}>\n{'-'*30}"

    def receive_all(self) -> tuple[str, bool]:
        """接收发到本层的消息。

        只对控制台与本机网络层开放。

        Returns:
            - [0] 接收到的消息。
            - [1] 控制台发来为`True`，本机网络层发来为`False`。
        """
        while True:
            message, port, _ = self._receive(bufsize=Network.IN_NE_BUFSIZE)
            if port == Topology.CMD_PORT:
                return message, True
            elif port == self.__net:
                return message, False
            else:
                continue

    def receive_from_cmd(self) -> str:
        """接收控制台发来的消息。

        Returns:
            接收到的消息。
        """
        port = ""
        while port != Topology.CMD_PORT:
            message, port, _ = self._receive(bufsize=Network.IN_NE_BUFSIZE)
        return message

    def receive_from_net(self) -> str:
        """接收本机网络层发来的消息。

        Returns:
            接收到的消息。
        """
        port = ""
        while port != self.__net:
            message, port, _ = self._receive(bufsize=Network.IN_NE_BUFSIZE)
        return message

    def send_to_net(self, message: str) -> int:
        """向主机网络层发送消息。

        Args:
            message: 要发的消息。

        Returns:
            总共发送的字节数。
        """
        return self._send(message, self.__net)
