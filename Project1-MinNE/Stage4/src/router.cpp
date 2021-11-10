/**
 *  @file   route.cpp
 *  @author 蔡与望
 *  @brief  路由器网络层。
 */
#include "../include/cnt.h"
using namespace std;

int main(int argc, char const *argv[]) {
    cout << "-----------ROUTER------------" << endl;
    // 提前声明本层会用到的变量。
    unsigned short routePort, inPort, outPort, srcPort, dstPort;
    unsigned short phyPorts[SWITCHER_PER_ROUTER] = {0};
    int recvBytes;
    char buffer[MAX_BUFFER_SIZE];
    // 确定端口，推荐通过命令行传参。
    if (argc == SWITCHER_PER_ROUTER + 2) {
        routePort = atoi(argv[1]);
        cout << "Router Port: " << routePort << endl;
        for (int i = 0; i < SWITCHER_PER_ROUTER; i++) {
            phyPorts[i] = atoi(argv[i + 2]);
            cout << "PHY Port to switcher " << i + 1 << " : " << phyPorts[i]
                 << endl;
        }
    } else {
        cout << "Router Port: ";
        cin >> routePort;
        for (int i = 0; i < SWITCHER_PER_ROUTER; i++) {
            cout << "PHY Port to switcher " << i + 1 << ": ";
            cin >> phyPorts[i];
        }
    }
    // 初始化网络库与套接字。
    WSADATA wsaData = initWSA();
    SwitchSocket sock(routePort);
    sock.bindPhys(phyPorts, sizeof(phyPorts) / sizeof(unsigned short));
    cout << "---------Initialized---------" << endl;

    // 轮流检查本地几个物理层端口有无消息。
    for (int i = 0;; i = (i + 1) % (SWITCHER_PER_ROUTER + 1)) {
        inPort = phyPorts[i];
        // 如果这个没有，就检查下一个。
        if (!sock.isReady(inPort)) {
            continue;
        }
        // 如果有，就读取消息。
        recvBytes = sock.recvFromPhy(buffer, inPort, 1000);
        // ! 这是个莫名其妙的bug：
        // 照理，程序走到了这里，说明这个端口是有东西读的；
        // 但是有时会什么都读不到。
        if (recvBytes <= 0) {
            continue;
        }
        // 获取信息的源与目的端口。
        Frame recvFrame(buffer);
        srcPort = recvFrame.getSrcPort();
        dstPort = recvFrame.getDstPort();
        // 对输入端口的反向学习。
        if (!sock.hasRelation(srcPort, inPort)) {
            sock.updateTable(srcPort, inPort);
            cout << "Address table updated:" << endl;
            sock.printTable();
        }
        // 检索应该发到哪个本地端口。
        outPort = sock.searchLocal(dstPort);
        cout << srcPort << " -> " << inPort << " -> " << outPort << " -> "
             << dstPort << " : " << decode(recvFrame.getData()) << endl;
        // 判断单播还是广播。
        if (dstPort == BROADCAST_PORT || outPort == 0) {
            // 如果发送端要求广播，或者地址表找不到这个远程端口，就向其他所有端口发送这条信息。
            cout << "Broadcasting to port";
            for (int i = 0; i < SWITCHER_PER_ROUTER; i++) {
                if (phyPorts[i] == inPort) {
                    continue;
                } else {
                    sock.sendToPhy(buffer, phyPorts[i]);
                    cout << " " << phyPorts[i];
                }
            }
            cout << "." << endl;
        } else {
            // 单播就直接发送。
            sock.sendToPhy(buffer, outPort);
            cout << "Unicasting to port " << outPort << "." << endl;
        }
    }
    quit();
}
