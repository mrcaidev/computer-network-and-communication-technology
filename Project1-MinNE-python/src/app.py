import sys

from utils import *

if __name__ == "__main__":
    print("App".center(30, "-"))

    # 确定端口。
    if len(sys.argv) == 3:
        app_port = sys.argv[1]
        print(f"App port: {app_port}")
        net_port = sys.argv[2]
        print(f"Net port: {net_port}")
    else:
        print("App port:")
        app_port = get_port_from_user()
        print("Net port:")
        net_port = get_port_from_user()

    # 创建应用层。
    app = AppLayer(app_port)
    app.bind_net(net_port)

    # 开始运作。
    while True:
        # 网元进入指定模式。
        mode = get_mode_from_user()
        app.send_to_net(mode)

        # 如果要退出程序，就跳出循环。
        if mode == const.Mode.QUIT:
            break

        # 如果要接收消息，就读取。
        elif mode == const.Mode.RECV:
            print("Waiting...")
            message = app.receive_from_net()
            print(f"\rReceived: {decode(message)}")
            continue

        # 如果要单播，就输入目的端口。
        elif mode == const.Mode.UNICAST:
            print("Input destination port:")
            app.send_to_net(get_port_from_user())

        # 如果要单播或广播，就发送。
        message = get_message_from_user()
        app.send_to_net(encode(message))
