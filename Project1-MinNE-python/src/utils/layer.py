import socket
from collections import defaultdict
from select import select
from time import sleep

import utils.constant as const


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
        self._socket.settimeout(const.Network.USER_TIMEOUT)

    def __str__(self) -> str:
        """打印抽象层信息。"""
        return f"<Abstract Layer at 127.0.0.1:{self._port}>"

    @property
    def socket(self) -> socket.socket:
        """将该层套接字设为只读。"""
        return self._socket


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
        message, _ = self._socket.recvfrom(const.Network.MAX_BUFFER_SIZE)
        return str(message)[2:-1]

    def send_to_net(self, message: str) -> int:
        """
        向网络层发送消息。

        Args:
            message: 要发的消息。

        Returns:
            总共发送的字节数。
        """
        return self._socket.sendto(
            bytes(message, encoding="utf-8"), ("127.0.0.1", int(self._net))
        )

    def receive_from_user(self, input_type: const.InputType) -> str:
        """
        从用户键盘输入接收消息。

        Args:
            input_type: 用户输入的分类，包括下列三种：
            - `utils.constant.InputType.MODE`：网元模式。
            - `utils.constant.InputType.PORT`：端口号。
            - `utils.constant.InputType.MESSAGE`：要发送的消息。

        Returns:
            接收到的消息。
        """
        if input_type == const.InputType.MODE:
            return AppLayer._get_mode_from_user()
        elif input_type == const.InputType.PORT:
            return AppLayer._get_port_from_user()
        elif input_type == const.InputType.MESSAGE:
            return AppLayer._get_message_from_user()
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
            """-----------------------------
|        Select mode        |
| 1::Receive     2::Unicast |
| 3::Broadcast   4::Quit    |
-----------------------------"""
        )
        while True:
            mode = input(">>> ")
            if mode in const.Mode.LIST:
                return mode

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
                print("[Error] Port should be an integer.")
                continue
            else:
                if 1 <= port_num <= 65535:
                    return port
                else:
                    print("[Error] Port should fall between 1 and 65535.")

    def _get_message_from_user() -> str:
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


class NetLayer(AbstractLayer):
    """主机网络层。"""

    def __init__(self, port: str) -> None:
        """
        初始化网络层。

        Args:
            port: 网络层端口号。
        """
        super().__init__(port)
        self._app = "-1"
        self._phy = "-1"

    def __str__(self) -> str:
        """打印网络层信息。"""
        return f"<Net Layer at 127.0.0.1:{self._port} {{App:{self._app}, Phy:{self._phy}}}>"

    def bind_app(self, port: str) -> None:
        """
        绑定应用层地址。

        Args:
            port: 应用层端口号。
        """
        self._app = port

    def send_to_app(self, message: str) -> int:
        """
        向应用层发送消息。

        Args:
            message: 要发的消息。

        Returns:
            总共发送的字节数。
        """
        return self._socket.sendto(
            bytes(message, encoding="utf-8"), ("127.0.0.1", int(self._app))
        )

    def receive_from_app(self) -> str:
        """
        从应用层接收消息。

        Returns:
            接收到的消息。
        """
        message, _ = self._socket.recvfrom(const.Network.MAX_BUFFER_SIZE)
        return str(message)[2:-1]

    def bind_phy(self, port: str) -> None:
        """
        绑定物理层地址。

        Args:
            port: 物理层端口号。
        """
        self._phy = port

    def send_to_phy(self, binary: str) -> int:
        """
        向物理层发送消息。

        Args:
            binary: 要发的消息（01序列）。

        Returns:
            总共发送的字节数。
        """
        binary = "".join(list(map(lambda char: chr(ord(char) - ord("0")), binary)))
        sleep(const.Network.FLOW_INTERVAL)
        return self._socket.sendto(
            bytes(binary, encoding="utf-8"), ("127.0.0.1", int(self._phy))
        )

    def receive_from_phy(
        self, timeout: int = const.Network.RECV_TIMEOUT
    ) -> tuple[str, bool]:
        """
        从物理层接收消息。

        Args:
            timeout: 接收超时时间，单位为秒，默认为`utils.constant.Network.RECV_TIMEOUT`。

        Returns:
            一个二元元组。
            - [0] 接收到的消息。
            - [1] 是否接收成功，成功为True，失败为False。
        """
        self._socket.settimeout(timeout)
        try:
            binary, _ = self._socket.recvfrom(const.Network.MAX_BUFFER_SIZE)
        except socket.timeout:
            result = ("", False)
        else:
            binary = "".join(list(map(lambda bit: chr(bit + ord("0")), binary)))
            result = (binary, True)
        finally:
            self._socket.settimeout(const.Network.USER_TIMEOUT)
            return result


