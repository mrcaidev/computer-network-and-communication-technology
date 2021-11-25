import socket

from utils.params import Network


class AbstractLayer:
    """各网元层的抽象父类。

    封装了套接字的三项基本功能：绑定、接收、发送。
    方法均为受保护类型，仅供具体网元层继承，不提供任何API供外部调用。
    """

    def __init__(self, port: str) -> None:
        """初始化套接字。

        创建绑定在指定端口的套接字，并设置默认超时时间。

        Args:
            port: 套接字要绑定的端口。
        """
        # 创建套接字。
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 绑定端口号。
        try:
            self._socket.bind(("127.0.0.1", int(port)))
        except OSError:
            print(f"[OS Error] Port {port} is currently occupied.")
            exit(-1)

        # 设置默认超时时间。
        self._socket.settimeout(Network.USER_TIMEOUT)

    def _receive(
        self,
        bufsize: int = Network.INTER_NE_BUFSIZE,
        timeout: int = Network.USER_TIMEOUT,
    ) -> tuple[str, str, bool]:
        """接收数据。

        使用指定大小的缓存区，在指定超时时间内，接收发到本套接字的数据。

        Args:
            bufsize: 可选，缓存区大小，单位为位，默认为`utils.params.Network.INTER_NE_BUFSIZE`。
            timeout: 可选，超时时间，单位为秒，默认为`utils.params.Network.USER_TIMEOUT`。

        Returns:
            - [0] 接收到的数据。
            - [1] 发来该数据的地址的端口号。
            - [2] 是否成功接收，成功为`True`，失败为`False`。
        """
        # 如果指定了超时时间，就在发送前设置。
        if timeout != Network.USER_TIMEOUT:
            self._socket.settimeout(timeout)

        result = ("", "", False)
        try:
            message, (_, port) = self._socket.recvfrom(bufsize)
        except socket.timeout:
            result = ("", "-1", False)
        else:
            result = (message.decode("utf-8"), str(port), True)
        finally:
            # 不管超不超时，都要恢复默认超时值。
            if timeout != Network.USER_TIMEOUT:
                self._socket.settimeout(Network.USER_TIMEOUT)
            return result

    def _send(self, data: str, port: str) -> int:
        """发送数据。

        向指定地址发送数据；数据可以是Unicode字符串或者01字符串。

        Args:
            data: 要发送的数据。
            port: 指定地址的端口号。

        Returns:
            总共发送的字节数。
        """
        return self._socket.sendto(data.encode("utf-8"), ("127.0.0.1", int(port)))
