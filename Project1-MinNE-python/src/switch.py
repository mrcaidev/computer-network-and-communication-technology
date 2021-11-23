import sys

from layer import SwitchLayer
from utils import *

if __name__ == "__main__":
    # 创建交换机网络层。
    switch = SwitchLayer(sys.argv[1])

    # 开始运作。
    while True:
        # 如果没有消息到达，就继续select。
        if not switch.has_message():
            continue

        # 读取消息。
        binary, in_port, _ = switch.receive_from_phy()
        frame = Frame()
        frame.read(binary)

        # 刷新端口地址表。
        if switch.refresh(local=in_port, remote=frame.src):
            switch.print_table()

        # 查找应该从哪个端口送出。
        out_ports = switch.search_locals(frame.dst)

        # 如果查出是单播，就直接向端口发送。
        if len(out_ports) == 1:
            out_port = out_ports[0]
            print(f"{frame.src} - {in_port} - {out_port} - {frame.dst}")
            switch.send_to_phy(binary, out_port)

        # 如果没查到或者是广播，就向所有端口发送。
        else:
            print(f"{frame.src} - {in_port} - [", end=" ")
            for port in filter(lambda port: port != in_port, switch.phy):
                switch.send_to_phy(binary, port)
                print(f"{port}", end=" ")
            print(f"] - {frame.dst}")
