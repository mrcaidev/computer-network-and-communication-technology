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
        mode = app.receive_from_user(InputType.MODE)
        app.send_to_net(mode)

        # 如果要退出程序，就跳出循环。
        if mode == Mode.QUIT:
            break

        # 如果要接收消息，就读取后打印。
        elif mode == Mode.RECV:
            # 接收消息类型。
            message_type = app.receive_from_net()

            # 接收消息本体。
            net_message = app.receive_from_net()

            # 呈现字符串。
            if message_type == MessageType.TEXT:
                string = decode_text(net_message)
                app.send_to_user(f"Received text: {string}")

            # 呈现图片。
            elif message_type == MessageType.FILENAME:
                decoded = decode_picture(net_message)
                if decoded:
                    app.send_to_user("Received picture: Saved in directory /img.")
                else:
                    app.send_to_user("[Warning] Received picture: Failed to decode.")
            continue

        # 如果要单播，就输入目的端口。
        elif mode == Mode.UNICAST:
            destination = app.receive_from_user(InputType.PORT)
            app.send_to_net(destination)

        # 询问消息类型。
        message_type = app.receive_from_user(InputType.MESSAGE_TYPE)
        app.send_to_net(message_type)

        # 如果要发送文本。
        if message_type == MessageType.TEXT:
            string = app.receive_from_user(InputType.TEXT)
            app.send_to_net(encode_text(string))

        # 如果要发送图片。
        else:
            filepath = app.receive_from_user(InputType.FILENAME)
            app.send_to_net(encode_picture(filepath))
