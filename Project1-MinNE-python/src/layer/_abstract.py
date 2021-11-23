import os
import socket
from json import loads

from utils.constant import File, Network


class AbstractLayer:
    """各网元层的抽象父类。"""

    rootdir = "."

    def __init__(self, port: str) -> None:
        """
        初始化本层。

        Args:
            port: 本层所在端口。
        """
        # 创建套接字，绑定地址。
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(("127.0.0.1", int(self._port)))

        # 所有层套接字的默认超时时间均为`utils.constant.Network.USER_TIMEOUT`。
        self._socket.settimeout(Network.USER_TIMEOUT)

    def __str__(self) -> str:
        """打印抽象层信息。"""
        return f"<Abstract Layer at 127.0.0.1:{self._port}>"

    @property
    def socket(self) -> socket.socket:
        """将该层套接字设为只读。"""
        return self._socket

    def _send(self, message: str, port: str) -> int:
        """
        发送消息。

        Args:
            message: 要发送的消息。
            port: 要发送到的端口号。

        Returns:
            总共发送的字节数。
        """
        return self._socket.sendto(message.encode("utf-8"), ("127.0.0.1", int(port)))

    def _receive(
        self, bufsize: int = Network.INTER_NE_BUFSIZE, timeout: int = None
    ) -> tuple[str, str, bool]:
        """
        接收消息。

        Args:
            bufsize: 可选，缓存区大小，单位为位，默认为`utils.constant.Network.INTER_NE_BUFSIZE`。
            timeout: 可选，超时时间，单位为秒，默认为`None`。

        Returns:
            一个三元元组。
            - [0] 接收到的消息。
            - [1] 发来该消息的端口号。
            - [2] 是否成功接收，成功为True，失败为False。
        """
        # 如果指定了超时时间，就提前设置好。
        if timeout != None:
            self._socket.settimeout(timeout)

        ret = ("", "", None)
        try:
            message, (_, port) = self._socket.recvfrom(bufsize)
        except socket.timeout:
            ret = ("", "-1", False)
        else:
            ret = (message.decode("utf-8"), str(port), True)
        finally:
            # 不管超不超时，都要恢复默认超时值。
            if timeout != None:
                self._socket.settimeout(Network.USER_TIMEOUT)
            return ret

    @staticmethod
    def get_config(device_id: int) -> dict:
        """
        获取配置文件内的设备配置。

        Args:
            device_id: 设备号。

        Returns:
            包含该设备配置的字典，包含下列三个键：
            - "app": 该设备的应用层端口号。
            - "net": 该设备的网络层端口号。
            - "phy": 该设备的物理层端口号。
        """
        # 定位目录。
        AbstractLayer.__locate_root()

        # 打开配置文件。
        try:
            with open(
                os.path.join(AbstractLayer.rootdir, File.CONFIG_DIR, File.PORT_MAP),
                mode="r",
                encoding="utf-8",
            ) as fr:
                # 读取该设备配置。
                try:
                    config: dict = loads(fr.read())[str(device_id)]

                # 如果配置读取出错，就报错退出。
                except KeyError:
                    print(f"[Error] Wrong device id: {device_id}.")
                    exit(-1)

                # 如果配置读取成功，就存储该设备的三个端口。
                else:
                    return config

        # 如果找不到配置文件，就报错退出。
        except FileNotFoundError:
            print("[Error] Config JSON not found.")
            exit(-1)

    @classmethod
    def __locate_root(cls) -> None:
        """定位到根目录。"""
        # 如果已经定位过，就不再定位。
        if cls.rootdir != ".":
            return

        # 获取当前目录和上级目录。
        cwd = os.getcwd()
        upper_dir = os.path.dirname(cwd)

        # 如果配置目录在上级目录下，那么根目录是上级目录。
        if os.path.exists(os.path.join(upper_dir, File.CONFIG_DIR)):
            cls.rootdir = upper_dir

        # 如果配置目录在当前目录下，那么当前目录为根目录。
        elif os.path.exists(os.path.join(cwd, File.CONFIG_DIR)):
            cls.rootdir = cwd
