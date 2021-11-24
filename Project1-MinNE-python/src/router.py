import os
import sys
from json import load

from layer import RouterLayer
from utils import *

if __name__ == "__main__":
    # 解析参数。
    if len(sys.argv) != 2:
        print("[Error] Device ID expected.")
        exit(-1)

    # 创建路由器网络层。
    device_id = sys.argv[1]
    router = RouterLayer(device_id)
    print(router)

    # 初始化路由表。
    router.initialize(get_router_env(device_id))

    # 开始运作。
    while True:
        # 如果没有消息到达，就继续select。
        if not router.has_message():
            continue

        # 读取消息。
        binary, _ = router.receive_from_phy()
        frame = Frame()
        frame.read(binary)
