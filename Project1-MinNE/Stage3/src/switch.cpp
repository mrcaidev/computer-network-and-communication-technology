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
    unsigned short phyPorts[HOST_PER_SWITCHER + 1] = {0};
    if (argc == HOST_PER_SWITCHER + 3) {
        // 命令行传参。
        switchPort = atoi(argv[1]);
        cout << "SWITCH Port: " << switchPort << endl;
        for (int i = 0; i < HOST_PER_SWITCHER + 1; i++) {
            phyPorts[i] = atoi(argv[i + 2]);
            if (i == 0) {
                // 第一个给路由器。
                cout << "PHY Port to router: " << phyPorts[i] << endl;
            } else {
                // 剩下的给主机。
                cout << "PHY Port to host " << i << " : " << phyPorts[i]
                     << endl;
            }
        }
    } else {
        // 手动传参。
        cout << "SWITCH Port: ";
        cin >> switchPort;
        cout << "PHY Port to router: ";
        cin >> phyPorts[0];
        for (int i = 1; i <= HOST_PER_SWITCHER; i++) {
            cout << "PHY Port to host " << i << ": ";
            cin >> phyPorts[i];
        }
    }
    // 初始化变量。
    char buffer[MAX_BUFFER_SIZE];
    int recvBytes = 0;
    unsigned short inPort = 0;
    unsigned short outPort = 0;
    unsigned short srcPort = 0;
    unsigned short srcPortInTable = 0;
    unsigned short dstPort = 0;
    // 初始化网络库与套接字。
    WSADATA wsaData = initWSA();
    SwitchSocket sock(switchPort);
    sock.bindPhys(phyPorts);

    cout << "---------Initialized---------" << endl;

    // 轮流检查本地几个物理层端口有无消息。
    for (int i = 0;; i = (i + 1) % (HOST_PER_SWITCHER + 1)) {
        inPort = phyPorts[i];
        // 如果这个没有，就检查下一个。
        if (!sock.isReady(inPort)) {
            cout << "No message from port " << inPort << "." << endl;
            continue;
        }
        // 如果有，就读取消息。
        cout << "Port " << inPort << " has a message." << endl;
        recvBytes = sock.recvFromPhy(buffer, inPort, 1000);
        // ! 这是个莫名的bug：
        // 照理，程序走到了这里，说明这个端口是有东西读的；
        // 但是有时会什么都读不到。
        if (recvBytes <= 0) {
            continue;
        }
        // 获取信息的源与目的端口。
        Frame recvFrame(buffer);
        srcPort = recvFrame.getSrcPort();
        dstPort = recvFrame.getDstPort();
        cout << srcPort << " -> " << dstPort << " : "
             << decode(recvFrame.getData()) << endl;
        // 对输入端口的反向学习。
        srcPortInTable = sock.searchRemote(inPort);
        if (srcPortInTable != srcPort) {
            sock.updateTable(inPort, srcPort);
            cout << "Address table updated:" << endl;
            sock.printTable();
        }
        // 检索应该发到哪个本地端口。
        outPort = sock.searchLocal(dstPort);
        // 判断单播还是广播。
        if (dstPort == BROADCAST_PORT || outPort == 0) {
            // 如果发送端要求广播，或者地址表找不到这个远程端口，就向其他所有端口发送这条信息。
            for (int i = 0; i < HOST_PER_SWITCHER + 1; i++) {
                if (phyPorts[i] == inPort) {
                    continue;
                } else {
                    sock.sendToPhy(buffer, phyPorts[i]);
                    cout << "Send to port " << phyPorts[i] << "." << endl;
                }
            }
        } else {
            // 单播就直接发送。
            sock.sendToPhy(buffer, outPort);
            cout << "send" << endl;
        }
    }
    quit();
}
