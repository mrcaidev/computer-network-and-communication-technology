from dataclasses import dataclass
from select import select

from utils.coding import bits_to_string, string_to_bits
from utils.constant import Network, Topology
from utils.io import get_device_map, get_router_env

from layer._abstract import AbstractLayer


@dataclass
class Path:
    """路由表内存储的，到达目的地的路径。"""

    # 路线的下一跳。
    next: str
    # 到达下一跳的本地物理层端口。
    exit: str
    # 到达目的地的费用。
    cost: int
    # 当前是否已经最优化。
    optimized: bool


class RouterTable:
    """路由表。"""

    def __init__(self, device_id: str) -> None:
        """初始化路由表。"""
        self._table: dict[str, Path] = {}
        self._device_id = device_id
        self.init_env(get_router_env(device_id))

    def __str__(self) -> str:
        """打印路由表。"""
        head = f"{'-'*45}\n| Destination | Next hop | Exit port | Cost |\n|{'-'*13}|{'-'*10}|{'-'*11}|{'-'*6}|"
        body = "\n".join(
            [
                f"|{dst.center(13)}|{path.next.center(10)}|{path.exit.center(11)}|{str(path.cost).center(6)}|"
                for dst, path in filter(
                    lambda item: item[0] != self._device_id, self._table.items()
                )
            ]
        )
        return f"{head}\n{body}\n{'-'*45}"

    def init_env(self, environment: dict[str, dict]) -> None:
        """
        初始化路由表周围环境。

        Args:
            environment: 包含路由器周围环境的字典，键值对格式如下：
            - 键：相邻路由器网络层端口号。
            - 值：一个字典，包括下列两个键：
                - exit: 要到达该路由器，要走哪个本地物理层端口。
                - cost: 到达该路由器的费用。
        """
        # 到自己的费用始终为0。
        self._table[self._device_id] = Path(next="", exit="", cost=0, optimized=True)

        # 依传入的字典逐项初始化。
        min_cost, min_dst = float("inf"), ""
        for dst, dic in environment.items():
            # 记录到达周围路由器的路径。
            cur_cost = dic["cost"]
            self._table[dst] = Path(
                next=dst, exit=dic["exit"], cost=cur_cost, optimized=False
            )
            # 顺便找到费用最小值。
            if cur_cost < min_cost:
                min_cost = cur_cost
                min_dst = dst

        # 记录当前费用最低的路由器端口号。
        self.next_merge = min_dst

    def pack(self) -> str:
        """
        将路由表中的路径打包为字符串，包括下一跳与费用。

        Returns:
            路径信息包，格式为"device_id:dst,cost|dst,cost|..."。
        """
        return f"{self._device_id}:{'|'.join(f'{dst}-{cost}' for dst, cost in filter(lambda item: item[0] != self._device_id, [(dst, str(path.cost)) for dst, path in self._table.items()]))}"

    @staticmethod
    def unpack(string: str) -> tuple[str, dict[str, int]]:
        """
        将字符串解包为路由表。

        Args:
            string: 包含路由表信息的字符串。

        Returns:
            一个二元元组。
            - [0] 发来路径包的设备号。
            - [1] 新路由表，键值对格式如下：
                - 键：目的路由器网络层端口号。
                - 值：到达该路由器的费用。
        """
        # 解包源设备号。
        src_id, string = string.split(":")

        # 解包路径信息。
        new_table: dict[str, int] = {}
        for path in string.split("|"):
            dst, cost = path.split("-")
            new_table[dst] = int(cost)

        return src_id, new_table

    def merge(self, package: str) -> None:
        """
        合并外部路由表与本地路由表。

        Args:
            src: 外部路由表的来源。
            package: 发来的路由表路径包。
        """
        # 解包字符串为路由表。
        src, table = RouterTable.unpack(package)

        # 标记到达该来源的路径为最优化。
        self._table[src].optimized = True

        # 创建本地路由表的一份浅拷贝。
        local_copy = self._table.copy()

        # 遍历更新本地路由表。
        min_cost, min_dst = float("inf"), ""
        for dst, new_cost in table.items():
            # 比对两表内，关于该目的地的数据。
            local_path = self._table.get(dst, None)
            new_path = Path(
                next=src,
                exit=self._table[src].exit,
                cost=new_cost + self._table[src].cost,
                optimized=False,
            )

            # 如果表里没有这条记录，就追加进表。
            if local_path == None:
                self._table[dst] = new_path
                cur_cost = new_cost

            # 如果这条记录已经是最优化的，就跳过。
            elif local_path.optimized:
                continue

            # 如果本地记录费用低，就维持本地路径。
            elif local_path.cost < new_path.cost:
                cur_cost = local_path.cost

            # 如果新记录费用低，就更新路径。
            else:
                self._table[dst] = new_path
                cur_cost = new_cost

            # 更新当前非最优化路径集的费用最小值。
            if min_cost > cur_cost:
                min_cost = cur_cost
                min_dst = dst

            # 如果这条路径原来就有，就在拷贝中删掉这一条。
            if local_path != None:
                local_copy.pop(dst)

        # 检测还有哪些端口没被比较过最小值。
        remained = dict(filter(lambda item: not item[1].optimized, local_copy.items()))

        # 如果还有端口没被比较过，就将最小值与这些端口相比较。
        if remained != {}:
            min_item = min(remained.items(), key=lambda item: item[1].cost)
            if min_item[1].cost < min_cost:
                min_dst = min_item[0]

        # 记录最小值对应的端口。
        self.next_merge = min_dst

        # 排序路由表。
        self._table = dict(sorted(self._table.items(), key=lambda item: item[0]))

    def search(self, app: str) -> Path:
        """
        在路由表中查询到达目的应用层的路径。

        Args:
            dst: 目的应用层端口号。

        Returns:
            到达目的地的路径。
        """
        try:
            app_router = list(
                filter(lambda router: app[:1] == router[:1], self._table.keys())
            )[0]
        except IndexError:
            return Path(next=Topology.DEFAULT_ROUTER, exit="", cost=0, optimized=False)
        else:
            return self[app_router]


class RouterLayer(RouterTable, AbstractLayer):
    """路由器网络层。"""

    def __init__(self, device_id: str) -> None:
        """
        初始化网络层。

        Args:
            device_id: 设备号。
        """
        # 初始化套接字。
        config = get_device_map(device_id)
        AbstractLayer.__init__(self, config["net"])
        self._phy = config["phy"]

        # 初始化路由表。
        RouterTable.__init__(self, device_id)

    def __str__(self) -> str:
        """打印网络层信息。"""
        return f"[Device {self._device_id}] <Router Layer @{self._port}>"

    def send_to_phy(self, binary: str, port: str) -> int:
        """
        向物理层发送消息。

        Args:
            binary: 要发的消息。（01字符串）
            port: 信息要送到的本地物理层端口。

        Returns:
            总共发送的字节数。
        """
        return self._send(string_to_bits(binary), port)

    def receive_from_phy(self) -> tuple[str, bool]:
        """
        从物理层接收消息。

        Returns:
            一个二元元组。
            - [0] 接收到的消息。
            - [1] 是否接收成功，成功为True，失败为False。
        """
        binary, _, success = self._receive()
        binary = bits_to_string(binary) if success else binary
        return binary, success

    def has_message(self) -> bool:
        """
        检测本层套接字是否有可读消息。

        Returns:
            可读为True，不可读为False。
        """
        ready_sockets, _, _ = select([self._socket], [], [], Network.SELECT_TIMEOUT)
        return len(ready_sockets) != 0

    def print_table(self) -> None:
        print(RouterTable.__str__(self))
