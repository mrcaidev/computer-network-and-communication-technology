import socket
from select import select

from utils.params import Network


class AbstractLayer:
    """各网元层的抽象父类。

    实现了套接字相关的四项基本功能：绑定、接收、发送、select。
    """

    def __init__(self, port: str) -> None:
        """初始化套接字。

        创建绑定在指定端口的套接字，并设置默认超时时间。

        Args:
            port: 套接字要绑定的端口。
        """
        # 创建套接字。
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 绑定端口号。
        try:
            self.__socket.bind(("127.0.0.1", int(port)))
        except OSError:
            print(f"[Error] Port {port} is currently occupied.")
            exit(-1)

        # 设置默认超时时间。
        self.__socket.settimeout(Network.USER_TIMEOUT)

    def _receive(
        self,
        bufsize: int = Network.INTER_NE_BUFSIZE,
        timeout: int = Network.USER_TIMEOUT,
    ) -> tuple[str, str, bool]:
        """接收数据。

        使用指定大小的缓存区，在指定超时时间内，接收发到本套接字的数据。

        Args:
            bufsize: 可选，缓存区大小，单位为位；默认为`INTER_NE_BUFSIZE`。
            timeout: 可选，超时时间，单位为秒；默认为`USER_TIMEOUT`。

        Returns:
            - [0] 接收到的数据。
            - [1] 发来该数据的地址的端口号。
            - [2] 接收成功为`True`，接收超时为`False`。
        """
        timeout_assigned = timeout != Network.USER_TIMEOUT

        # 如果指定了超时时间，就在发送前设置。
        if timeout_assigned:
            self.__socket.settimeout(timeout)

        result = ("", "", False)
        # 尝试接收数据。
        try:
            data, (_, port) = self.__socket.recvfrom(bufsize)
        # 如果接收超时，不进行异常处理。
        except socket.timeout:
            pass
        # 如果接收成功，则将接收到的`bytes`解码为`str`。
        else:
            result = (data.decode("utf-8"), str(port), True)
        # 不管超不超时，都要恢复默认超时值。
        finally:
            if timeout_assigned:
                self.__socket.settimeout(Network.USER_TIMEOUT)
            return result

    def _send(self, data: str, port: str) -> int:
        """向指定地址发送数据。

        Args:
            data: 要发送的数据。
            port: 指定地址的端口号。

        Returns:
            总共发送的字节数。
        """
        return self.__socket.sendto(data.encode("utf-8"), ("127.0.0.1", int(port)))

    @property
    def readable(self) -> bool:
        """检测是否有消息发到本层。

        使用`select()`方法检测本层套接字可读性。

        Returns:
            可读为`True`，不可读为`False`。
        """
        ready_sockets, _, _ = select([self.__socket], [], [], Network.SELECT_TIMEOUT)
        return len(ready_sockets) != 0
