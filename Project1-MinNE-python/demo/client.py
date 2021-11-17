from random import randint
from time import time

from utils import *

if __name__ == "__main__":
    print("Client".center(50, "-"))
    # 创建客户端。
    client = AppLayer(13200)
    client.bind_net(13100)

    # 进入20次收发。
    start = time()
    for iter in range(20):
        # 发送随机数。
        send_num = randint(1, 500)
        print(f"{iter+1}\tSend: {str(send_num).rjust(3)}", end="")
        client.send(str(send_num))
        # 判断是否有回传。
        ready_sockets = select_readable([client.socket])
        if client.socket in ready_sockets:
            recv_num = int(client.receive())
            print(f"\tRecv: {str(recv_num).rjust(3)}")
        else:
            print("\tTimeout.")

    # 打印程序运行信息。
    end = time()
    print("-" * 50)
    print(f"Cost {round(end-start, 1)} second(s).")
