from layer import CommandLayer
from utils import *

if __name__ == "__main__":
    # 创建控制台。
    cmd = CommandLayer()
    print(cmd)

    # 开始运作。
    while True:
        # 确定源设备。
        print("Send from device:")
        src = cmd.receive_from_user(InputType.PORT)

        # 确定发送模式，并通知源设备。
        print("Select mode: 1::Unicast  2::Broadcast")
        mode = cmd.receive_from_user(InputType.MODE)
        cmd.send_to_app(mode, src)

        # 确定目标设备，并通知源设备。
        if mode == Mode.UNICAST:
            print("Destination device:")
            dst = cmd.receive_from_user(InputType.PORT)
        else:
            dst = Topology.BROADCAST_PORT
        cmd.send_to_app(dst, src)

        # 确定消息类型，并通知源设备。
        print("Select message type: 1::Text  2::File")
        msgtype = cmd.receive_from_user(InputType.MSGTYPE)
        cmd.send_to_app(msgtype, src)

        # 确定消息内容，并通知源设备。
        if msgtype == MessageType.TEXT:
            print("Text content:")
            message = cmd.receive_from_user(InputType.TEXT)
        else:
            print("File name:")
            message = cmd.receive_from_user(InputType.FILE)
        cmd.send_to_app(message, src)
