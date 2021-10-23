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
    unsigned short seq = 0;
    char buffer[MAX_BUFFER_SIZE];
    string upperMessage = "";
    string selfMessage = "";
    string lowerMessage = "";
    string thisMessage = "";
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
            sock.recvFromLowerAsBits(buffer);
            Frame reqFrame(buffer);
            recvFrameNum = binToDec(reqFrame.getData());
            sock.sendToUpper(to_string(recvFrameNum));
            cout << "\r";
            for (int frame = 0; frame < recvFrameNum; frame++) {
                // 下层消息。
                sock.recvFromLowerAsBits(buffer);
                lowerMessage = buffer;
                memset(buffer, 0, sizeof(buffer));
                // 提取信息。
                Frame thisFrame(lowerMessage);
                if (thisFrame.verifyChecksum()) {
                    sock.sendToUpper(thisFrame.getData());
                } else {
                    cout << "Verification failed!" << endl;
                }
                thisMessage.clear();
                selfMessage.clear();
                lowerMessage.clear();
            }

            /* ----------------------发送模式-------------------------- */
        } else if (mode == SEND_MODE) {
            // 目标端口。
            sock.recvFromUpper(buffer);
            dstPort = atoi(buffer);
            memset(buffer, 0, sizeof(buffer));
            // 上层消息。
            sock.recvFromUpper(buffer);
            upperMessage = buffer;
            memset(buffer, 0, sizeof(buffer));
            // 告知对方要发多少帧。
            sendFrameNum = Frame::calcNum(upperMessage.length());
            Frame reqFrame(upperPort, seq, decToBin(sendFrameNum, SEQ_LEN),
                           dstPort);
            selfMessage = reqFrame.stringify();
            sock.sendToLowerAsBits(selfMessage);
            cout << "\rFrame[" << seq << "] " << selfMessage << endl;
            selfMessage.clear();
            seq = (seq + 1) % 256;
            // 逐帧发送。
            for (int frame = 0; frame < sendFrameNum; frame++) {
                if (frame == sendFrameNum - 1) {
                    // 最后一帧，直接发送剩余信息。
                    thisMessage = upperMessage;
                } else {
                    // 不是最后一帧，取剩余信息的前一部分。
                    thisMessage = upperMessage.substr(0, DATA_LEN);
                    upperMessage = upperMessage.substr(DATA_LEN);
                }
                // 封装。
                Frame thisFrame(upperPort, seq, thisMessage, dstPort);
                selfMessage = thisFrame.stringify();
                // 打印并传输。
                cout << "\rFrame[" << seq << "] " << selfMessage << endl;
                sock.sendToLowerAsBits(selfMessage);
                // 清理并前进。
                thisMessage.clear();
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
