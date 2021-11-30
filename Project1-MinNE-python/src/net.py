import sys
from time import time

from layer import NetLayer
from utils import *

if __name__ == "__main__":
    # 解析参数。
    if len(sys.argv) != 2:
        print("[Error] Device ID expected")
        exit(-1)

    # 创建主机网络层。
    device_id = sys.argv[1]
    net = NetLayer(device_id)
    print(net)

    # 全局变量。
    ack = Frame()
    nak = Frame()
    recv_frame = Frame()
    resp_frame = Frame()

    # 开始运作。
    while True:
        # 如果没有消息可读，就继续等待。
        if not net.readable:
            continue
        # 如果有消息可读，就接收消息。
        first_message, is_from_app = net.receive_all()

        # 如果消息来自本机应用层，说明本机成为发送端。
        if is_from_app:
            # 接收发送模式。
            mode = first_message
            print(f"[Log] Current mode: {mode}")
            # 接收目标端口。
            dst = net.receive_from_app()
            print(f"[Log] Destination: {dst}")
            # 接收消息类型。
            send_msgtype = net.receive_from_app()
            print(f"[Log] Message type: {send_msgtype}")
            # 接收消息内容。
            send_message = net.receive_from_app()

            # 逐帧封装。
            send_frames = net.pack(msgtype=send_msgtype, message=send_message, dst=dst)
            send_total = len(send_frames) - 1
            print(f"[Log] Total: {send_total}")
            # 逐帧发送。
            cur_seq = keepalive_cnt = 0
            print(f"[Log] Start time: {eval(File.FULL_TIME)}")
            start_tick = time()
            while True:
                # 向物理层发送消息。
                net.send_to_phy(send_frames[cur_seq].binary)
                print(f"{send_frames[cur_seq]} | Sent")

                # 如果是单播，只有接收到ACK才发下一帧。
                if mode == Mode.UNICAST:
                    resend_flag = True
                    resp_binary, success = net.receive_from_phy()
                    # 如果超时，就累加1次超时次数。
                    if not success:
                        print("[Log] Timeout")
                        keepalive_cnt += 1
                    # 如果有回复。
                    else:
                        # 重置超时次数。
                        keepalive_cnt = 0
                        # 解包读取回复。
                        resp_frame.read(resp_binary)
                        resp_message = decode_ascii(resp_frame.data)
                        if resp_message == FramePack.ACK:
                            print(f"{resp_frame} | ACK")
                            resend_flag = False
                        elif resp_message == FramePack.NAK:
                            print(f"{resp_frame} | NAK")
                        else:
                            print(f"{resp_frame} | Garbled")

                # 如果是广播，只要至少有一次ACK就发下一帧，不检查ACK数量。
                else:
                    has_at_least_one_response = resend_flag = False
                    ack_cnt = nak_cnt = garble_cnt = 0
                    # 持续等待回复。
                    while True:
                        resp_binary, success = net.receive_from_phy()
                        # 如果没有回复，说明之后也没有信息会发来了。
                        # ! 这是一个潜在的bug，有可能回复因为延时没到达。
                        if not success:
                            # 如果一次回复都没收到，说明这帧超时，就累加1次超时次数。
                            if not has_at_least_one_response:
                                keepalive_cnt += 1
                                resend_flag = True
                            break
                        # 一旦有回复，就重置超时次数。
                        keepalive_cnt = 0
                        has_at_least_one_response = True
                        # 解包读取回复。
                        resp_frame.read(resp_binary)
                        resp_message = decode_ascii(resp_frame.data)
                        if resp_message == FramePack.ACK:
                            ack_cnt += 1
                        elif resp_message == FramePack.NAK:
                            nak_cnt += 1
                            resend_flag = True
                        else:
                            garble_cnt += 1
                            resend_flag = True
                    # 打印等待回复过程的信息。
                    if not has_at_least_one_response:
                        print("[Log] Timeout")
                    else:
                        print(f"{ack_cnt} ACK, {nak_cnt} NAK, {garble_cnt} garbled")

                # 如果连续多次超时，就停止重传。
                if keepalive_cnt == Network.KEEPALIVE_MAX_RETRY:
                    print("[Warning] Keepalive max retries")
                    break
                # 如果不必重传，就可以发送下一帧。
                if not resend_flag:
                    cur_seq += 1
                # 如果没有下一帧了，就跳出循环。
                if cur_seq == send_total + 1:
                    break

            # 释放这些帧的空间。
            del send_frames
            # 计算网速。
            print(f"[Log] Finish time: {eval(File.FULL_TIME)}")
            end_tick = time()
            speed = (
                Constant.BITS_PER_UNICODE * len(send_message) / (end_tick - start_tick)
            )
            print(f"[Log] Sending speed: {round(speed, 1)}bps")

        # 如果消息来自本机物理层，说明本机成为接收端。
        else:
            cur_seq, recv_total, keepalive_cnt = -1, 0, 0
            recv_msgtype = recv_message = ""
            is_first_recv = True
            start_tick = time()
            print(f"[Log] Start time: {eval(File.FULL_TIME)}")
            # 持续接收消息。
            while True:
                # 从物理层接收消息。
                if is_first_recv:
                    new_binary, success = first_message, True
                    is_first_recv = False
                else:
                    new_binary, success = net.receive_from_phy()

                # 如果超时，就累加1次超时次数。
                if not success:
                    keepalive_cnt += 1

                # 如果有消息。
                else:
                    # 重置超时次数。
                    keepalive_cnt = 0
                    # 解析接收到的帧。
                    recv_frame.read(new_binary)

                    # 如果帧不是给自己的，就什么都不做，重新开始等待。
                    if not net.should_receive(recv_frame.dst):
                        print(f"{recv_frame} | Not for me")
                        continue

                    # 如果序号重复，就丢弃这帧，再回复一遍ACK。
                    if cur_seq == recv_frame.seq:
                        print(f"{recv_frame} | Repeated")
                        ack = net.generate_ack(seq=recv_frame.seq, dst=recv_frame.src)
                        net.send_to_phy(ack)
                        continue

                    # 如果校验未通过，就丢弃这帧，回复NAK。
                    if not recv_frame.verified:
                        print(f"{recv_frame} | Invalid")
                        nak = net.generate_nak(seq=recv_frame.seq, dst=recv_frame.src)
                        net.send_to_phy(nak)
                        continue

                    # 如果帧信息正确，就接收这帧，回复ACK。
                    cur_seq = recv_frame.seq
                    if cur_seq == 0:
                        recv_total = bin_to_dec(
                            recv_frame.data[: FramePack.DATA_LEN // 2]
                        )
                        recv_msgtype = decode_ascii(
                            recv_frame.data[FramePack.DATA_LEN // 2 :]
                        )
                        print(f"[Log] Message type: {recv_msgtype}")
                        print(f"[Log] Total: {recv_total}")
                    else:
                        recv_message += recv_frame.data
                    print(f"{recv_frame} | Verified")
                    ack = net.generate_ack(seq=recv_frame.seq, dst=recv_frame.src)
                    net.send_to_phy(ack)

                # 如果超时次数达到Keepalive机制上限，就不再接收。
                if keepalive_cnt == Network.KEEPALIVE_MAX_RETRY:
                    print(f"[Warning] Keepalive max retries")
                    break
                # 如果没有下一帧了，就退出循环。
                if cur_seq == recv_total:
                    break

            # 如果什么都没收到，就继续开始等待双端消息。
            if not recv_message:
                continue

            # 如果接收到了消息，就将消息传给应用层。
            net.send_to_app(recv_msgtype)
            net.send_to_app(recv_message)

            # 计算网速。
            print(f"[Log] Finish time: {eval(File.FULL_TIME)}")
            end_tick = time()
            speed = (
                Constant.BITS_PER_UNICODE * len(recv_message) / (end_tick - start_tick)
            )
            print(f"[Log] Receiving speed: {round(speed, 1)}bps")
