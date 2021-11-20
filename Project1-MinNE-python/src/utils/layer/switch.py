from collections import defaultdict
from select import select

import utils.constant as const
from utils.coding import bits_to_string, string_to_bits
from utils.layer._abstract import AbstractLayer


class SwitchTable(defaultdict):
    """端口地址表。"""

    def __init__(self) -> None:
        """初始化内部defaultdict。"""
        return super().__init__(dict[str, int])

    def __str__(self) -> None:
        """打印端口地址表。"""
        head = """------------------------
|       |    Remote    |
| Local |--------------|
|       | Port  | Life |"""

        body = "\n".join(
            filter(
                None,
                [
                    "|----------------------|\n"
                    + "\n".join(
                        [
                            f"| {local.center(5)} | {port.center(5)} | {str(life).center(4)} |"
                            for port, life in remotes.items()
                        ]
                    )
                    if len(remotes.items()) != 0
                    else None
                    for local, remotes in self.items()
                ],
            )
        )
        return f"{head}\n{body}\n{'-' * 24}"

    def refresh(self, reset_port: str):
        """
        刷新表内端口的寿命。

        Args:
            reset_port: 当前激活的远程端口号，需要重置其寿命。
        """
        for remotes in self.values():
            for port, life in remotes.copy().items():
                refreshed_life = (
                    const.Network.REMOTE_MAX_LIFE if port == reset_port else life - 1
                )
                if refreshed_life == 0:
                    remotes.pop(port)
                else:
                    remotes.update({port: refreshed_life})

    def update(
        self, local: str, remote: str, life: int = const.Network.REMOTE_MAX_LIFE
    ) -> bool:
        """
        更新端口地址表。

        Args:
            local: 本地物理层端口号。
            remote: 远程应用层端口号。

        Returns:
            有更新为True，无更新为False。
        """
        # 如果已经有这对关系，就不再追加。
        if remote in self.get(local, {}).keys():
            return False

        # 如果没有这对关系，就追加进字典。
        self[local].update({remote: life})
        return True

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
                lambda local: remote in self[local].keys(),
                self.keys(),
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
        return list(self.get(local, {}).keys())


class SwitchLayer(AbstractLayer, SwitchTable):
    """交换机网络层。"""

    def __init__(self, port: str) -> None:
        """
        初始化网络层。

        Args:
            port: 网络层端口号。
        """
        AbstractLayer.__init__(self, port)
        SwitchTable.__init__(self)

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
            self.update(port, const.Topology.BROADCAST_PORT, -1)

    def send_to_phy(self, binary: str, port: str) -> int:
        """
        向物理层发送消息。

        Args:
            binary: 要发的消息（01序列）。
            port: 信息要送到的本地物理层端口。

        Returns:
            总共发送的字节数。
        """
        return self._send(string_to_bits(binary), port)

    def receive_from_phy(self) -> tuple[str, str, bool]:
        """
        从物理层接收消息。

        Returns:
            一个三元元组。
            - [0] 接收到的消息。
            - [1] 消息来自的本地物理层端口。
            - [2] 是否接收成功，成功为True，失败为False。
        """
        binary, port, success = self._receive()
        binary = bits_to_string(binary) if success else binary
        return binary, port, success

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

    def print_table(self) -> None:
        print(SwitchTable.__str__(self))
