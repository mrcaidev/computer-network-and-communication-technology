from dataclasses import dataclass
from time import time

from utils.coding import bits_to_string, decode_ascii, encode_ascii, string_to_bits
from utils.frame import Frame
from utils.io import get_router_LAN, get_router_WAN
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

        Args:
            device_id: 该路由器的设备号。
        """
        self.__device_id = device_id
        self.__init_WAN()
        self._LAN = get_router_LAN(self.__device_id)

    def __str__(self) -> str:
        """打印路由表。"""
        head = f"{'-'*36}\n| Destination | Next | Exit | Cost |\n|{'-'*13}|{'-'*6}|{'-'*6}|{'-'*6}|"
        body = "\n".join(
            [
                f"|{dst.center(13)}|{path.next.center(6)}|{path.exit.center(6)}|{str(path.cost).center(6)}|"
                for dst, path in filter(
                    lambda item: item[0] != self.__device_id, self._WAN.items()
                )
            ]
        )
        return f"{head}\n{body}\n{'-'*36}"

    def __init_WAN(self) -> None:
        """初始化路由表周围环境。

        读取配置文件，记录下相邻的路由器设备号，以及到达它们的本地物理层端口号、费用。
        """
        self._WAN: dict[str, Path] = {}
        env = get_router_WAN(self.__device_id)

        # 到自己的费用始终为0。
        self._WAN[self.__device_id] = Path(next="", exit="", cost=0, optimized=True)

        # 依传入的字典逐项初始化。
        min_cost, min_dst = float("inf"), ""
        for dst, dic in env.items():
            # 记录到达周围路由器的路径。
            cur_cost = dic["cost"]
            self._WAN[dst] = Path(
                next=dst, exit=dic["exit"], cost=cur_cost, optimized=False
            )
            # 顺便找到费用最小值。
            if cur_cost < min_cost:
                min_cost = cur_cost
                min_dst = dst

        # 记录当前费用最低的路由器端口号。
        self._next_merge = min_dst

    @property
    def package(self) -> str:
        """打包路由表。

        将路由表中的下一跳与费用（除了到达自身的）打包为字符串。

        Returns:
            路由表包，格式为"device:dst-cost|dst-cost|...|dst-cost:$"。
        """
        return f"{self.__device_id}:{'|'.join(f'{dst}-{cost}' for dst, cost in filter(lambda item: item[0] != self.__device_id, [(dst, str(path.cost)) for dst, path in self._WAN.items()]))}:$"

    @staticmethod
    def __unpack(package: str) -> tuple[str, dict[str, int]]:
        """将路由表包解包为路由表。

        Args:
            package: 路由表包。

        Returns:
            - [0] 发来路由表包的设备号。
            - [1] 新路由表，键值对格式如下：
                - 键：目的路由器网络层端口号。
                - 值：到达该路由器的费用。
        """
        # 解包源设备号。
        src_device, body, _ = package.split(":")

        # 解包路径信息。
        table: dict[str, int] = {}
        for path in body.split("|"):
            dst, cost = path.split("-")
            table[dst] = int(cost)

        return src_device, table

    def merge(self, package: str) -> None:
        """合并外部路由表与本地路由表。

        采用`Dijkstra`算法更新本地路由表路径。

        Args:
            package: 发来的路由表包。
        """
        # 解包字符串为路由表。
        src_device, table = RouterTable.__unpack(package)

        # 标记到达该来源的路径为最优化。
        self._WAN[src_device].optimized = True

        # 创建本地路由表的一份浅拷贝。
        local_copy = self._WAN.copy()

        # 遍历更新本地路由表。
        min_cost, min_dst = float("inf"), ""
        for dst, new_cost in table.items():
            # 比对两表内，关于该目的地的数据。
            local_path = self._WAN.get(dst, None)
            new_path = Path(
                next=src_device,
                exit=self._WAN[src_device].exit,
                cost=new_cost + self._WAN[src_device].cost,
                optimized=False,
            )

            # 如果表里没有这条记录，就追加进表。
            if not local_path:
                self._WAN[dst] = new_path
                cur_cost = new_cost

            # 如果这条记录已经是最优化的，就跳过。
            elif local_path.optimized:
                continue

            # 如果本地记录费用低，就维持本地路径。
            elif local_path.cost < new_path.cost:
                cur_cost = local_path.cost

            # 如果新记录费用低，就更新路径。
            else:
                self._WAN[dst] = new_path
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
        self._next_merge = min_dst

        # 排序路由表。
        self._WAN = dict(sorted(self._WAN.items(), key=lambda item: item[0]))

    def static_merge(self) -> None:
        """静态合并路由表，与配置文件内的其它路由表合并。"""
        while self._next_merge:
            table = RouterTable(self._next_merge)
            self.merge(table.package)

    def search(self, dst: str) -> str:
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
            dst_router = min(
                filter(lambda nominee: nominee >= dst[1], self._WAN.keys())
            )

        # 如果找不到上级路由器。
        except Exception:
            return ""

        # 如果上级路由器是自己。
        if dst_router == self.__device_id:
            try:
                dst_exit = list(
                    filter(lambda item: item[0] == dst[1], self._LAN.items())
                )[0][1]

            # 如果找不到对应的本地物理层出口。
            except IndexError:
                return ""
            else:
                return dst_exit

        # 如果目的地不在子网内，就返回出口。
        else:
            return self._WAN[dst_router].exit


class RouterLayer(RouterTable, AbstractLayer):
    """路由器网络层。

    实现了路由器网络层-路由器物理层的消息收发和select。
    """

    def __init__(self, device_id: str) -> None:
        """初始化路由器网络层。

        Args:
            device_id: 该路由器的设备号。
        """
        # 初始化套接字。
        self.__device_id = device_id
        self.__port = f"1{device_id}200"
        AbstractLayer.__init__(self, self.__port)

        # 初始化路由表。
        RouterTable.__init__(self, device_id)
        self.__cache: dict[str, TableCache] = {}
        self.__broadcast_tick = time()

    def __str__(self) -> str:
        """打印网络层信息。"""
        return f"[Device {self.__device_id}] <Router Layer @{self.__port}>\n{'-'*30}"

    @property
    def port(self) -> str:
        """将路由器网络层端口号设为只读。"""
        return self.__port

    def receive_from_phys(self) -> tuple[str, str, bool]:
        """接收来自路由器物理层的消息。

        Returns:
            - [0] 接收到的01字符串。
            - [1] 发来该消息的本地物理层端口。
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

    def broadcast_to_LAN(self, binary: str, port: str = "") -> str:
        """向所有内网设备广播消息，除了指定的端口。

        用于多主机间的消息交换；指定的端口一般是当次收到消息的端口。

        Args:
            binary: 要发的01字符串。
            port: 可选，指定不发消息的端口号，默认为""。

        Returns:
            发送到的端口列表字符串。
        """
        target_phys = list(filter(lambda phy: phy != port, self._LAN.values()))
        for phy in target_phys:
            self.unicast_to_phy(binary, phy)
        return f"[{' '.join(target_phys)}]"

    def broadcast_to_WAN(self, binary: str, port: str = "") -> str:
        """向所有路由器广播消息，除了指定的端口。

        仅用于扩散路由表；指定的端口一般是当次收到路由表的端口。

        Args:
            binary: 要发的01字符串。
            port: 可选，指定不发消息的端口号，默认为""。

        Returns:
            发送到的端口列表字符串。
        """
        target_exits = list(
            filter(
                lambda exit: exit != port and exit != "",
                [path.exit for path in self._WAN.values()],
            )
        )
        for exit in target_exits:
            self.unicast_to_phy(binary, exit)
        return f"[{' '.join(target_exits)}]"

    def show_table(self) -> None:
        """打印路由表。"""
        print(RouterTable.__str__(self))

    def broadcast_table(self) -> None:
        """向所有路由器扩散自己的路由表。"""
        if time() - self.__broadcast_tick < Network.ROUTER_SPREAD_INTERVAL:
            return
        self.__broadcast_tick = time()

        table = self.package
        send_total = Frame.calc_frame_num(table)
        for i in range(send_total):
            seal_message = table[i * FramePack.DATA_LEN : (i + 1) * FramePack.DATA_LEN]
            send_frame = Frame()
            send_frame.write(
                {
                    "src": self.__port,
                    "seq": i,
                    "data": encode_ascii(seal_message),
                    "dst": Topology.BROADCAST_PORT,
                }
            )
            self.broadcast_to_WAN(send_frame.binary)

    def receive_table(self, src: str, binary: str) -> bool:
        """接收别的路由器扩散的路由表。

        Args:
            src: 源路由器设备号。
            binary: 本次发来的路由表部分的01字符串。

        Returns:
            是否全部接收完毕，是为`True`，不是为`False`。
        """
        # 预处理。
        src_device = src[1]
        part = decode_ascii(binary)

        # 如果该键之前没有记录，就为其创建默认值。
        if not self.__cache.get(src_device, None):
            self.__cache[src_device] = TableCache(string="", completed=False)

        # 如果该键之前被标记为接收完毕，则重新开始接收。
        if self.__cache[src_device].completed:
            self.__cache[src_device].string = ""
            self.__cache[src_device].completed = False

        # 拼接本次接收的部分。
        self.__cache[src_device].string += part

        # 如果路由表字符串完整了，就标记该键为接收完毕。
        if self.__cache[src_device].string.endswith("$"):
            self.__cache[src_device].completed = True

        # 返回是否所有键都接收完毕。
        return all([cache.completed for cache in self.__cache.values()])

    def dynamic_merge(self) -> None:
        """动态合并路由表，将缓存内的路由表包全部合并。"""
        while self._next_merge:
            self.merge(self.__cache[self._next_merge].string)
