import os
import sys

from layer import AppLayer
from utils import *

if __name__ == "__main__":
    # 创建应用层。
    app = AppLayer(sys.argv[1])

    # 开始运作。
    while True:
        # 网元进入指定模式。
        mode = app.receive_from_user(InputType.MODE)
        app.send_to_net(mode)

        # 如果要退出程序，就跳出循环。
        if mode == Mode.QUIT:
            break

        # 如果要接收消息，就读取后打印。
        elif mode == Mode.RECEIVE:
            # 接收消息类型和消息本体。
            msgtype = app.receive_from_net()
            message = app.receive_from_net()

            # 呈现字符串。
            if msgtype == MessageType.TEXT:
                text = decode_text(message)
                app.send_to_user(f"[Log] Received text: {text}")

            # 呈现文件。
            elif msgtype == MessageType.FILE:
                result = decode_file(message)
                if result == b"":
                    app.send_to_user("[Log] Failed to decode file.")
                else:
                    try:
                        with open(
                            os.path.join(app.rootdir, File.RSC_DIR, "received.png"),
                            mode="wb",
                        ) as fw:
                            fw.write(result)
                    except Exception:
                        app.send_to_user("[Warning] Received picture: Failed to save.")
                    else:
                        app.send_to_user(
                            "[Log] Received picture: Saved under /resource."
                        )
            continue

        # 如果要单播，就输入目的端口。
        elif mode == Mode.UNICAST:
            destination = app.receive_from_user(InputType.PORT)
            app.send_to_net(destination)

        # 询问消息类型。
        msgtype = app.receive_from_user(InputType.MSGTYPE)
        app.send_to_net(msgtype)

        # 如果要发送文本。
        if msgtype == MessageType.TEXT:
            text = app.receive_from_user(InputType.TEXT)
            app.send_to_net(encode_text(text))

        # 如果要发送图片。
        else:
            filepath = app.receive_from_user(InputType.FILE)
            app.send_to_net(encode_file(filepath))