class SwitchLayer(AbstractLayer):
    """交换机网络层。"""

    def __init__(self, port: str) -> None:
        """
        初始化网络层。

        Args:
            port: 网络层端口号。
        """
        super().__init__(port)
        self._port_table = defaultdict(dict[str, int])

    def __str__(self) -> str:
        """打印网络层信息。"""
        return f"<Switch Layer at 127.0.0.1:{self._port}>"

    def bind_phys(self, ports: list[str]) -> None:
        """
        在端口地址表中记录本地物理层到广播端口。

        Args:
            ports: 本地物理层端口号列表。
        """
        for port in ports:
            self._port_table[port].update({const.Topology.BROADCAST_PORT: -1})

    def send_to_phy(self, binary: str, port: str) -> int:
        """
        向物理层发送消息。

        Args:
            binary: 要发的消息（01序列）。
            port: 信息要送到的本地物理层端口。

        Returns:
            总共发送的字节数。
        """
        binary = "".join(list(map(lambda char: chr(ord(char) - ord("0")), binary)))
        sleep(const.Network.FLOW_INTERVAL)
        return self._socket.sendto(
            bytes(binary, encoding="utf-8"), ("127.0.0.1", int(port))
        )

    def receive_from_phy(
        self, timeout: int = const.Network.RECV_TIMEOUT
    ) -> tuple[str, str, bool]:
        """
        从物理层接收消息。

        Args:
            timeout: 接收超时时间，单位为秒，默认为`utils.constant.Network.RECV_TIMEOUT`。

        Returns:
            一个三元元组。
            - [0] 接收到的消息。
            - [1] 消息来自的本地物理层端口。
            - [2] 是否接收成功，成功为True，失败为False。
        """
        self._socket.settimeout(timeout)
        try:
            binary, (_, port) = self._socket.recvfrom(const.Network.MAX_BUFFER_SIZE)
        except socket.timeout:
            ret = ("", -1, False)
        else:
            binary = "".join(list(map(lambda bit: chr(bit + ord("0")), binary)))
            ret = (binary, str(port), True)
        finally:
            self._socket.settimeout(const.Network.USER_TIMEOUT)
            return ret

    def has_message(self) -> bool:
        """
        检测本层套接字是否有可读消息。

        Returns:
            可读为True，不可读为False。
        """
        ready_sockets, _, _ = select(
            [self._socket], [], [], const.Network.SELECT_TIMEOUT
        )
        return len(ready_sockets) != 0

    def remove_expired(self, remote: str) -> bool:
        """
        清除过期的端口地址关系。

        Args:
            remote: 当前激活的远程端口号，需要重置其寿命。
        """
        removed = False
        for remotes in self._port_table.values():
            for port, life in remotes.copy().items():
                if port == remote:
                    remotes.update({port: const.Network.REMOTE_LIFE})
                else:
                    remotes.update({port: life - 1})
                if life == 0:
                    remotes.pop(port)
                    removed = True
        return removed

    def update_table(self, relations: dict[str, dict[str, int]]) -> bool:
        """
        更新端口地址表。

        Args:
            包含若干对应关系的字典，包含两个键。
            - local: 本地物理层的端口号。
            - remote: 远程应用层的端口号。

        Returns:
            有更新为True，无更新为False。
        """
        updated = False
        # 逐一更新。
        for local, remote in relations.items():
            # 如果已经有这对关系，就不再追加。
            if self.has_relation(local, remote):
                continue
            # 如果没有这对关系，就追加进列表。
            self._port_table[local].update({remote: const.Network.REMOTE_LIFE})
            updated = True

        return updated

    def search_locals(self, remote: str) -> list[str]:
        """
        在端口地址表中查找本地端口号。

        Args:
            remote: 某一远程应用层的端口号。

        Returns:
            对应的本地物理层端口号列表。
        """
        return list(
            filter(
                lambda local: remote in self._port_table[local].keys(),
                self._port_table.keys(),
            )
        )

    def search_remotes(self, local: str) -> list[str]:
        """
        在端口地址表中查找远程端口号。

        Args:
            local: 某一本地物理层的端口号。

        Returns:
            对应的远程应用层端口号列表。
        """
        return list(self._port_table.get(local, {}).keys())

    def has_relation(self, local: str, remote: str) -> bool:
        """
        在端口地址表中查找某一对应关系。

        Args:
            local: 本地物理层的端口号。
            remote: 远程应用层的端口号。

        Returns:
            有该关系为True，没有该关系为False。
        """
        return remote in self._port_table.get(local, {}).keys()

    def print_table(self) -> None:
        print(
            """------------------------
|       |    Remote    |
| Local |--------------|
|       | Port  | Life |"""
        )
        for local, remotes in self._port_table.items():
            print("|----------------------|")
            for port, life in remotes.items():
                print(
                    f"| {local.center(5)} | {port.center(5)} | {str(life).center(4)} |"
                )
        print("-" * 24)
