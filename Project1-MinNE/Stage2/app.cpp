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

    // 等待事件。
    while (true) {
        cout << "---------------------------------------" << endl;
        // 选择收/发模式。
        cout << "Select mode: (0::Quit, 1::Recv, 2::Send)" << endl << ">>> ";
        cin >> mode;
        // 模式对应的事件。
        if (mode == QUIT) {
            sock.sendToLower(to_string(mode));
            quit();
        } else if (mode == RECV_MODE) {
            // 通知下层正在接收。
            sock.sendToLower(to_string(mode));
            // 获取二进制编码消息并解码。
            cout << "Waiting...";
            sock.recvFromLower(buffer);
            cout << "\rReceived: " << decode(buffer) << endl;
            memset(buffer, 0, sizeof(buffer));
        } else if (mode == SEND_MODE) {
            // 通知下层正在发送。
            sock.sendToLower(to_string(mode));
            // 目标端口。
            cout << "Destination port: ";
            cin >> dstPort;
            sock.sendToLower(to_string(dstPort));
            dstPort = 0;
            // 消息。
            cout << "Send: ";
            cin >> selfMessage;
            sock.sendToLower(encode(selfMessage));
            selfMessage.clear();
        } else {
            cout << "Invalid mode <" << mode << ">!" << endl;
        }
    }
    quit();
}