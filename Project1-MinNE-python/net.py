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

    # 变量提前声明。
    seq = 0

    while True:
        mode = net.receive_from_app()

        if mode == const.QUIT:
            break

        elif mode == const.RECV:
            i, recv_total, src, message = 0, 0, const.BROADCAST_PORT, ""
            while True:
                if i == 0:
                    new_message, success = net.receive_from_phy(const.USER_TIMEOUT)
                else:
                    new_message, success = net.receive_from_phy()

                if not success:
                    print(f"[Frame {seq + 1}] Timeout.")
                    nak = Frame()
                    nak.write(app_port, seq + 1, encode(const.NAK), src)
                    net.send_to_phy(nak.binary)
                    continue

                recv_frame = Frame()
                recv_frame.read(new_message)
                print(f"new_message:{new_message}")
                print(f"recv_frame.binary:{recv_frame.binary}")

                if recv_frame.dst not in (app_port, const.BROADCAST_PORT):
                    print(f"I'm not {recv_frame.dst}.")
                    continue

                if seq == recv_frame.seq:
                    print(f"[Frame {seq}] Repeated.")
                    ack = Frame()
                    ack.write(app_port, seq, encode(const.ACK), src)
                    net.send_to_phy(ack.binary)
                    continue

                if not recv_frame.verified:
                    print(f"[Frame {seq + 1}] Invalid.")
                    nak = Frame()
                    nak.write(app_port, seq + 1, encode(const.NAK), src)
                    net.send_to_phy(nak.binary)
                    continue

                seq = recv_frame.seq
                if i == 0:
                    recv_total = int(decode(recv_frame.data))
                    print(f"[Frame {seq}] Receiving {recv_total} frames.")
                else:
                    message += recv_frame.data
                    print(f"[Frame {seq}] Verified.")

                ack = Frame()
                ack.write(app_port, seq, encode(const.ACK), src)
                net.send_to_phy(ack.binary)
                i += 1

                if i == recv_total + 1:
                    break

            net.send_to_app(message)

        else:
            if mode == const.UNICAST:
                dst = net.receive_from_app()
                print(f"Unicasting to port {dst}.")
            else:
                dst = const.BROADCAST_PORT
                print("Broadcasting...")

            message = net.receive_from_app()
            send_total = Frame.calc_frame_num(message)

            seq = (seq + 1) % 256
            request = Frame()
            request.write(app_port, seq, encode(str(send_total)), dst)
            packages = [request]

            for i in range(send_total):
                send_message = message[i * const.DATA_LEN : (i + 1) * const.DATA_LEN]
                seq = (seq + 1) % 256
                ready = Frame()
                ready.write(app_port, seq, send_message, dst)
                packages.append(ready)

            frame = 0
            while True:
                print(f"send binary:{packages[frame].binary}")
                net.send_to_phy(packages[frame].binary)
                if frame == 0:
                    print(
                        f"[Frame {packages[frame].seq}] Sending {send_total} frame(s)."
                    )
                else:
                    print(f"[Frame {packages[frame].seq}] Sent.")

                target_num = 1 if mode == const.UNICAST else const.BROADCAST_RECVER_NUM
                ackTimes = 0
                for target in range(target_num):
                    resp_binary, success = net.receive_from_phy()
                    if not success:
                        print(f"[Frame {packages[frame].seq}] Timeout.")
                        break

                    response = Frame()
                    response.read(resp_binary)
                    resp_message = decode(response.data)
                    if resp_message == const.ACK:
                        print(f"[Frame {response.seq}] ACK.")
                        ackTimes += 1
                    elif resp_message == const.NAK:
                        print(f"[Frame {response.seq}] NAK.")
                    else:
                        print(f"[Frame {response.seq}] Unknown response.")

                if ackTimes == target_num:
                    frame += 1
                if frame > send_total:
                    break

            del packages

        print("-" * 50)
