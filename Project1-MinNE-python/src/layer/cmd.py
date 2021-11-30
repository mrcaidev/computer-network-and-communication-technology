from re import fullmatch

from utils.io import search_rsc
from utils.params import *

from layer._abstract import AbstractLayer


class CommandLayer(AbstractLayer):
    """控制台。"""

    def __init__(self) -> None:
        """初始化控制台。"""
        super().__init__(Topology.CMD_PORT)

    def __str__(self) -> str:
        """打印控制台信息。"""
        return f"[CMD] <Cmd layer @{Topology.CMD_PORT}>"

    def receive_from_user(self, input_type: InputType) -> str:
        """从用户键盘输入接收消息。

        Args:
            input_type: 用户输入的类型，包括：
            - `MODE`：网元模式。
            - `PORT`：目标应用层端口号。
            - `MSGTYPE`：消息类型。
            - `TEXT`：文本。
            - `FILE`：文件名。

        Returns:
            接收到的消息。
        """
        if input_type == InputType.MODE:
            return CommandLayer.__get_mode_from_user()
        elif input_type == InputType.PORT:
            return CommandLayer.__get_port_from_user()
        elif input_type == InputType.MSGTYPE:
            return CommandLayer.__get_msgtype_from_user()
        elif input_type == InputType.TEXT:
            return CommandLayer.__get_text_from_user()
        elif input_type == InputType.FILE:
            return CommandLayer.__get_file_from_user()
        else:
            return ""

    def send_to_app(self, message: str, port: str):
        return self._send(message, port)

    @staticmethod
    def __get_mode_from_user() -> str:
        """获取源设备的发送模式。

        Returns:
            源设备的发送模式，包括：
            - `UNICAST`: 单播模式。
            - `BROADCAST`: 广播模式。
        """
        while True:
            mode = input(">>> ")
            if not mode:
                pass
            elif mode not in Mode.LIST:
                print(f"[Warning] Invalid mode {mode}")
            else:
                return mode

    @staticmethod
    def __get_port_from_user() -> str:
        """获取目的地应用层端口号。

        Returns:
            目的应用层端口号。
        """
        while True:
            dst_device_id = input(">>> ")
            if not dst_device_id:
                pass
            if not fullmatch(r"[1-9]", dst_device_id):
                print("[Warning] ID should be an integer between 1 and 9")
            else:
                return f"1{dst_device_id}300"

    @staticmethod
    def __get_msgtype_from_user() -> str:
        """获取消息类型。

        Returns:
            消息类型，包括下列两种：
            - `TEXT`：文本。
            - `FILE`：文件。
        """
        while True:
            msgtype = input(">>> ")
            if not msgtype:
                pass
            elif msgtype not in MessageType.LIST:
                print(f"[Warning] Invalid type {msgtype}")
            else:
                return msgtype

    @staticmethod
    def __get_text_from_user() -> str:
        """获取文本。

        Returns:
            适合层间传输的文本。
        """
        while True:
            message = input(">>> ")
            if not message:
                pass
            elif len(message) > Network.MESSAGE_MAX_LEN:
                print(f"[Warning] Length exceeded ({len(message)} characters)")
            else:
                return message

    @staticmethod
    def __get_file_from_user() -> str:
        """获取文件名。

        Returns:
            文件的绝对路径。
        """
        while True:
            filename = input(">>> ")
            if not filename:
                pass
            else:
                filepath = search_rsc(filename)
                if not filepath:
                    print(f"[Warning] {filename} not found")
                else:
                    return filepath
