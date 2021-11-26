from dataclasses import dataclass
from select import select
from time import time

from utils.coding import bits_to_string, encode_text, string_to_bits
from utils.frame import Frame
from utils.io import get_device_map, get_router_env
from utils.params import FramePack, Network, Topology

from layer._abstract import AbstractLayer


@dataclass
class Path:
    """路径结构。"""

    # 路线的下一跳。
    next: str
    # 到达下一跳的本地物理层端口。
    exit: str
    # 到达目的地的费用。
    cost: int
    # 当前是否已经最优化。
    optimized: bool


@dataclass
class TableCache:
    """路由表缓存。"""

    # 目前接收到的路由表字符串。
    string: str
    # 是否接收完毕。
    completed: bool


class RouterTable:
    """路由表。

    内部是`dict`，键值对格式如下：
    - 键：路由器设备号。
    - 值：到达该路由器的路径。

    实现了`Dijkstra`算法、解包、打包。
    """

    def __init__(self, device_id: str) -> None:
        """初始化路由表。

        根据路由器设备号，初始化路由表周围环境。

        Args:
            device_id: 该路由器的设备号。
        """
        self._device_id = device_id
        self._table: dict[str, Path] = {}
        self.__init_env(get_router_env(device_id))

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

    def __init_env(self, environment: dict[str, dict]) -> None:
        """初始化路由表周围环境。

        读取配置文件，记录下相邻的路由器设备号，以及到达它们的本地物理层端口号、费用。

        Args:
            environment: 路由器周围环境，键值对格式如下：
            - 键：相邻路由器网络层端口号。
            - 值：一个字典，包括：
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
        """打包路由表。

        将路由表中的下一跳与费用（除了到达自身的）打包为字符串。

        Returns:
            路由表包，格式为"device:dst-cost|dst-cost|...|dst-cost:$"。
        """
        return f"{self._device_id}:{'|'.join(f'{dst}-{cost}' for dst, cost in filter(lambda item: item[0] != self._device_id, [(dst, str(path.cost)) for dst, path in self._table.items()]))}:$"

    @staticmethod
    def unpack(string: str) -> tuple[str, dict[str, int]]:
        """将字符串解包为路由表。

        Args:
            string: 包含路由表信息的字符串。

        Returns:
            - [0] 发来路径包的设备号。
            - [1] 新路由表，键值对格式如下：
                - 键：目的路由器网络层端口号。
                - 值：到达该路由器的费用。
        """
        # 解包源设备号。
        src_id, string, _ = string.split(":")

        # 解包路径信息。
        new_table: dict[str, int] = {}
        for path in string.split("|"):
            dst, cost = path.split("-")
            new_table[dst] = int(cost)

        return src_id, new_table

    def merge(self, package: str) -> None:
        """合并外部路由表与本地路由表。

        采用`Dijkstra`算法更新本地路由表路径。

        Args:
            package: 发来的路由表包。
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
            if local_path:
                local_copy.pop(dst)

        # 检测还有哪些端口没被比较过最小值。
        remained = dict(filter(lambda item: not item[1].optimized, local_copy.items()))

        # 如果还有端口没被比较过，就将最小值与这些端口相比较。
        if remained:
            min_item = min(remained.items(), key=lambda item: item[1].cost)
            if min_item[1].cost < min_cost:
                min_dst = min_item[0]

        # 记录最小值对应的端口。
        self.next_merge = min_dst

        # 排序路由表。
        self._table = dict(sorted(self._table.items(), key=lambda item: item[0]))

    def search(self, dst: str) -> Path:
        """
        在路由表中查询到达目的应用层的路径。

        Args:
            dst: 目的应用层端口号。

        Returns:
            到达目的地的本地物理层出口。如果没找到，就返回""。
        """
        # 传入的端口号必须为5位。
        try:
            assert len(dst) == 5
        except AssertionError:
            return ""

        # 反映射查找路径。
        try:
            dst_router = list(
                filter(
                    lambda router: int(dst[1]) % Topology.ROUTER_NUM == int(router),
                    self._table.keys(),
                )
            )[0]
        except IndexError:
            return ""

        # 如果目的下属于自己。
        if dst_router == self._device_id:
            return ""

        # 当且仅当目的地属于别的路由器，才返回出口值。
        else:
            return self._table[dst_router].exit


