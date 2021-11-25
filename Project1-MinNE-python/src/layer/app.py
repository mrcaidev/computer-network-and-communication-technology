from re import fullmatch

from utils.io import get_device_map, search_rsc
from utils.params import InputType, MessageType, Mode, Network

from layer._abstract import AbstractLayer


class AppLayer(AbstractLayer):
    """主机应用层。

    实现了用户-主机应用层、主机应用层-主机网络层的消息收发。
    """

    def __init__(self, device_id: str) -> None:
        """初始化主机应用层。

        根据主机设备号，初始化本层的套接字。

        Args:
            device_id: 该主机的设备号。
        """
        self._device_id = device_id
        self.__port, self.__net_port = self.__get_app_map()
        super().__init__(self.__port)

    def __str__(self) -> str:
        """打印设备号与端口号。"""
        return f"[Device {self._device_id}] <App Layer @{self.__port}>"

    def __get_app_map(self) -> tuple[str, str]:
        """获取端口号。

        从配置文件内读取该主机的应用层、网络层端口号。

        Returns:
            - [0] 应用层端口号。
            - [1] 网络层端口号。
        """
        config = get_device_map(self._device_id)
        try:
            ports = (config["app"], config["net"])
        except KeyError:
            print(f"[Config Error] Device {self._device_id} layer absence")
            exit(-1)
        else:
            return ports

    def receive_from_net(self) -> str:
        """从主机网络层接收消息。

        Returns:
            接收到的消息。
        """
        # 保证消息来自网络层。
        port = ""
        while port != self.__net_port:
            message, port, _ = self._receive(bufsize=Network.IN_NE_BUFSIZE)
        return message

    def send_to_net(self, message: str) -> int:
        """向主机网络层发送消息。

        Args:
            message: 要发的消息。

        Returns:
            总共发送的字节数。
        """
        return self._send(message, self.__net_port)

    def receive_from_user(self, input_type: InputType) -> str:
        """从用户键盘输入接收消息。

        Args:
            input_type: 用户输入的类型，包括：
            - `utils.params.InputType.MODE`：网元模式。
            - `utils.params.InputType.DST`：目标设备号。
            - `utils.params.InputType.MSGTYPE`：消息类型。
            - `utils.params.InputType.TEXT`：文本。
            - `utils.params.InputType.FILE`：文件名。

        Returns:
            接收到的消息。
        """
        if input_type == InputType.MODE:
            return AppLayer.__get_mode_from_user()
        elif input_type == InputType.DST:
            return self.__get_dst_from_user()
        elif input_type == InputType.MSGTYPE:
            return AppLayer.__get_msgtype_from_user()
        elif input_type == InputType.TEXT:
            return AppLayer.__get_text_from_user()
        elif input_type == InputType.FILE:
            return AppLayer.__get_file_from_user()
        else:
            return ""

    @staticmethod
    def __get_mode_from_user() -> str:
        """获取网元当前的工作模式。

        Returns:
            网元当前的工作模式，包括：
            - `utils.params.Mode.RECEIVE`: 接收模式。
            - `utils.params.Mode.UNICAST`: 单播模式。
            - `utils.params.Mode.BROADCAST`: 广播模式。
            - `utils.params.Mode.QUIT`: 退出程序。
        """
        print(
            f"{'-'*29}\n|{'Select Mode'.center(27)}|\n| 1::Receive     2::Unicast |\n| 3::Broadcast   4::Quit    |\n{'-'*29}"
        )
        while True:
            mode = input(">>> ")
            if not mode:
                pass
            elif mode not in Mode.LIST:
                print(f"[Warning] Invalid mode {mode}")
            else:
                return mode

    def __get_dst_from_user(self) -> str:
        """获取目的应用层端口号。

        用户输入的是设备号，通过地址解析映射到端口号。

        Returns:
            目的应用层端口号。
        """
        print("Input destination device ID:")
        while True:
            dst_device_id = input(">>> ")
            if not dst_device_id:
                pass
            if not fullmatch(r"[1-9]", dst_device_id):
                print("[Warning] ID should be an integer between 1 and 9")
            elif dst_device_id == self._device_id:
                print("[Warning] This is my ID")
            else:
                return f"1{dst_device_id}300"

    @staticmethod
    def __get_msgtype_from_user() -> str:
        """获取消息类型。

        Returns:
            消息类型，包括下列两种：
            - `utils.params.MessageType.TEXT`：文本。
            - `utils.params.MessageType.FILE`：文件。
        """
        print("Input message type:\n1::Text  2::File")
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
        print("Input text:")
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
        print("Input file name:")
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
