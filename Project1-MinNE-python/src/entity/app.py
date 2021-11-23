import os
from json import loads

from layer.app import AppLayer
from utils.coding import decode_image, decode_text, encode_image, encode_text
from utils.constant import File, InputType, MessageType, Mode, Topology


class AppEntity(AppLayer):
    """主机应用层实体。"""

    def __init__(self, device_id: int) -> None:
        """
        初始化实体。

        Args:
            device_id: 设备号。
        """
        # 打开配置文件。
        try:
            with open(
                os.path.join(
                    os.path.dirname(os.getcwd()), File.CONFIG_DIR, File.PORT_MAP
                ),
                mode="r",
                encoding="utf-8",
            ) as fr:
                # 读取该设备配置。
                try:
                    device_config = loads(fr.read())[str(device_id)]
                    app_port = device_config["app"]
                    net_port = device_config["net"]

                # 如果配置读取出错，就报错退出。
                except KeyError:
                    print(f"[Error] Wrong device id: {device_id}.")
                    exit(-1)

                # 如果读取成功，就初始化实体，打印信息。
                else:
                    super().__init__(app_port)
                    self.bind_net(net_port)
                    print(f"{'App'.center(30, '-')}\nApp: {app_port}\nNet: {net_port}")

        # 如果找不到配置文件，就报错退出。
        except FileNotFoundError:
            print("[Error] Config JSON not found.")
            exit(-1)

    def enter_mode(self) -> None:
        """网元进入指定模式。"""
        self.mode = self.receive_from_user(InputType.MODE)
        self.send_to_net(self.mode)

    def recv(self) -> None:
        """接收模式。"""
        # 接收消息类型和消息本体。
        msgtype = self.receive_from_net()
        message = self.receive_from_net()

        # 如果收到的是文本。
        if msgtype == MessageType.TEXT:
            text = decode_text(message)
            self.send_to_user(f"[Log] Received text: {text}")

        # 如果收到的是图片。
        elif msgtype == MessageType.FILE:
            success = decode_image(message)
            if success:
                self.send_to_user("[Log] Received image: Saved under /img.")
            else:
                self.send_to_user("[Warning] Failed to save image.")

        # 如果是不支持的消息类型。
        else:
            self.send_to_user(f"[Warning] Message type not supported: {msgtype}.")

    def common_send(self, dst: str) -> None:
        """
        发送模式。

        Args:
            dst: 消息的目标端口。
        """
        # 发送目标端口。
        self.send_to_net(dst)

        # 发送消息类型。
        msgtype = self.receive_from_user(InputType.MSGTYPE)
        self.send_to_net(msgtype)

        # 如果要发送文本。
        if msgtype == MessageType.TEXT:
            text = self.receive_from_user(InputType.TEXT)
            self.send_to_net(encode_text(text))

        # 如果要发送图片。
        elif msgtype == MessageType.FILE:
            filepath = self.receive_from_user(InputType.FILE)
            self.send_to_net(encode_image(filepath))

        # 如果是不支持的消息类型。
        else:
            self.send_to_user(f"[Warning] Message type not supported: {msgtype}.")

    def unicast(self) -> None:
        """单播模式。"""
        dst = self.receive_from_user(InputType.PORT)
        self.common_send(dst)

    def broadcast(self) -> None:
        """广播模式。"""
        dst = Topology.BROADCAST_PORT
        self.common_send(dst)

    def run(self) -> None:
        """启动应用层。"""
        while True:
            self.enter_mode()
            if self.mode == Mode.QUIT:
                break
            elif self.mode == Mode.RECEIVE:
                self.recv()
            elif self.mode == Mode.UNICAST:
                self.unicast()
            elif self.mode == Mode.BROADCAST:
                self.broadcast()
