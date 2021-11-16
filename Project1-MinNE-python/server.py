from random import randint

from utils import *

if __name__ == "__main__":
    print("Server".center(50, "-"))
    border = 100
    ret_cnt = 0

    # 创建服务器。
    server = AppLayer(13100)
    server.bind_net(13200)

    # 进入20次收发。
    for iter in range(20):
        # 接收与产生随机数。
        recv_num = int(server.receive())
        rand_num = randint(1, 500)
        print(
            f"{iter+1}\tRecv: {str(recv_num).rjust(3)}\tGenerated: {str(rand_num).rjust(3)}"
        )
        # 判断是否回传。
        if recv_num + rand_num > border:
            server.send(str(recv_num + rand_num))
            ret_cnt += 1

    # 打印程序运行信息。
    print("-" * 50)
    print(f"{ret_cnt} return(s), expecting {10-0.5*ret_cnt} seconds.")
