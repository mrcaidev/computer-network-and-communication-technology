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
    // 初始化变量。
    cout << "------------------App------------------" << endl;
    int port = 0;
    int mode = 0;
    char buffer[MAX_BUFFER_SIZE];
    string message = "";

    // 初始化网络库与套接字。
    WSADATA wsaData = initWSA();
    CNTSocket sock(SOCK_DGRAM);
    sock.setSendTimeout(SEND_TIMEOUT);
    sock.setRecvTimeout(RECV_TIMEOUT);

    // 绑定本层与下层端口。
    cout << "APP port at: ";
    cin >> port;
    sock.bindSelfPort(port);
    cout << "NET port at: ";
    cin >> port;
    sock.bindLowerPort(port);

    // 等待事件。
    while (true) {
        cout << "---------------------------------------" << endl;
        // 选择收/发模式。
        cout << "Select mode: (0::Quit, 1::Recv, 2::Send)" << endl << ">>> ";
        cin >> mode;
        // 模式对应的事件。
        if (mode == QUIT) {
            return 0;
        } else if (mode == RECV_MODE) {
            cout << "Waiting...";
            int len = sock.recvFromLower(buffer);
            cout << "\rReceived: " << decode(buffer) << endl;
            memset(buffer, 0, sizeof(buffer));
        } else if (mode == SEND_MODE) {
            cout << "Send: ";
            cin >> message;
            sock.sendToLower(encode(message));
            message.clear();
        } else {
            cout << "Invalid option!" << endl;
        }
    }
}