from collections import defaultdict
from select import select

from utils.coding import bits_to_string, string_to_bits
from utils.io import get_phynum
from utils.params import Network, Topology

from layer._abstract import AbstractLayer


class SwitchTable:
    """端口地址表。

    内部是`defaultdict`，键值对格式如下：
    - 键：本地物理层端口号。
    - 值：远程端口状态，键值对格式如下：
        - 键：远程应用层端口号。
        - 值：该远程端口号在表内的剩余寿命。

    实现了单播、广播、学习、清除。
    """

    def __init__(self) -> None:
        """初始化内部字典。"""
        self._table = defaultdict(dict[str, int])

    def __str__(self) -> None:
        """打印端口地址表。"""
        head = f"{'-'*24}\n|{' '*7}|{'Remote'.center(14)}|\n|{'Local'.center(7)}|{'-'*14}|\n|{' '*7}|{'Port'.center(7)}|{'Life'.center(6)}|"
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
                    for local, remotes in self._table.items()
                ],
            )
        )
        return f"{head}\n{body}\n{'-'*24}"

    def update(self, local: str, remote: str) -> bool:
        """更新端口地址表。

        Args:
            local: 当前激活的本地端口。
            remote: 当前激活的远程端口。

        Returns:
            端口地址表是否有更新，有更新为`True`，没有更新为`False`。
        """
        updated = False

        # 查询是否有该关系，没有就会迎来更新。
        if remote not in self._table[local].keys():
            updated = True

        # 不管之前有没有这对关系，它们的寿命都要重置为最大值+1。（后面的遍历会扣回最大值。）
        self._table[local].update({remote: Network.REMOTE_MAX_LIFE + 1})

        # 所有远程端口寿命-1。
        for remotes in self._table.values():
            for port, life in remotes.copy().items():
                life -= 1
                if life == 0:
                    remotes.pop(port)
                    updated = True
                else:
                    remotes.update({port: life})

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
                lambda local: remote in self._table[local].keys(),
                self._table.keys(),
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
        return list(self._table.get(local, {}).keys())


class SwitchLayer(SwitchTable, AbstractLayer):
    """交换机网络层。

    实现了交换机网络层-交换机物理层的消息单播、广播和select。
    """

    def __init__(self, device_id: str) -> None:
        """初始化交换机网络层。

        Args:
            device_id: 该交换机的设备号。
        """
        # 初始化套接字。
        self.__device_id = device_id
        self.__port = f"1{device_id}200"
        self.__phys = [f"1{device_id}10{i}" for i in range(get_phynum(device_id))]
        AbstractLayer.__init__(self, self.__port)

        # 初始化端口地址表。
        SwitchTable.__init__(self)
        self._table.update(
            dict([phy, {Topology.BROADCAST_PORT: float("inf")}] for phy in self.__phys)
        )

    def __str__(self) -> str:
        """打印设备号与端口号。"""
        return f"[Device {self.__device_id}] <Switch Layer @{self.__port}>"

    def receive_from_phys(self) -> tuple[str, str, bool]:
        """接收来自交换机物理层的消息。

        Returns:
            - [0] 接收到的01字符串。
            - [1] 发来消息的本地物理层端口。
            - [2] 是否接收成功，成功为`True`，失败为`False`。
        """
        binary, port, success = self._receive()
        binary = bits_to_string(binary) if success else binary
        return binary, port, success

    def unicast_to_phy(self, binary: str, port: str) -> int:
        """向指定物理层单播消息。

        Args:
            binary: 要发的01字符串。
            port: 信息要送到的本地物理层端口。

        Returns:
            总共发送的字节数。
        """
        return self._send(string_to_bits(binary), port)

    def broadcast_to_phys(self, binary: str, port: str) -> str:
        """向所有物理层广播消息，除了指定的端口。

        指定的端口一般是发来消息的端口。

        Args:
            binary: 要发的01字符串。
            port: 指定的端口号。

        Returns:
            发送到的端口列表字符串。
        """
        target_phys = list(filter(lambda phy: phy != port, self.__phys))
        for phy in target_phys:
            self.unicast_to_phy(binary, phy)
        return f"[{' '.join(target_phys)}]"

    def has_message(self) -> bool:
        """检测是否有消息发到本层。

        使用`select()`方法检测本层套接字可读性。

        Returns:
            可读为`True`，不可读为`False`。
        """
        ready_sockets, _, _ = select([self._socket], [], [], Network.SELECT_TIMEOUT)
        return len(ready_sockets) != 0

    def show_table(self) -> None:
        """打印端口地址表。"""
        print(SwitchTable.__str__(self))
