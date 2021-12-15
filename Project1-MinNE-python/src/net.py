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

    recv_frame = Frame()
    resp_frame = Frame()

    # 开始运作。
    while True:
        # 持续等待，直到有消息可读。
        if not net.readable:
            continue
        first_message, is_from_app = net.receive_all()

        # 如果消息来自本机应用层，说明本机成为发送端。
        if is_from_app:
            # 逐帧封装。
            send_data: dict = eval(first_message)
            frame_pool = net.build_pool(send_data)
            send_total = len(frame_pool) - 1

            # 逐帧发送。
            send_cnt = keepalive_cnt = 0
            write_log(device_id, "Send start")
            start_tick = time()
            while True:
                # 向物理层发送消息。
                net.send_to_phy(frame_pool[send_cnt].binary)
                print(f"{frame_pool[send_cnt]} | Sent, ", end="")

                # 如果是单播，只有接收到 ACK 才发下一帧。
                if send_data["dst"] != Topology.BROADCAST_PORT:
                    resend_flag = True
                    resp_binary, success = net.receive_from_phy()
                    # 如果超时，就累加 1 次超时次数。
                    if not success:
                        keepalive_cnt += 1
                        print("Timeout")
                    # 如果有回复。
                    else:
                        # 重置超时次数。
                        keepalive_cnt = 0
                        # 解包读取回复。
                        is_ack = net.parse_reply(resp_binary)
                        if is_ack:
                            print("ACK")
                            resend_flag = False
                        else:
                            print("NAK")

                # 如果是广播，只要至少有一次 ACK 就发下一帧，不检查 ACK 数量。
                else:
                    has_at_least_one_response = resend_flag = False
                    ack_cnt = nak_cnt = 0
                    # 持续等待回复。
                    while True:
                        resp_binary, success = net.receive_from_phy()
                        # 如果没有回复，说明之后也没有信息会发来了。
                        # ! 这是一个潜在的bug，有可能回复因为延时没到达。
                        if not success:
                            # 如果一次回复都没收到，说明这帧超时，就累加 1 次超时次数。
                            if not has_at_least_one_response:
                                keepalive_cnt += 1
                                resend_flag = True
                            break

                        # 一旦有回复，就重置超时次数。
                        keepalive_cnt = 0
                        has_at_least_one_response = True
                        # 解包读取回复。
                        is_ack = net.parse_reply(resp_binary)
                        if is_ack:
                            ack_cnt += 1
                        else:
                            nak_cnt += 1
                            resend_flag = True
                    print(f"{ack_cnt} ACK, {nak_cnt} NAK")

                # 如果连续多次超时，就停止重传。
                if keepalive_cnt == Network.KEEPALIVE_MAX_RETRY:
                    print("[Warning] Keepalive max retries")
                    break
                # 如果不必重传，就可以发送下一帧。
                if not resend_flag:
                    send_cnt += 1
                # 如果没有下一帧了，就跳出循环。
                if send_cnt == send_total + 1:
                    break

            # 释放这些帧的空间。
            del frame_pool

            # 计算网速。
            end_tick = time()
            speed = 16 * len(send_data["message"]) / (end_tick - start_tick)
            write_log(device_id, f"Send finish: {round(speed, 1)}bps")

        # 如果消息来自本机物理层，说明本机成为接收端。
        else:
            cur_seq, keepalive_cnt = -1, 0
            recv_msgtype = recv_message = ""
            is_first_recv = True
            recv_finish = False
            # 持续接收消息。
            while True:
                # 从物理层接收消息。
                if is_first_recv:
                    recv_binary, success = first_message, True
                    is_first_recv = False
                else:
                    recv_binary, success = net.receive_from_phy()

                # 如果超时，就累加1次超时次数。
                if not success:
                    keepalive_cnt += 1

                # 如果有消息。
                else:
                    # 重置超时次数。
                    keepalive_cnt = 0
                    # 解析接收到的帧。
                    recv_frame = net.parse_message(recv_binary)

                    # 第一帧收到的必须有 REQ 标志，不然就不能接收。
                    if recv_binary == first_message:
                        try:
                            assert recv_frame.session_state in SessionState.REQ_LIST
                        except AssertionError:
                            is_first_recv = True
                            break
                        else:
                            start_tick = time()
                            write_log(device_id, "Recv start")

                    # 如果帧不是给自己的，就什么都不做，重新开始等待。
                    if not net.should_receive(recv_frame.dst):
                        print(f"{recv_frame} | Not for me")
                        continue

                    # 如果序号重复，就丢弃这帧，再回复一遍 ACK。
                    if cur_seq == recv_frame.seq:
                        print(f"{recv_frame} | Repeated")
                        ack = net.build_ack(dst=recv_frame.src)
                        net.send_to_phy(ack.binary)
                        continue

                    # 如果校验未通过，就丢弃这帧，回复 NAK。
                    if not recv_frame.verified:
                        print(f"{recv_frame} | Invalid")
                        nak = net.build_nak(dst=recv_frame.src)
                        net.send_to_phy(nak.binary)
                        continue

                    # 如果帧信息正确，就接收这帧，回复 ACK。
                    cur_seq = recv_frame.seq
                    if recv_frame.session_state == SessionState.REQ_TXT:
                        recv_msgtype = MessageType.TEXT
                    elif recv_frame.session_state == SessionState.REQ_IMG:
                        recv_msgtype = MessageType.FILE
                    elif recv_frame.session_state == SessionState.FIN:
                        recv_message += recv_frame.data
                        recv_finish = True
                    else:
                        recv_message += recv_frame.data

                    print(f"{recv_frame} | Verified")
                    ack = net.build_ack(dst=recv_frame.src)
                    net.send_to_phy(ack.binary)

                # 如果超时次数达到 Keepalive 机制上限，就不再接收。
                if keepalive_cnt == Network.KEEPALIVE_MAX_RETRY:
                    print(f"[Warning] Keepalive max retries")
                    break
                # 如果接收结束，就退出循环。
                if recv_finish:
                    break

            # 如果什么都没收到，就继续开始等待双端消息。
            if not recv_message:
                continue

            # 如果接收到了消息，就将消息传给应用层。
            net.send_to_app(
                str(
                    {
                        "msgtype": recv_msgtype,
                        "message": recv_message,
                        "src": recv_frame.src,
                    }
                )
            )

            # 计算网速。
            end_tick = time()
            speed = 16 * len(recv_message) / (end_tick - start_tick)
            write_log(device_id, f"Recv finish: {round(speed, 1)}bps")
