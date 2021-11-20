from collections import namedtuple
from json import load


class RouterTable(dict):
    Path = namedtuple("Path", ["next", "exit", "cost"])

    def __init__(self) -> None:
        """初始化内部字典。"""
        return super().__init__()

    def __str__(self) -> str:
        """打印路由表。"""
        head = """------------------------------------------------
| Destination | Next router | Exit port | Cost |
|-------------|-------------|-----------|------|"""
        body = "\n".join(
            [
                f"|{dst.center(13)}|{next.center(13)}|{exit.center(11)}|{str(cost).center(6)}|"
                for dst, (next, exit, cost) in self.items()
            ]
        )
        return f"{head}\n{body}\n{'-' * 48}"

    def initialize(self, initializer: dict[str, list[str, str, int]]) -> None:
        """
        初始化路由表。

        Args:
            initializer: 用于初始化的字典，键值对格式如下：
            - 键：目的应用层端口号。
            - 值：一个三元列表。
                - [0] 下一跳的路由器网络层端口号。
                - [1] 为了到达下一跳，应该从哪个本地物理层端口送出。
                - [2] 到达这个目的应用层的费用。
        """
        for dst, [next, exit, cost] in initializer.items():
            self[dst] = RouterTable.Path(next=next, exit=exit, cost=cost)

    def pack(self) -> str:
        """
        将路由表打包成字符串。

        Returns:
            一个字符串，格式为|目的端口:费用|目的端口:费用|...|
        """
        return "|".join([f"{dst}:{cost}" for dst, (_, _, cost) in self.items()])

    def unpack(
        self, src_router: str, in_port: str, string: str
    ) -> dict[str, tuple[str, str, int]]:
        """
        将字符串解包为路由表。

        Args:
            src_router: 发来这份路由表的路由器网络层端口号。
            in_port: 接收到这份路由表的本地物理层端口号。
            string: 要解包的字符串。

        Returns:
            解包所得的路由表。
        """
        unpacked_table = {}

        # 逐条解析为Path元组。
        for his_path in string.split("|"):
            dst, his_cost = his_path.split(":")
            unpacked_table[dst] = RouterTable.Path(
                next=src_router, exit=in_port, cost=int(his_cost) + 1
            )
        return unpacked_table

    def update(self, path_info: dict[str, tuple[str, str, int]]) -> bool:
        """
        更新路由表。

        Args:
            info: 一条路径的信息，键值对格式如下：
            - 键：目的应用层端口号。
            - 值：一个三元元组。
                - [0] 下一跳的路由器网络层端口号。
                - [1] 为了到达下一跳，应该从哪个本地物理层端口送出。
                - [2] 到达这个目的应用层的费用。

        Returns:
            是否有更新，有更新为True，无更新为False。
        """
        updated = False
        # 解包传入的字典。
        for dst, new_path in path_info.items():
            # 查找路由表内，这个目的应用层的已有路径。
            old_path, recorded = self.search(dst)

            # 如果路由表还没记录到这个应用层的路径，或者记录的路径费用较高，就更新路径。
            if not recorded or new_path.cost < old_path.cost:
                self[dst] = new_path
                updated = True

        return updated

    def search(self, dst: str) -> tuple[tuple[str, str, int], bool]:
        """
        在路由表中查找路径。

        Args:
            目的应用层端口号。

        Returns:
            一个二元元组。
            - [0] Path三元元组，包含到达目的应用层的路径信息。
            - [1] 是否记录了该路径，有记录为True，无记录为False。
        """
        result = self.get(dst, None)
        return result, result != None


if __name__ == "__main__":
    table_17200 = RouterTable()
    table_18200 = RouterTable()
    with open(
        "./Project1-MinNE-python/src/utils/layer/router_initializer.json",
        "r",
        encoding="utf-8",
    ) as fr:
        dic = load(fr)
        table_17200.initialize(dic["17200"])
        table_18200.initialize(dic["18200"])
    print(table_17200)
    print(table_18200)
    package_17200 = table_17200.pack()
    print("Package sealed by 17200:")
    print(package_17200)
    package_18200 = table_17200.unpack("17200", "18101", package_17200)
    print("Package received by 18200:")
    print(package_18200)
    table_18200.update(package_18200)
    print(table_18200)
