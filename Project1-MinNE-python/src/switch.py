import sys

from layer import SwitchLayer
from utils import *

if __name__ == "__main__":
    # 解析参数。
    if len(sys.argv) != 2:
        print("[Error] Device ID expected.")
        exit(-1)

    # 创建交换机网络层。
    device_id = sys.argv[1]
    switch = SwitchLayer(device_id)
    print(switch)

    # 开始运作。
    frame = Frame()
    while True:
        # 持续等待，直到有消息可读。
        if not switch.readable:
            continue
        binary, in_port = switch.receive_from_phys()
        frame.read(binary)

        # 刷新端口地址表。
        if switch.update(local=in_port, remote=frame.src):
            switch.show_table()

        # 查找应该从哪个端口送出。
        out_ports = switch.search_locals(frame.dst)

        print(f"[Log] {frame.src}-{in_port}-", end="")
        # 如果查出是单播，就直接向端口发送。
        if len(out_ports) == 1:
            out_port = out_ports[0]
            switch.unicast_to_phy(binary, out_port)
            print(out_port, end="")

        # 如果没查到或者是广播，就向所有端口发送。
        else:
            print(switch.broadcast_to_phys(binary, in_port), end="")

        print(f"-{frame.dst}")
