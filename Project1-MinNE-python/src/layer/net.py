from time import sleep

from utils.coding import *
from utils.frame import Frame
from utils.params import *

from layer._abstract import AbstractLayer


class NetLayer(AbstractLayer):
    """主机网络层。

    实现的消息收发：主机应用层<->主机网络层<->主机物理层。
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
        return f"[Device {self.__device_id}] <Net Layer @{self.__port}>\n{'-'*30}"

    def receive_all(self) -> tuple[str, bool]:
        """接收来自本机应用层与本机物理层的消息。

        Returns:
            - [0] 接收到的消息。
            - [1] 本机应用层发来为`True`，本机物理层发来为`False`。
        """
        while True:
            message, port, _ = self._receive(bufsize=Network.IN_NE_BUFSIZE)
            if port == self.__app:
                return message, True
            elif port == self.__phy:
                return bits_to_string(message), False
            else:
                continue

    def receive_from_app(self) -> str:
        """接收来自本机应用层的消息。

        Returns:
            接收到的消息。
        """
        port = ""
        while port != self.__app:
            message, port, _ = self._receive(bufsize=Network.IN_NE_BUFSIZE)
        return message

    def receive_from_phy(self, timeout: int = Network.RECV_TIMEOUT) -> tuple[str, bool]:
        """接收来自本机物理层的消息。

        Args:
            timeout: 可选，接收超时时间，单位为秒，默认为`RECV_TIMEOUT`。

        Returns:
            - [0] 接收到的消息。
            - [1] 接收成功为`True`，接收超时为`False`。
        """
        binary, _, success = self._receive(timeout=timeout)
        binary = bits_to_string(binary) if success else binary
        return binary, success

    def send_to_app(self, message: str) -> int:
        """向本机应用层发送消息。

        Args:
            message: 要发送的消息。

        Returns:
            总共发送的字节数。
        """
        return self._send(message, self.__app)

    def send_to_phy(self, binary: str) -> int:
        """向本机物理层发送消息。

        Args:
            binary: 要发送的消息。

        Returns:
            总共发送的字节数。
        """
        # 流量控制。
        sleep(Network.FLOW_INTERVAL)
        return self._send(string_to_bits(binary), self.__phy)

    def pack(self, message_data: dict) -> list[Frame]:
        """将消息打包为帧。

        Args:
            message_data: 本机应用层传来的消息数据。

        Returns:
            打包的帧列表。
        """
        # 解析传入的字典。
        message = message_data["message"]
        msgtype = message_data["msgtype"]
        dst = message_data["dst"]

        # 计算总共发送的帧数。
        total = Frame.calc_frame_num(message)

        # 请求帧。
        request = Frame()
        request.write(
            {
                "src": self.__app,
                "seq": 0,
                "data": f"{dec_to_bin(total, FramePack.DATA_LEN//2)}{encode_ascii(msgtype)}",
                "dst": dst,
            }
        )
        frames = [request]

        # 消息帧。
        for i in range(0, total):
            sub_message = message[i * FramePack.DATA_LEN : (i + 1) * FramePack.DATA_LEN]
            frame = Frame()
            frame.write(
                {
                    "src": self.__app,
                    "seq": (i + 1) % (2 ** FramePack.SEQ_LEN),
                    "data": sub_message,
                    "dst": dst,
                }
            )
            frames.append(frame)

        return frames

    def should_receive(self, port: str) -> bool:
        """判断本层是否应该接收某帧。

        Args:
            发来的帧的目的端口号。

        Returns:
            应该接收为`True`，不应该接收为`False`。
        """
        return port in (self.__app, Topology.BROADCAST_PORT)

    def generate_ack(self, seq: int, dst: str) -> str:
        """生成ACK帧。

        Args:
            seq: ACK的序号。
            dst: ACK的目的地，即原消息的源。

        Returns:
            该ACK的01字符串。
        """
        ack = Frame()
        ack.write(
            {
                "src": self.__app,
                "seq": seq,
                "data": encode_ascii(FramePack.ACK),
                "dst": dst,
            }
        )
        return ack.binary

    def generate_nak(self, seq: int, dst: str) -> str:
        """生成NAK帧。

        Args:
            seq: NAK的序号。
            dst: NAK的目的地，即原消息的源。

        Returns:
            该NAK的01字符串。
        """
        nak = Frame()
        nak.write(
            {
                "src": self.__app,
                "seq": seq,
                "data": encode_ascii(FramePack.NAK),
                "dst": dst,
            }
        )
        return nak.binary