class RouterLayer(RouterTable, AbstractLayer):
    """路由器网络层。

    实现了路由器网络层-路由器物理层的消息收发和select。
    """

    def __init__(self, device_id: str) -> None:
        """初始化路由器网络层。

        根据路由器设备号，初始化本层的套接字。

        Args:
            device_id: 该路由器的设备号。
        """
        # 初始化套接字。
        self._device_id = device_id
        self.__port, self.__phys = self.__get_router_map()
        AbstractLayer.__init__(self, self.__port)

        # 初始化路由表。
        RouterTable.__init__(self, device_id)
        self._cache: dict[str, TableCache] = {}
        self.broadcast_time = time()

    def __str__(self) -> str:
        """打印网络层信息。"""
        return f"[Device {self._device_id}] <Router Layer @{self.__port}>"

    def __get_router_map(self) -> tuple[str, list[str]]:
        """获取端口号。

        从配置文件内读取该路由器的网络层、物理层端口号。

        Returns:
            - [0] 网络层端口号。
            - [1] 物理层端口号列表。
        """
        config = get_device_map(self._device_id)
        try:
            ports = (config["net"], config["phy"])
        except KeyError:
            print(f"[Error] Device {self._device_id} layer absence")
            exit(-1)
        else:
            return ports

    @property
    def port(self) -> str:
        """将路由器网络层端口号设为只读。"""
        return self.__port

    def receive_from_phys(self) -> tuple[str, bool]:
        """
        接收来自路由器物理层的消息。

        Returns:
            - [0] 接收到的01字符串。
            - [1] 是否接收成功，成功为`True`，失败为`False`。
        """
        binary, _, success = self._receive()
        binary = bits_to_string(binary) if success else binary
        return binary, success

    def send_to_phy(self, binary: str, port: str) -> int:
        """向指定物理层发送消息。

        Args:
            binary: 要发的01字符串。
            port: 信息要送到的本地物理层端口。

        Returns:
            总共发送的字节数。
        """
        return self._send(string_to_bits(binary), port)

    def broadcast_to_routers(self, binary: str, port: str = None) -> str:
        """向所有路由器广播消息，除了指定的端口。

        指定的端口一般是发来消息的端口。

        Args:
            binary: 要发的01字符串。
            port: 指定的端口号。

        Returns:
            发送到的端口列表字符串。
        """
        target_phys = list(
            filter(
                lambda phy: phy != port and phy != "",
                [path.exit for path in self._table.values()],
            )
        )
        for phy in target_phys:
            _ = self._send(string_to_bits(binary), phy)
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
        """打印路由表。"""
        print(RouterTable.__str__(self))

    def broadcast_table(self) -> None:
        """向所有路由器出口扩散自己的路由表。"""
        if time() - self.broadcast_time < Network.ROUTER_SPREAD_INTERVAL:
            return
        self.broadcast_time = time()

        table = self.pack()
        send_total = Frame.calc_frame_num(table)
        for i in range(send_total):
            seal_message = table[i * FramePack.DATA_LEN : (i + 1) * FramePack.DATA_LEN]
            send_frame = Frame()
            send_frame.write(
                {
                    "src": self.__port,
                    "seq": i,
                    "data": encode_text(seal_message),
                    "dst": Topology.BROADCAST_PORT,
                }
            )
            self.broadcast_to_routers(send_frame.binary)

    def receive_table(self, src: str, part: str) -> bool:
        """接收别的路由器扩散的路由表。"""
        src_device = src[1]

        # 如果该键之前没有记录，就为其创建默认值。
        if not self._cache.get(src_device, None):
            self._cache[src_device] = TableCache(string="", completed=False)

        # 如果该键之前被标记为接收完毕，则重新开始接收。
        if self._cache[src_device].completed:
            self._cache[src_device].string = ""
            self._cache[src_device].completed = False

        # 拼接本次接收的部分。
        self._cache[src_device].string += part

        # 如果路由表字符串完整了，就标记该键为接收完毕。
        if self._cache[src_device].string.endswith("$"):
            self._cache[src_device].completed = True

        # 返回是否所有键都接收完毕。
        return all([cache.completed for cache in self._cache.values()])

    def merge_all(self) -> None:
        while self.next_merge != "":
            self.merge(self._cache[self.next_merge].string)
