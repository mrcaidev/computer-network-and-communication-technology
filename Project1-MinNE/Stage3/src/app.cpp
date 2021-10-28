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
    // 确定端口，推荐通过命令行传参。
    unsigned short appPort = 0, netPort = 0;
    if (argc == 3) {
        appPort = atoi(argv[1]);
        netPort = atoi(argv[2]);
        cout << "APP Port: " << appPort << endl
             << "NET Port: " << netPort << endl;
    } else {
        cout << "APP Port: ";
        cin >> appPort;
        cout << "NET Port: ";
        cin >> netPort;
    }
    // 初始化变量。
    unsigned short dstPort = 0;
    int mode = 0;
    char buffer[MAX_BUFFER_SIZE];
    string message = "";
    // 初始化网络库与套接字。
    WSADATA wsaData = initWSA();
    AppSocket sock(appPort);
    sock.bindNet(netPort);
    cout << "---------Initialized---------" << endl;

    while (true) {
        /* -------------------------选择当前模式。---------------------- */
        cout << "Select mode: (1::Recv, 2::Unicast, 3::Broadcast, 4::Quit)"
             << endl
             << ">>> ";
        cin >> mode;

        /* ---------------------------接收模式。----------------------- */
        if (mode == RECV) {
            // 通知下层正在接收。
            sock.sendToNet(to_string(mode));
            cout << "Waiting...";
            // 接收消息。
            sock.recvFromNet(buffer, USER_TIMEOUT);
            cout << "\rReceived: " << decode(buffer) << endl;

            /* -----------------------发送模式。----------------------- */
        } else if (mode == UNICAST || mode == BROADCAST) {
            // 通知下层正在发送。
            sock.sendToNet(to_string(mode));
            // 如果是单播，还需要额外输入目标端口。
            if (mode == UNICAST) {
                cout << "Destination port: ";
                cin >> dstPort;
                sock.sendToNet(to_string(dstPort));
            }
            // 要发的消息。
            cout << "Send: ";
            cin >> message;
            sock.sendToNet(encode(message));

            /* -----------------------退出程序。----------------------- */
        } else if (mode == QUIT) {
            sock.sendToNet(to_string(mode));
            break;

            /* -------------------其他选项会提示错误。------------------- */
        } else {
            cout << "Invalid mode [" << mode << "]." << endl;
        }
        // 结束一轮后，画一条分割线。
        cout << "-----------------------------" << endl;
    }
    // 清理并退出。
    quit();
}