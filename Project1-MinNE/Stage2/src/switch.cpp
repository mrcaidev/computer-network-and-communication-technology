/**
 *  @file   switch.cpp
 *  @author 蔡与望
 *  @brief  交换机网络层。
 */
#include <iostream>
#include <winsock2.h>
#include "../include/param.h"
#include "../include/coding.cpp"
#include "../include/frame.cpp"
#include "../include/socket.cpp"
using namespace std;

int main(int argc, char const *argv[]) {
    cout << "-----------SWITCH------------" << endl;
    // 确定端口。
    unsigned short switchPort = 0;
    cout << "SWITCH Port: ";
    cin >> switchPort;
    unsigned short hostPhyPorts[HOST_PER_SWITCHER] = {0};
    for (int i = 0; i < HOST_PER_SWITCHER; i++) {
        cout << "PHY Port to host " << i + 1 << ": ";
        cin >> hostPhyPorts[i];
    }
    unsigned short routePhyPort = 0;
    cout << "PHY Port to router: ";
    cin >> routePhyPort;
    // 初始化变量。
    // 初始化网络库与套接字。
    WSADATA wsaData = initWSA();
    SwitchSocket sock(switchPort);
    sock.bindPhys(routePhyPort, hostPhyPorts);

    cout << "---------Initialized---------" << endl;

    while (true) {
    }

    return 0;
}
