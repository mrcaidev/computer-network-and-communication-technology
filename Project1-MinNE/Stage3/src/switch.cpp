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
    char buffer[MAX_BUFFER_SIZE];
    unsigned short inputPort = 0;
    unsigned short outputPort = 0;
    unsigned short srcPort = 0;
    unsigned short dstPort = 0;
    // 初始化网络库与套接字。
    WSADATA wsaData = initWSA();
    SwitchSocket sock(switchPort);
    sock.bindPhys(routePhyPort, hostPhyPorts);

    cout << "---------Initialized---------" << endl;

    while (true) {
        // 检查本地几个物理层端口有无消息。
        inputPort = sock.selectReadyPort();
        // 如果没有，就再次检查。
        if (inputPort == 0) {
            continue;
        }
        // 如果有，就取走这些消息。
        sock.recvFromPhy(buffer, inputPort, RECV_TIMEOUT * 2);
        // 获取信息的源与目的端口。
        Frame recvFrame(buffer);
        srcPort = recvFrame.getSrcPort();
        dstPort = recvFrame.getDstPort();
        cout << srcPort << " -> " << dstPort << " : " << recvFrame.getData()
             << endl;
        // 对输入端口的反向学习。
        if (sock.searchRemote(inputPort) != srcPort) {
            sock.updateAddrTable(inputPort, srcPort);
            cout << "Address table updated:" << endl;
            sock.printAddrTable();
        }
        // 检索应该发到哪个本地端口。
        outputPort = sock.searchLocal(dstPort);
        // 判断单播还是广播。
        if (dstPort == BROADCAST_PORT || outputPort == 0) {
            // 如果发送端要求广播，或者地址表找不到这个远程端口，就向其他所有端口发送这条信息。
            sock.sendToPhy(buffer, routePhyPort);
            for (int i = 0; i < HOST_PER_SWITCHER; i++) {
                if (hostPhyPorts[i] == inputPort) {
                    continue;
                } else {
                    sock.sendToPhy(buffer, hostPhyPorts[i]);
                }
            }
        } else {
            // 单播就直接发送。
            sock.sendToPhy(buffer, outputPort);
        }
    }
    quit();
}
