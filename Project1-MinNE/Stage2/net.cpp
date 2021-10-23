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
#include "include/frame.cpp"
using namespace std;

int main(int argc, char *argv[]) {
    cout << "------------------NET------------------" << endl;

    // 初始化变量。
    unsigned short upperPort = 0;
    unsigned short selfPort = 0;
    unsigned short lowerPort = 0;
    unsigned short dstPort = 0;
    int mode = 0;
    int seq = 0;
    char buffer[MAX_BUFFER_SIZE];
    string upperMessage = "";
    string selfMessage = "";
    string frameMessage = "";

    // 初始化网络库与套接字。
    WSADATA wsaData = initWSA();
    CNTSocket sock(SOCK_DGRAM);
    sock.setSendTimeout(SEND_TIMEOUT);
    sock.setRecvTimeout(RECV_TIMEOUT);

    // 绑定上层、本层、下层端口。
    cout << "APP port at: ";
    cin >> upperPort;
    sock.bindUpperPort(upperPort);
    cout << "NET port at: ";
    cin >> selfPort;
    sock.bindSelfPort(selfPort);
    cout << "PHY port at: ";
    cin >> lowerPort;
    sock.bindLowerPort(lowerPort);

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
            // 目标端口。
            sock.recvFromUpper(buffer);
            dstPort = atoi(buffer);
            cout << "This message will be sent to port " << dstPort << "."
                 << endl;
            memset(buffer, 0, sizeof(buffer));
            // 消息。
            sock.recvFromUpper(buffer);
            upperMessage = buffer;
            cout << "Upper message: " << upperMessage << endl;
            memset(buffer, 0, sizeof(buffer));
            // 封装。
            int frameNum = calcFrameNum(upperMessage.length());
            for (int frame = 0; frame < frameNum; frame++) {
                if (frame == frameNum - 1) {
                    frameMessage = upperMessage;
                } else {
                    frameMessage = upperMessage.substr(0, DATA_LEN);
                    upperMessage = upperMessage.substr(DATA_LEN);
                }
                selfMessage += decToBin(upperPort, PORT_LEN);
                selfMessage += decToBin(seq, SEQ_LEN);
                selfMessage += frameMessage;
                selfMessage += decToBin(dstPort, PORT_LEN);
                // TODO: 校验码。
                selfMessage = LOCATOR + trans(selfMessage) + LOCATOR;
                cout << "Self message: " << selfMessage << endl;
                // sock.sendToLower(selfMessage);
                frameMessage.clear();
                selfMessage.clear();
                seq = (seq + 1) % 256;
            }
        } else {
            cout << "Invalid mode <" << mode << ">!" << endl;
        }
    }

    // 清理并退出程序。
    quit();
}
