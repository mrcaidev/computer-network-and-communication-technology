from dataclasses import dataclass
from json import loads


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


class RouterTable(dict[str, Path]):
    """
    路由表，内部是字典。

    - 键：目的路由器网络层端口号。
    - 值：到达目的路由器的最佳路径。
    """

    def __init__(self, port: str) -> None:
        """初始化路由表。"""
        super().__init__()
        self._port = port

    def __str__(self) -> str:
        """打印路由表。"""
        head = f"{'-'*46}\n| Destination | Next jump | Exit port | Cost |\n|{'-'*13}|{'-'*11}|{'-'*11}|{'-'*6}|"
        body = "\n".join(
            [
                f"|{dst.center(13)}|{path.next.center(11)}|{path.exit.center(11)}|{str(path.cost).center(6)}|"
                for dst, path in filter(
                    lambda item: item[0] != self._port, self.items()
                )
            ]
        )
        return f"{head}\n{body}\n{'-'*46}"

    def initialize(self, initializer: dict[str, dict]) -> str:
        """
        从JSON文件初始化路由表周围环境。

        Args:
            initializer: 用于初始化环境的字典，键值对格式如下：
            - 键：相邻路由器网络层端口号。
            - 值：一个字典，包括下列两个键：
                - exit: 要到达该路由器，要走哪个本地物理层端口。
                - cost: 到达该路由器的费用。

        Returns:
            首先应合并谁的路由表。
        """
        self[self._port] = Path(next="", exit="", cost=0, optimized=True)
        min_cost, min_dst = float("inf"), ""
        for dst, dic in initializer.items():
            cur_cost = dic["cost"]
            self[dst] = Path(next=dst, exit=dic["exit"], cost=cur_cost, optimized=False)
            if cur_cost < min_cost:
                min_cost = cur_cost
                min_dst = dst
        return min_dst

    def pack(self) -> str:
        """
        将路由表内的下一跳与费用打包成字符串。

        Returns:
            包含路由表信息的字符串，路径间以"|"分隔，路径内以":"分隔。
        """
        return "|".join(
            f"{dst}:{cost}"
            for dst, cost in filter(
                lambda item: item[0] != self._port,
                [(dst, str(path.cost)) for dst, path in self.items()],
            )
        )

    def unpack(string: str) -> dict[str, int]:
        """
        将字符串解包为路由表。

        Args:
            string: 包含路由表信息的字符串。

        Returns:
            一个字典，键值对格式如下：
            - 键：目的路由器网络层端口号。
            - 值：到达该路由器的费用。
        """
        new_table = {}
        for path in string.split("|"):
            dst, cost = path.split(":")
            new_table.update({dst: int(cost)})
        return new_table

    def merge(self, src: str, table: dict[str, int]) -> str:
        """
        合并外部路由表与本地路由表。

        Args:
            src: 外部路由表的来源。
            table: 发来的路由表。

        Returns:
            接下来合并谁的路由表。
        """
        # 标记到达该来源的路径为最优化。
        self[src].optimized = True

        # 创建本地路由表的一份拷贝。
        old_copy = self.copy()

        min_cost, min_dst = float("inf"), ""
        for dst, new_cost in table.items():
            # 比对两表内，关于该目的地的数据。
            old_path = self.get(dst, None)
            new_path = Path(
                next=src,
                exit=self[src].exit,
                cost=new_cost + self[src].cost,
                optimized=False,
            )

            # 如果表里没有这条记录，就追加进表。
            if old_path == None:
                self[dst] = new_path
                cur_cost = new_cost

            # 如果这条记录已经是最优化的，就跳过。
            elif old_path.optimized:
                continue

            # 如果本地记录费用低，就维持本地路径。
            elif old_path.cost < new_path.cost:
                cur_cost = old_path.cost

            # 如果新记录费用低，就更新路径。
            else:
                self[dst] = new_path
                cur_cost = new_cost

            # 更新当前非最优化路径集的费用最小值。
            if min_cost > cur_cost:
                min_cost = cur_cost
                min_dst = dst

            # 如果这条路径原来就有，就在拷贝中删掉这一条。
            if old_path != None:
                old_copy.pop(dst)

        # 检测还有哪些端口没被比较过最小值。
        remained = dict(filter(lambda item: not item[1].optimized, old_copy.items()))

        # 如果还有端口没被比较过，就将最小值与这些端口相比较。
        if remained != {}:
            min_item = min(remained.items(), key=lambda item: item[1].cost)
            if min_item[1].cost < min_cost:
                min_dst = min_item[0]

        # 返回最小值对应的端口。
        return min_dst


with open("config/router_env.json", "r", encoding="utf-8") as fr:
    router_env = loads(fr.read())

table_11200 = RouterTable("11200")
table_21200 = RouterTable("21200")
table_31200 = RouterTable("31200")
table_41200 = RouterTable("41200")
table_51200 = RouterTable("51200")

next_merge_router = table_11200.initialize(router_env["11200"])
print(table_11200)

table_21200.initialize(router_env["21200"])
package_21200 = table_21200.pack()
table_31200.initialize(router_env["31200"])
package_31200 = table_31200.pack()
table_41200.initialize(router_env["41200"])
package_41200 = table_41200.pack()
table_51200.initialize(router_env["51200"])
package_51200 = table_51200.pack()

while next_merge_router != "":
    next_merge_router = table_11200.merge(
        next_merge_router, RouterTable.unpack(eval(f"package_{next_merge_router}"))
    )
    print(table_11200)
