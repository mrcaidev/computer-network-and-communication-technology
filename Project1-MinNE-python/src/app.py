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
            # 解析控制台传来的数据。
            data: dict = eval(first_message)
            if data["dst"] == Topology.BROADCAST_PORT:
                print("[Broadcast]", end=" ")
            else:
                print(f"[Unicast to {data['dst'][1]}]", end=" ")
            text = data.pop("text")
            file = data.pop("file")
            # 如果消息类型是文本。
            if data["msgtype"] == MessageType.TEXT:
                print(text)
                data["message"] = encode_unicode(text)
            # 如果消息类型是图片。
            else:
                print(file)
                data["message"] = encode_file(file)
            # 发送给本机网络层。
            app.send_to_net(str(data))

        # 如果消息来自本机网络层，说明本机成为接收端。
        else:
            # 解析本机网络层传来的数据。
            data: dict = eval(first_message)
            print(f"[Receive from {data['src'][1]}]", end=" ")
            # 如果消息类型是文本。
            if data["msgtype"] == MessageType.TEXT:
                text = decode_unicode(data["message"])
                print(text)
            # 如果消息类型是文件。
            else:
                # 如果解码失败。
                file, decoded = decode_file(data["message"])
                if not decoded:
                    print("[Warning] Decoding failed")
                    continue
                # 如果保存失败。
                filepath, saved = save_rsc(file)
                if not saved:
                    print("[Warning] Saving failed")
                else:
                    print(filepath)
