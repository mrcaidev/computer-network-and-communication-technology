import socket

from utils.constant import Network


class AbstractLayer:
    """各网元层的抽象父类。"""

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
        return f"<Abstract Layer @{self._port}>"

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
