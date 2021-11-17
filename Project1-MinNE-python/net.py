import sys

from utils import *

if __name__ == "__main__":
    print("Net".center(50, "-"))

    # 固定端口。
    if len(sys.argv) == 4:
        app_port = sys.argv[1]
        net_port = sys.argv[2]
        phy_port = sys.argv[3]
        print(f"App port: {app_port}")
        print(f"Net port: {net_port}")
        print(f"Phy port: {phy_port}")
    else:
        app_port = input("App port: ")
        net_port = input("Net port: ")
        phy_port = input("Phy port: ")

    # 创建网络层。
    net = NetLayer(net_port)
    net.bind_app(app_port)
    net.bind_phy(phy_port)

    # 序号为全局变量。
    seq = 0
    ack = Frame()
    nak = Frame()

    while True:
        # 得知模式。
        mode = net.receive_from_app()

        # 退出程序。
        if mode == const.QUIT:
            break

        # 接收模式。
        elif mode == const.RECV:
            cur_frame_num, recv_total, src, message = 0, 0, const.BROADCAST_PORT, ""
            while True:
                # 从物理层接收消息，第一帧可以等得久一些。
                if cur_frame_num == 0:
                    new_message, success = net.receive_from_phy(const.USER_TIMEOUT)
                else:
                    new_message, success = net.receive_from_phy()

                # 如果超时，就什么都不做，重新开始等待。
                if not success:
                    print(f"[Frame {seq + 1}] Timeout.")
                    continue

                # 解析接收到的帧。
                recv_frame = Frame()
                recv_frame.read(new_message)

                # 如果帧不是给自己的，就什么都不做，重新开始等待。
                if recv_frame.dst not in (app_port, const.BROADCAST_PORT):
                    print(f"I'm not {recv_frame.dst}.")
                    continue

                # 如果序号重复，就丢弃这帧，再发一遍ACK。
                if seq == recv_frame.seq:
                    print(f"[Frame {seq}] Repeated.")
                    ack.write(app_port, seq, encode(const.ACK), src)
                    net.send_to_phy(ack.binary)
                    continue

                # 如果校验未通过，就丢弃这帧，发送NAK。
                if not recv_frame.verified:
                    print(f"[Frame {seq + 1}] Invalid.")
                    nak.write(app_port, seq + 1, encode(const.NAK), src)
                    net.send_to_phy(nak.binary)
                    continue

                # 如果帧信息正确，就接收这帧，发送ACK。
                seq = recv_frame.seq
                if cur_frame_num == 0:
                    recv_total = int(decode(recv_frame.data))
                    print(f"[Frame {seq}] Receiving {recv_total} frames.")
                else:
                    message += recv_frame.data
                    print(f"[Frame {seq}] Verified.")
                ack.write(app_port, seq, encode(const.ACK), src)
                net.send_to_phy(ack.binary)

                # 如果这是最后一帧，就退出循环。
                if cur_frame_num == recv_total:
                    break

                # 可以开始接收下一帧了。
                cur_frame_num += 1

            # 将消息传给应用层。
            net.send_to_app(message)

        # 发送模式。
        else:
            # 确定目的端口。
            if mode == const.UNICAST:
                dst = net.receive_from_app()
                print(f"Unicasting to port {dst}.")
            else:
                dst = const.BROADCAST_PORT
                print("Broadcasting...")

            # 确定消息。
            message = net.receive_from_app()
            send_total = Frame.calc_frame_num(message)

            # 第一帧是请求帧，告知对方总共发多少帧。
            seq = (seq + 1) % 256
            request = Frame()
            request.write(app_port, seq, encode(str(send_total)), dst)
            packages = [request]

            # 逐帧封装。
            for cur_frame_num in range(send_total):
                send_message = message[
                    cur_frame_num
                    * const.DATA_LEN : (cur_frame_num + 1)
                    * const.DATA_LEN
                ]
                seq = (seq + 1) % 256
                ready = Frame()
                ready.write(app_port, seq, send_message, dst)
                packages.append(ready)

            # 逐帧发送。
            cur_frame_num = 0
            timeout_cnt = 0
            while True:
                # 向物理层发送消息。
                net.send_to_phy(packages[cur_frame_num].binary)
                if cur_frame_num == 0:
                    print(
                        f"[Frame {packages[cur_frame_num].seq}] Sending {send_total} frame(s)."
                    )
                else:
                    print(f"[Frame {packages[cur_frame_num].seq}] Sent.")

                # 接收来自每个接收端的回复。
                dst_num = 1 if mode == const.UNICAST else const.BROADCAST_RECVER_NUM
                ack_cnt = 0
                for _ in range(dst_num):
                    resp_binary, success = net.receive_from_phy()
                    # 如果超时了，说明之后没有信息会发来了，直接跳出循环，同时超时次数+1。
                    if not success:
                        print(f"[Frame {packages[cur_frame_num].seq}] Timeout.")
                        timeout_cnt += 1
                        break

                    # 一旦有回复，就重置超时次数。
                    timeout_cnt = 0

                    # 解包读取回复，如果是ACK就记录下来。
                    resp_frame = Frame()
                    resp_frame.read(resp_binary)
                    resp_message = decode(resp_frame.data)
                    if resp_message == const.ACK:
                        print(f"[Frame {resp_frame.seq}] ACK.")
                        ack_cnt += 1
                    elif resp_message == const.NAK:
                        print(f"[Frame {resp_frame.seq}] NAK.")
                    else:
                        print(f"[Frame {resp_frame.seq}] Unknown response.")

                # 如果连续多次超时，就停止重传。
                if timeout_cnt == const.KEEPALIVE_CNT:
                    break

                # 如果每个接收端都ACK了，就可以发下一帧。
                if ack_cnt == dst_num:
                    cur_frame_num += 1

                # 如果这是发送的最后一帧，就跳出循环。
                if cur_frame_num > send_total:
                    break

            # 释放这些帧的空间。
            del packages
