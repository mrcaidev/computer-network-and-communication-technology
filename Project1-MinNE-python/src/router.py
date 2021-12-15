import sys

from layer import RouterLayer
from utils import *

if __name__ == "__main__":
    # 解析参数。
    if len(sys.argv) != 2:
        print("[Error] Device ID expected")
        exit(-1)

    # 创建路由器网络层。
    device_id = sys.argv[1]
    router = RouterLayer(device_id)
    print(router)

    # 合并其它路由器的路由表。
    router.static_merge()
    router.show_table()

    # 开始运作。
    parser = FrameParser()
    while True:
        # 持续等待，直到有消息可读。
        if not router.readable:
            continue
        binary, in_port = router.receive_from_phys()
        frame = parser.parse(binary)

        print(f"[Log] {frame.src}-{in_port}-", end="")
        # 如果是局域网广播帧，就向局域网广播。
        if frame.dst == Topology.BROADCAST_PORT:
            print(router.broadcast_to_LAN(binary, in_port), end="")

        # 如果是单播帧。
        else:
            # 寻找本地物理层出口。
            exit_port = router.search(frame.dst)
            # 如果没找到，说明目的地没有上级路由器，或者不知道给哪个交换机。
            if not exit_port:
                print("Abandon")
                continue
            # 如果找到的和发来的是一个端口，就不用再发一遍了。
            elif exit_port == in_port:
                print("Abandon")
                continue
            # 如果找到了，就向其单播。
            else:
                print(exit_port, end="")
                router.unicast_to_phy(binary, exit_port)

        print(f"-{frame.dst}")
