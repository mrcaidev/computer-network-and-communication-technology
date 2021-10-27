/**
 * @file    app.cpp
 * @author  蔡与望
 * @brief   主机应用层。
 */
#include <iostream>
#include <winsock2.h>
#include "../include/param.h"
#include "../include/coding.cpp"
#include "../include/socket.cpp"
using namespace std;

int main(int argc, char *argv[]) {
    cout << "-------------APP-------------" << endl;
    // 确定端口。
    unsigned short appPort = 0;
    cout << "APP Port: ";
    cin >> appPort;
    unsigned short netPort = 0;
    cout << "NET Port: ";
    cin >> netPort;
    // 初始化变量。
    unsigned short dstPort = 0;
    int mode = 0;
    char buffer[MAX_BUFFER_SIZE];
    string selfMessage = "";
    int recvTotal = 0;
    // 初始化网络库与套接字。
    WSADATA wsaData = initWSA();
    AppSocket sock(appPort);
    sock.bindNet(netPort);

    cout << "---------Initialized---------" << endl;

    while (true) {
        /* ------------------------选择当前模式。----------------------- */

        cout << "Select mode: (1::Recv, 2::Send, 3::Broadcast, 4::Quit)" << endl
             << ">>> ";
        cin >> mode;

        /* ----------------------按`1`进入接收模式。--------------------- */

        if (mode == RECV_MODE) {
            // 通知下层正在接收。
            cout << "Waiting...";
            sock.sendToNet(to_string(mode));
            // 接收消息。
            sock.recvFromNet(buffer, USER_TIMEOUT);
            cout << "\rReceived: " << decode(buffer) << endl;
            cout << "-------Recv completed--------" << endl;

            /* ------------------按`2`进入发送模式。--------------------- */

        } else if (mode == SEND_MODE) {
            // 通知下层正在发送。
            sock.sendToNet(to_string(mode));
            // 目标端口。
            cout << "Destination port: ";
            cin >> dstPort;
            sock.sendToNet(to_string(dstPort));
            // 要发的消息。
            cout << "Send: ";
            cin >> selfMessage;
            sock.sendToNet(encode(selfMessage));
            cout << "-------Send completed-------" << endl;

            /* ------------------按`3`进入广播模式。--------------------- */

        } else if (mode == BROADCAST_MODE) {
            // TODO: 广播模式。

            /* --------------------按`4`退出程序。----------------------- */

        } else if (mode == QUIT) {
            // 通知下层退出。
            sock.sendToNet(to_string(mode));
            quit();

            /* ------------------其他选项会提示错误。---------------------- */

        } else {
            cout << "Invalid mode [" << mode << "]." << endl;
        }
    }
}