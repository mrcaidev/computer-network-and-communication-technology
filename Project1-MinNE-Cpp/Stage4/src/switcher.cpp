/**
 *  @file   switcher.cpp
 *  @author 蔡与望
 *  @brief  交换机网络层。
 */
#include "../include/cnt.h"
using namespace std;

int main(int argc, char const *argv[]) {
    cout << "----------SWITCHER-----------" << endl;
    // 提前声明本层会用到的变量。
    unsigned short switchPort, inPort, outPort, srcPort, dstPort;
    unsigned short phyPorts[HOST_PER_SWITCHER + 1] = {0};
    int recvBytes;
    char buffer[MAX_BUFFER_SIZE];
    // 确定端口，推荐通过命令行传参。
    if (argc == HOST_PER_SWITCHER + 3) {
        switchPort = atoi(argv[1]);
        cout << "Switcher Port: " << switchPort << endl;
        phyPorts[0] = atoi(argv[2]);
        cout << "PHY Port to router: " << phyPorts[0] << endl;
        for (int i = 1; i < HOST_PER_SWITCHER + 1; i++) {
            phyPorts[i] = atoi(argv[i + 2]);
            cout << "PHY Port to host " << i << " : " << phyPorts[i] << endl;
        }
    } else {
        cout << "Switcher Port: ";
        cin >> switchPort;
        cout << "PHY Port to router: ";
        cin >> phyPorts[0];
        for (int i = 1; i < HOST_PER_SWITCHER + 1; i++) {
            cout << "PHY Port to host " << i << ": ";
            cin >> phyPorts[i];
        }
    }
    // 初始化网络库与套接字。
    WSADATA wsaData = initWSA();
    SwitchSocket sock(switchPort);
    sock.bindPhys(phyPorts, sizeof(phyPorts) / sizeof(unsigned short));
    cout << "---------Initialized---------" << endl;

    // 轮流检查本地几个物理层端口有无消息。
    for (int i = 0;; i = (i + 1) % (HOST_PER_SWITCHER + 2)) {
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
        cout << "Port " << inPort << " has a message!" << endl;
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
            for (int i = 0; i < HOST_PER_SWITCHER + 1; i++) {
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
