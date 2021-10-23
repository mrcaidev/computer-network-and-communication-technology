/**
 * @name: app.cpp
 * @author: MrCai
 * @description: 网元应用层。
 */
#include <iostream>
#include <winsock2.h>
#include "include/param.h"
#include "include/socket.cpp"
#include "include/coding.cpp"
using namespace std;

int main(int argc, char *argv[]) {
    cout << "------------------APP------------------" << endl;

    // 初始化变量。
    unsigned short selfPort = 0;
    unsigned short lowerPort = 0;
    unsigned short dstPort = 0;
    int mode = 0;
    char buffer[MAX_BUFFER_SIZE];
    string selfMessage = "";
    string lowerMessage = "";
    int recvFrameNum = 0;

    // 初始化网络库与套接字。
    WSADATA wsaData = initWSA();
    CNTSocket sock(SOCK_DGRAM);
    sock.setSendTimeout(SEND_TIMEOUT);
    sock.setRecvTimeout(RECV_TIMEOUT);

    // 绑定本层与下层端口。
    cout << "APP port at: ";
    cin >> selfPort;
    sock.bindSelfPort(selfPort);
    cout << "NET port at: ";
    cin >> lowerPort;
    sock.bindLowerPort(lowerPort);

    /* --------------------初始化结束，下面开始持续收发-------------------- */

    while (true) {
        cout << "---------------------------------------" << endl;
        // 选择当前模式。
        cout << "Select mode: (0::Quit, 1::Recv, 2::Send)" << endl << ">>> ";
        cin >> mode;

        /* -----------------------按`0`退出程序------------------------ */
        if (mode == QUIT) {
            sock.sendToLower(to_string(mode));
            quit();

            /* ------------------按`1`进入接收模式---------------------- */
        } else if (mode == RECV_MODE) {
            // 通知下层正在接收。
            sock.sendToLower(to_string(mode));
            // 得知要收多少帧。
            cout << "Waiting...";
            sock.recvFromLower(buffer);
            recvFrameNum = atoi(buffer);
            // 逐帧接收。
            cout << "\rReceived: ";
            for (int i = 0; i < recvFrameNum; i++) {
                // 读取缓冲。
                sock.recvFromLower(buffer);
                lowerMessage = buffer;
                memset(buffer, 0, sizeof(buffer));
                // 解码并打印。
                selfMessage = decode(lowerMessage);
                cout << selfMessage;
                lowerMessage.clear();
                selfMessage.clear();
            }
            cout << endl;

            /* ------------------按`2`进入发送模式---------------------- */
        } else if (mode == SEND_MODE) {
            // 通知下层正在发送。
            sock.sendToLower(to_string(mode));
            // 目标端口。
            cout << "Destination port: ";
            cin >> dstPort;
            sock.sendToLower(to_string(dstPort));
            dstPort = 0;
            // 本层消息。
            cout << "Send: ";
            cin >> selfMessage;
            sock.sendToLower(encode(selfMessage));
            selfMessage.clear();

            /* ------------------按`3`进入广播模式---------------------- */
        } else if (mode == BROADCAST_MODE) {
            // TODO: 广播模式。

            /* ------------------其他选项会提示错误---------------------- */
        } else {
            cout << "Invalid mode <" << mode << ">!" << endl;
        }
    }
    quit();
}