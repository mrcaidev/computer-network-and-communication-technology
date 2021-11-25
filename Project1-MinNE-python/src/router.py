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

    # 开始运作。
    while True:
        # 如果没有消息到达，就继续select。
        if not router.has_message():
            continue

        # 读取消息。
        binary, _ = router.receive_from_phys()
        frame = Frame()
        frame.read(binary)

        # 如果帧目的地是自己，说明是别的路由器发来的路由表。
        if frame.dst == router.port:
            pass

        # 如果帧目的地不是自己，就寻找目的地所属的路由器。
        else:
            exit_port = router.search(frame.dst)
            if not exit_port:
                continue
            else:
                router.send_to_phy(binary, exit_port)
