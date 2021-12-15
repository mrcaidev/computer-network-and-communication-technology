from time import sleep

from utils.coding import *
from utils.frame import *
from utils.params import *

from layer._abstract import AbstractLayer


class NetLayer(AbstractLayer):
    """主机网络层。

    实现了主机应用层 <-> 主机网络层 <-> 主机物理层的消息收发。
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

        self.__normal_builder = FrameBuilder()
        self.__normal_builder.build(
            src=self.__app,
            reply_state=ReplyState.ACK,
        )
        self.__reply_builder = FrameBuilder()
        self.__reply_builder.build(
            src=self.__app,
            session_state=SessionState.NORMAL,
            data="",
        )
        self.__parser = FrameParser()

    def __str__(self) -> str:
        """打印设备号与端口号。"""
        return f"[Device {self.__device_id}] <Net Layer @{self.__port}>\n{'-'*30}"

    def receive_all(self) -> tuple[str, bool]:
        """接收来自本机应用层与本机物理层的消息。

        Returns:
            - [0] 接收到的消息。
            - [1] 本机应用层发来为 `True`，本机物理层发来为 `False`。
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
            timeout: 可选，接收超时时间，单位为秒，默认为 `RECV_TIMEOUT`。

        Returns:
            - [0] 接收到的消息。
            - [1] 接收成功为 `True`，接收超时为 `False`。
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

    def should_receive(self, port: str) -> bool:
        """判断本层是否应该接收某帧。

        Args:
            发来的帧的目的端口号。

        Returns:
            应该接收为 `True`，不应该接收为 `False`。
        """
        return port in (self.__app, Topology.BROADCAST_PORT)

    def build_pool(self, app_data: dict) -> list[Frame]:
        """将消息打包为帧。

        Args:
            app_data: 本机应用层传来的消息数据。

        Returns:
            打包的帧列表。
        """
        message = app_data["message"]
        frame_num = Frame.calc_num(message)

        # 第一帧是请求帧。
        request_frame = self.__normal_builder.build(
            session_state=SessionState.REQ_TXT
            if app_data["msgtype"] == MessageType.TEXT
            else SessionState.REQ_IMG,
            dst=app_data["dst"],
        )
        frame_pool = [request_frame]

        # 中间的帧是常规帧。
        frame_pool.extend(
            [
                self.__normal_builder.build(
                    session_state=SessionState.NORMAL,
                    data=message[
                        i * FrameParam.DATA_LEN : (i + 1) * FrameParam.DATA_LEN
                    ],
                )
                for i in range(frame_num - 1)
            ]
        )

        # 最后一帧是结束帧。
        final_frame = self.__normal_builder.build(
            session_state=SessionState.FIN,
            data=message[(frame_num - 1) * FrameParam.DATA_LEN :],
        )
        frame_pool.append(final_frame)

        return frame_pool

    def build_ack(self, dst: str) -> Frame:
        """生成 ACK 帧。

        Args:
            dst: ACK 的目的地，即原消息的源。

        Returns:
            生成的 ACK 帧。
        """
        return self.__reply_builder.build(reply_state=ReplyState.ACK, dst=dst)

    def build_nak(self, dst: str) -> Frame:
        """生成 NAK 帧。

        Args:
            dst: NAK 的目的地，即原消息的源。

        Returns:
            生成的 NAK 帧。
        """
        return self.__reply_builder.build(reply_state=ReplyState.NAK, dst=dst)

    def parse_reply(self, binary: str) -> bool:
        """解析回复。

        Args:
            binary: 含有回复的 01 字符串。

        Returns:
            ACK 为 `True`，NAK 为 `False`。
        """
        response = self.__parser.parse(binary)
        return True if response.reply_state == ReplyState.ACK else False

    def parse_message(self, binary: str) -> Frame:
        """解析消息。

        Args:
            binary: 含有消息的 01 字符串。

        Returns:
            收到的消息帧。
        """
        return self.__parser.parse(binary)
