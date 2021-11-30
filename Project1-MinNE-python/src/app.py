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
        # 持续等待，直到有消息可读。
        if not app.readable:
            continue
        first_message, is_from_cmd = app.receive_all()

        # 如果消息来自控制台，说明本机成为发送端。
        if is_from_cmd:
            send_data: dict = eval(first_message)
            # 将字典中的消息编码。
            text = send_data.pop("text")
            file = send_data.pop("file")
            if send_data["msgtype"] == MessageType.TEXT:
                print(f"[Send] {text}")
                send_data["message"] = encode_unicode(text)
            else:
                print(f"[Send] {file}")
                send_data["message"] = encode_file(file)
            # 发送给本机网络层。
            app.send_to_net(str(send_data))

        # 如果消息来自本机网络层，说明本机成为接收端。
        else:
            recv_data = eval(first_message)
            # 如果消息类型是文本。
            if recv_data["msgtype"] == MessageType.TEXT:
                text = decode_unicode(recv_data["message"])
                print(f"[Recv] {text}")
            # 如果消息类型是文件。
            else:
                # 如果解码失败。
                file, decoded = decode_file(recv_data["message"])
                if not decoded:
                    print("[Warning] Decoding failed")
                    continue
                # 如果保存失败。
                filepath, saved = save_rsc(file)
                if not saved:
                    print("[Warning] Saving failed")
                else:
                    print(f"[Recv] {filepath}")
