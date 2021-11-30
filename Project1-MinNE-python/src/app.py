import sys

from layer import AppLayer
from utils import *

if __name__ == "__main__":
    # 解析参数。
    if len(sys.argv) != 2:
        print("[Error] Device ID expected")
        exit(-1)

    # 创建主机应用层。
    device_id = sys.argv[1]
    app = AppLayer(device_id)
    print(app)

    # 开始运作。
    while True:
        # 如果没有消息可读，就继续等待。
        if not app.readable:
            continue
        # 如果有消息可读，就接收消息。
        first_message, is_from_cmd = app.receive_all()

        # 如果消息来自控制台，说明本机成为发送端。
        if is_from_cmd:
            # 接收发送模式，并通知本机网络层。
            mode = first_message
            print(f"[Log] Current mode: {mode}")
            app.send_to_net(mode)
            # 接收目标端口，并通知本机网络层。
            dst = app.receive_from_cmd()
            print(f"[Log] Destination: {dst}")
            app.send_to_net(dst)
            # 接收消息类型，并通知本机网络层。
            send_msgtype = app.receive_from_cmd()
            print(f"[Log] Message type: {send_msgtype}")
            app.send_to_net(send_msgtype)
            # 接收消息内容，并通知本机网络层。
            send_message = app.receive_from_cmd()
            if send_msgtype == MessageType.TEXT:
                print(f"[Log] Text content: {send_message}")
                app.send_to_net(encode_unicode(send_message))
            else:
                print(f"[Log] File path: {send_message}")
                app.send_to_net(encode_file(send_message))

        # 如果消息来自本机网络层，说明本机成为接收端。
        else:
            # 接收消息类型和消息内容。
            recv_msgtype = first_message
            recv_message = app.receive_from_net()

            # 如果消息类型是文本。
            if recv_msgtype == MessageType.TEXT:
                text = decode_unicode(recv_message)
                print(f"[Log] Received text: {text}")

            # 如果消息类型是文件。
            else:
                # 如果解码失败。
                file, decoded = decode_file(recv_message)
                if not decoded:
                    print("[Warning] Decoding failed")
                    continue
                # 如果保存失败。
                filepath, saved = save_rsc(file)
                if not saved:
                    print("[Warning] Saving failed")
                else:
                    print(f"[Log] File Saved: {filepath}")
