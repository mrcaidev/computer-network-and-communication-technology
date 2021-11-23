from collections import defaultdict
from select import select

from utils.coding import bits_to_string, string_to_bits
from utils.constant import Network, Topology

from layer._abstract import AbstractLayer


class SwitchTable(defaultdict):
    """端口地址表。"""

    def __init__(self) -> None:
        """初始化内部defaultdict。"""
        return super().__init__(dict[str, int])

    def __str__(self) -> None:
        """打印端口地址表。"""
        head = f"{'-'*24}\n|{'-'*7}|{'Remote'.center(14)}|\n|{'Local'.center(14)}|{'-'*14}|\n|{'-'*7}|{'Port'.center(7)}|{'Life'.center(6)}|"
        body = "\n".join(
            filter(
                None,
                [
                    "|----------------------|\n"
                    + "\n".join(
                        [
                            f"|{local.center(7)}|{port.center(7)}|{str(life).center(6)}|"
                            for port, life in remotes.items()
                        ]
                    )
                    if len(remotes.items()) != 0
                    else None
                    for local, remotes in self.items()
                ],
            )
        )
        return f"{head}\n{body}\n{'-'*24}"

    def refresh(self, local: str, remote: str) -> bool:
        """
        更新端口地址表。

        Args:
            local: 当前激活的本地端口。
            remote: 当前激活的远程端口。

        Returns:
            端口地址表是否有更新，有为True，没有为False。
        """
        updated = False

        # 查询是否有该关系，没有就会迎来更新。
        if remote not in self[local].keys():
            updated = True

        # 不管之前有没有这对关系，它们的寿命都要重置为最大值+1。（后面的遍历会扣回最大值。）
        self[local].update({remote: Network.REMOTE_MAX_LIFE + 1})

        # 所有远程端口寿命-1。
        for remotes in self.values():
            for port, life in remotes.copy().items():
                life -= 1
                if life == 0:
                    remotes.pop(port)
                    updated = True
                else:
                    remotes.update({port: life})

        # 返回是否有端口关系更新。
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

    def __init__(self, device_id: str) -> None:
        """
        初始化网络层。

        Args:
            device_id: 设备号。
        """
        SwitchTable.__init__(self)
        config = AbstractLayer.get_config(device_id)
        AbstractLayer.__init__(self, config["net"])
        self.phy = config["phy"]
        print("Switch".center(30, "-"))
        print(f"Net port: {self._port}\nNet port: {self.phy}")
        self.update(dict([port, {Topology.BROADCAST_PORT: -1}] for port in self.phy))

    def __str__(self) -> str:
        """打印网络层信息。"""
        return f"<Switch Layer at 127.0.0.1:{self._port}>"

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
        ready_sockets, _, _ = select([self._socket], [], [], Network.SELECT_TIMEOUT)
        return len(ready_sockets) != 0

    def print_table(self) -> None:
        print(SwitchTable.__str__(self))
