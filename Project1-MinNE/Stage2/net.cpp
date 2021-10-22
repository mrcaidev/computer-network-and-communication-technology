/**
 * @name: net.cpp
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
    cout << "------------------NET------------------" << endl;

    // 初始化变量。
    int port = 0;
    int mode = 0;
    char buffer[MAX_BUFFER_SIZE];
    string message = "";

    // 初始化网络库与套接字。
    WSADATA wsaData = initWSA();
    CNTSocket sock(SOCK_DGRAM);
    sock.setSendTimeout(SEND_TIMEOUT);
    sock.setRecvTimeout(RECV_TIMEOUT);

    // 绑定上层、本层、下层端口。
    cout << "APP port at: ";
    cin >> port;
    sock.bindUpperPort(port);
    cout << "NET port at: ";
    cin >> port;
    sock.bindSelfPort(port);
    cout << "PHY port at: ";
    cin >> port;
    sock.bindLowerPort(port);

    // 等待事件。
    while (true) {
        cout << "---------------------------------------" << endl;
        // 上层告知当前模式。
        sock.recvFromUpper(buffer);
        mode = atoi(buffer);
        if (mode == QUIT) {
            quit();
        } else if (mode == RECV_MODE) {
            cout << "Waiting...";
            sock.recvFromLower(buffer);
            cout << "\rReceived: " << buffer << endl;
            // 提起
        } else if (mode == SEND_MODE) {
            // 发送模式。
        } else {
            cout << "Invalid mode <" << mode << ">!" << endl;
        }
    }

    // 清理并退出程序。
    quit();
}
