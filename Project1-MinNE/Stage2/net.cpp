/**
 * @name: net.cpp
 * @author: MrCai
 * @description: 网元网络层。
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
    string lowerMessage = "";
    string innerMessage = "";
    int sendFrameNum = 0;
    int recvFrameNum = 0;

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

    /* --------------------初始化结束，下面开始持续收发-------------------- */

    while (true) {
        cout << "---------------------------------------" << endl;
        // 上层告知当前模式。
        sock.recvFromUpper(buffer);
        mode = atoi(buffer);
        memset(buffer, 0, sizeof(buffer));

        /* --------------------------退出程序-------------------------- */
        if (mode == QUIT) {
            quit();

            /* ----------------------接收模式-------------------------- */
        } else if (mode == RECV_MODE) {
            cout << "Waiting...";
            // 知道要收多少帧，然后逐帧接收。
            sock.recvFromLower(buffer);
            recvFrameNum = atoi(buffer);
            sock.sendToUpper(to_string(recvFrameNum));
            for (int frame = 0; frame < recvFrameNum; frame++) {
                // 下层消息。
                sock.recvFromLower(buffer);
                lowerMessage = buffer;
                memset(buffer, 0, sizeof(buffer));
                // 提取信息。
                selfMessage = extractMessage(lowerMessage);
                if (verifyCRC(selfMessage)) {
                    innerMessage = readMessage(selfMessage);
                    sock.sendToUpper(innerMessage);
                } else {
                    // 要求重传。
                }
                innerMessage.clear();
                selfMessage.clear();
                lowerMessage.clear();
            }
            /* ----------------------发送模式-------------------------- */
        } else if (mode == SEND_MODE) {
            // 目标端口。
            sock.recvFromUpper(buffer);
            dstPort = atoi(buffer);
            cout << "This message will be sent to port " << dstPort << "."
                 << endl;
            memset(buffer, 0, sizeof(buffer));
            // 上层消息。
            sock.recvFromUpper(buffer);
            upperMessage = buffer;
            memset(buffer, 0, sizeof(buffer));
            // 告知对方要发多少帧，然后逐帧发送。
            sendFrameNum = calcSendFrameNum(upperMessage.length());
            sock.sendToLower(to_string(sendFrameNum));
            for (int frame = 0; frame < sendFrameNum; frame++) {
                if (frame == sendFrameNum - 1) {
                    // 最后一帧，直接发送剩余信息。
                    innerMessage = upperMessage;
                } else {
                    // 不是最后一帧，取剩余信息的前一部分。
                    innerMessage = upperMessage.substr(0, DATA_LEN);
                    upperMessage = upperMessage.substr(DATA_LEN);
                }
                // 封装。
                selfMessage += decToBin(upperPort, PORT_LEN);
                selfMessage += decToBin(seq, SEQ_LEN);
                selfMessage += innerMessage;
                selfMessage += decToBin(dstPort, PORT_LEN);
                selfMessage += generateCRC(selfMessage);
                selfMessage = addLocator(selfMessage);
                // 打印并传输。
                cout << "Frame[" << seq << "]" << selfMessage << endl;
                sock.sendToLower(selfMessage);
                // 清理并前进。
                innerMessage.clear();
                selfMessage.clear();
                seq = (seq + 1) % 256;
            }
            upperMessage.clear();

            /* ----------------------广播模式-------------------------- */
        } else if (mode == BROADCAST_MODE) {
            // TODO: 广播模式。

            /* ------------------其他选项会提示错误---------------------- */
        } else {
            cout << "Invalid mode <" << mode << ">!" << endl;
        }
    }
    quit();
}
