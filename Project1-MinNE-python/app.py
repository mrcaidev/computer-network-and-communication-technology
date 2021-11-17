import sys

from utils import *


def show_options():
    """CLI界面。"""
    print("-----------------------------")
    print("|        Select mode        |")
    print("| 1::Receive     2::Unicast |")
    print("| 3::Broadcast   4::Quit    |")
    print("-----------------------------")


if __name__ == "__main__":
    print("App".center(50, "-"))

    # 固定端口。
    if len(sys.argv) == 3:
        app_port = sys.argv[1]
        net_port = sys.argv[2]
        print(f"App port: {app_port}")
        print(f"Net port: {net_port}")
    else:
        app_port = input("App port: ")
        net_port = input("Net port: ")

    # 创建应用层。
    app = AppLayer(app_port)
    app.bind_net(net_port)
    print("Initialized".center(50, "-"))

    while True:
        # 选择模式。
        show_options()
        mode = input(">>> ")
        if mode not in ("1", "2", "3", "4"):
            continue
        app.send(mode)

        # 如果要退出程序，就跳出循环。
        if mode == const.QUIT:
            break

        # 如果要接收消息，就读取。
        elif mode == const.RECV:
            print("Waiting...")
            message = app.receive(const.USER_TIMEOUT)
            print(f"\rReceived: {decode(message)}")
            continue

        # 如果要单播，就输入目的端口。
        elif mode == const.UNICAST:
            app.send(input("Destination port: "))

        # 如果要单播或广播，就发送。
        app.send(input("Message: "))
