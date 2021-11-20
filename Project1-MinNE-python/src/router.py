import sys

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
    router = RouterLayer()
