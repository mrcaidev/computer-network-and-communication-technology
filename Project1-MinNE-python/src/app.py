import sys

from layer import AppLayer
from utils import *

if __name__ == "__main__":
    # 解析参数。
    if len(sys.argv) != 2:
        print("[Error] Device ID expected.")
        exit(-1)

    # 创建主机应用层。
    device_id = sys.argv[1]
    app = AppLayer(device_id)
    print(app)

    # 开始运作。
    while True:
        # 网元进入指定模式。
        mode = app.receive_from_user(InputType.MODE)
        app.send_to_net(mode)

        # 如果要退出程序。
        if mode == Mode.QUIT:
            break

        # 如果要接收消息。
        elif mode == Mode.RECEIVE:
            # 接收消息类型和消息本体。
            msgtype = app.receive_from_net()
            message = app.receive_from_net()
            # 如果收到的是文本。
            if msgtype == MessageType.TEXT:
                text = decode_text(message)
                print(f"[Log] Received text: {text}")
            # 如果收到的是文件。
            elif msgtype == MessageType.FILE:
                # 如果解码失败，就报错。
                file, decoded = decode_file(message)
                if not decoded:
                    print("[Warning] Failed to decode file.")
                    continue
                # 如果保存失败，就报错。
                saved = save_file(file)
                if not saved:
                    print("[Warning] Failed to save file.")
                else:
                    print(f"[Log] File Saved under {File.RSC_DIR}.")

        # 如果要发送消息。
        else:
            # 如果要单播，就要额外输入并发送目的端口。
            if mode == Mode.UNICAST:
                dst = app.receive_from_user(InputType.PORT)
                app.send_to_net(dst)
            # 发送消息类型。
            msgtype = app.receive_from_user(InputType.MSGTYPE)
            app.send_to_net(msgtype)
            # 如果发送的是文本。
            if msgtype == MessageType.TEXT:
                text = app.receive_from_user(InputType.TEXT)
                app.send_to_net(encode_text(text))
            # 如果发送的是图片。
            else:
                file = app.receive_from_user(InputType.FILE)
                app.send_to_net(encode_file(file))
