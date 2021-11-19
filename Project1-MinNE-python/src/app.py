import sys

from utils import *

if __name__ == "__main__":
    print("App".center(30, "-"))

    # 确定端口。
    if len(sys.argv) == 3:
        app_port, net_port = sys.argv[1:]
        print(f"App port: {app_port}")
        print(f"Net port: {net_port}")
    else:
        print(f"[Error] Expect 2 arguments, got {len(sys.argv) - 1}.")
        exit(-1)

    # 创建应用层。
    app = AppLayer(app_port)
    app.bind_net(net_port)

    # 开始运作。
    while True:
        # 网元进入指定模式。
        mode = app.receive_from_user(const.InputType.MODE)
        app.send_to_net(mode)

        # 如果要退出程序，就跳出循环。
        if mode == const.Mode.QUIT:
            break

        # 如果要接收消息，就读取后打印。
        elif mode == const.Mode.RECV:
            message = app.receive_from_net()
            app.send_to_user(f"Received: {decode(message)}")
            continue

        # 如果要单播，就输入目的端口。
        elif mode == const.Mode.UNICAST:
            destination = app.receive_from_user(const.InputType.PORT)
            app.send_to_net(destination)

        # 如果要单播或广播，就发送。
        message = app.receive_from_user(const.InputType.MESSAGE)
        app.send_to_net(encode(message))
