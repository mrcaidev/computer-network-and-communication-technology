import os

from utils.constant import InputType, MessageType, Mode, Network, Others
from utils.layer._abstractlayer import AbstractLayer


class AppLayer(AbstractLayer):
    """主机应用层。"""

    def __init__(self, port: str) -> None:
        """
        初始化应用层。

        Args:
            port: 应用层端口号。
        """
        super().__init__(port)
        self._net = "-1"

    def __str__(self) -> str:
        """打印应用层信息。"""
        return f"<App Layer at 127.0.0.1:{self._port} {{Net:{self._net}}}>"

    def bind_net(self, port: str) -> None:
        """
        绑定网络层地址。

        Args:
            port: 网络层端口号。
        """
        self._net = port

    def receive_from_net(self) -> str:
        """
        从网络层接收消息。

        Returns:
            接收到的消息。
        """
        port = "-1"
        while port != self._net:
            message, port, _ = self._receive(bufsize=Network.IN_NE_BUFSIZE)
        return message

    def send_to_net(self, message: str) -> int:
        """
        向网络层发送消息。

        Args:
            message: 要发的消息。

        Returns:
            总共发送的字节数。
        """
        return self._send(message, self._net)

    def receive_from_user(self, input_type: InputType) -> str:
        """
        从用户键盘输入接收消息。

        Args:
            input_type: 用户输入的分类，包括下列五种：
            - `utils.constant.InputType.MODE`：网元模式。
            - `utils.constant.InputType.PORT`：端口号。
            - `utils.constant.InputType.MESSAGE_TYPE`：要发送的消息类型。
            - `utils.constant.InputType.TEXT`：要发送的消息。
            - `utils.constant.InputType.FILENAME`：要发送的图片文件名。

        Returns:
            接收到的消息。
        """
        if input_type == InputType.MODE:
            return AppLayer._get_mode_from_user()
        elif input_type == InputType.PORT:
            return AppLayer._get_port_from_user()
        elif input_type == InputType.MESSAGE_TYPE:
            return AppLayer._get_msgtype_from_user()
        elif input_type == InputType.TEXT:
            return AppLayer._get_text_from_user()
        elif input_type == InputType.FILENAME:
            return AppLayer._get_imgname_from_user()
        else:
            return ""

    def send_to_user(self, message: str) -> None:
        """
        终端打印消息。

        Args:
            message: 要打印的消息。
        """
        print(message)

    def _get_mode_from_user() -> str:
        """
        从用户键盘输入获取当前工作模式。

        Returns:
            网元当前的工作模式，包括下列四种：
            - `utils.constant.Mode.RECV`: 接收模式。
            - `utils.constant.Mode.UNICAST`: 单播模式。
            - `utils.constant.Mode.BROADCAST`: 广播模式。
            - `utils.constant.Mode.QUIT`: 退出程序。
        """
        print(
            f"""{'-'*29}\n|{'Select Mode'.center(27)}|\n| 1::Receive     2::Unicast |\n| 3::Broadcast   4::Quit    |\n{'-'*29}"""
        )
        while True:
            mode = input(">>> ")
            if mode in Mode.LIST:
                return mode
            else:
                print("[Warning] Invalid mode!")

    def _get_port_from_user() -> str:
        """
        从用户键盘输入获取端口号。

        Returns:
            在[1, 65535]区间内的端口号。
        """
        print("Input destination port:")
        while True:
            port = input(">>> ")
            try:
                port_num = int(port)
            except Exception:
                print("[Warning] Port should be an integer.")
                continue
            else:
                if 1 <= port_num <= 65535:
                    return port
                else:
                    print("[Warning] Port should fall between 1 and 65535.")

    def _get_msgtype_from_user() -> str:
        """
        从用户键盘输入获取要发送的消息类型。

        Returns:
            消息类型，包括下列两种：
            - `utils.constant.MessageType.TEXT`：字符串。
            - `utils.constant.MessageType.FILENAME`：图片文件。
        """
        print("Input message type:\n1::Text  2::Picture")
        while True:
            message_type = input(">>> ")
            if message_type in MessageType.LIST:
                return message_type
            else:
                print("[Warning] Invalid message type!")

    def _get_text_from_user() -> str:
        """
        从用户键盘输入获取要发送的消息。

        Returns:
            消息字符串。
        """
        print("Input a piece of message:")
        while True:
            message = input(">>> ")
            if message != "":
                return message

    def _get_imgname_from_user() -> str:
        """
        从用户键盘输入获取要发送的图片文件名。

        Returns:
            图片文件的绝对路径。
        """
        print("Input file name: (i.e. foo.png)")
        while True:
            # 获取图片文件名。
            filename = input(">>> ")
            filepath = os.path.join(
                os.path.dirname(os.getcwd()), Others.IMAGE_DIR, filename
            )

            # 检查是否有该文件。
            if os.path.exists(filepath):
                return filepath
            else:
                print(f"[Warning] {filepath} not found.")
