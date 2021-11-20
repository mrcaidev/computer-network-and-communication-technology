import os
import sys
from json import load

from utils import *

if __name__ == "__main__":
    print("Router".center(30, "-"))

    # 确定端口。
    if len(sys.argv) == 2 + const.Topology.SWITCHER_PER_ROUTER:
        router_port = sys.argv[1]
        phy_ports = sys.argv[2:]
        print(f"Rtr port: {router_port}")
        print(f"Phy ports: {[int(port) for port in phy_ports]}")
    else:
        print(
            f"[Error] Expect {1 + const.Topology.SWITCHER_PER_ROUTER} arguments, got {len(sys.argv) - 1}."
        )
        exit(-1)

    # 创建路由器网络层。
    router = RouterLayer(router_port)

    # 读取配置，初始化路由表。
    with open(
        os.path.join(os.path.dirname(sys.path[0]), "config", "router_initializer.json"),
        mode="r",
        encoding="utf-8",
    ) as fr:
        router.initialize(load(fr)[router_port])

    # 开始运作。
    while True:
        # 如果没有消息到达，就继续select。
        if not router.has_message():
            continue
