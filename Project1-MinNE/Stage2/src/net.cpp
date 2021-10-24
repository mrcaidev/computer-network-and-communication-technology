/**
 * @name: net.cpp
 * @author: MrCai
 * @description: 网元网络层。
 */
#include <iostream>
#include <winsock2.h>
#include "../include/param.h"
#include "../include/coding.cpp"
#include "../include/frame.cpp"
#include "../include/socket.cpp"
using namespace std;

int main(int argc, char *argv[]) {
    cout << "------------------NET------------------" << endl;
    // 确定端口。
    unsigned short appPort = 0;
    cout << "APP Port: ";
    cin >> appPort;
    unsigned short netPort = 0;
    cout << "NET Port: ";
    cin >> netPort;
    unsigned short phyPort = 0;
    cout << "PHY Port: ";
    cin >> phyPort;
    // 初始化变量。
    unsigned short dstPort = 0;
    int mode = 0;
    unsigned short seq = 0;
    char buffer[MAX_BUFFER_SIZE];
    string allMessage = "";
    string selfMessage = "";
    string thisMessage = "";
    int sendTotal = 0;
    int recvTotal = 0;
    int reRecvNum = 0;
    // 初始化网络库与套接字。
    WSADATA wsaData = initWSA();
    CNTSocket sock(SOCK_DGRAM);
    sock.bindUpperPort(appPort);
    sock.bindSelfPort(netPort);
    sock.bindLowerPort(phyPort);
    sock.setSendTimeout(SEND_TIMEOUT);
    sock.setRecvTimeout(RECV_TIMEOUT);

    cout << "---------------------------------------" << endl;

    while (true) {
        /* ----------------------上层通知当前模式。----------------------- */
        memset(buffer, 0, sizeof(buffer));
        sock.recvFromUpper(buffer);
        mode = atoi(buffer);
        /* --------------------进入与应用层相同的模式。-------------------- */
        if (mode == RECV_MODE) {
            // 从对面那里得知要收多少帧。
            memset(buffer, 0, sizeof(buffer));
            sock.recvFromLowerAsBits(buffer);
            Frame request(buffer);
            recvTotal = binToDec(request.getData());
            cout << "[Frame " << request.getSeq() << "] Receiving " << recvTotal
                 << " frames in total." << endl;
            // 逐帧接收。
            selfMessage.clear();
            reRecvNum = 0;
            for (int frame = 0; frame < recvTotal + reRecvNum; ++frame) {
                // 解封。
                memset(buffer, 0, sizeof(buffer));
                sock.recvFromLowerAsBits(buffer);
                // TODO: 如果超时没收到消息，要回复NAK。
                Frame recvFrame(buffer);
                seq = recvFrame.getSeq();
                cout << "[Frame " << seq << "] ";
                // 验证并回复。
                if (recvFrame.isVerified()) {
                    // 拼接消息，回复ACK。
                    cout << "Verified. (" << decode(recvFrame.getData()) << ")"
                         << endl;
                    selfMessage += recvFrame.getData();
                    Frame ack(appPort, seq, encode(ACK),
                              recvFrame.getSrcPort());
                    sock.sendToLowerAsBits(ack.stringify());
                } else {
                    // 回复NAK。
                    cout << "Invalid. (" << decode(recvFrame.getData()) << ")"
                         << endl;
                    reRecvNum++;
                    Frame nak(appPort, seq, encode(NAK),
                              recvFrame.getSrcPort());
                    sock.sendToLowerAsBits(nak.stringify());
                }
            }
            // 通知上层接收完毕。
            sock.sendToUpper(selfMessage);

            cout << "---------------------------------------" << endl;

        } else if (mode == SEND_MODE) {
            // 目标端口。
            memset(buffer, 0, sizeof(buffer));
            sock.recvFromUpper(buffer);
            dstPort = atoi(buffer);
            cout << "Sending to port " << dstPort << "." << endl;
            // 要发的消息的所有位。
            memset(buffer, 0, sizeof(buffer));
            sock.recvFromUpper(buffer);
            allMessage = buffer;
            // 计算并通知对方要发多少帧。
            seq = (seq + 1) % 256;
            sendTotal = Frame::calcTotal(allMessage.length());
            Frame request(appPort, seq, decToBin(sendTotal, SEQ_LEN), dstPort);
            sock.sendToLowerAsBits(request.stringify());
            cout << "[Frame " << seq << "] Sending " << sendTotal
                 << " frames in total." << endl;
            // 逐帧封装。
            Frame *packages = new Frame[sendTotal];
            for (int frame = 0; frame < sendTotal; ++frame) {
                seq = (seq + 1) % 256;
                if (frame == sendTotal - 1) {
                    // 最后一帧，直接取走所有剩余消息。
                    thisMessage = allMessage;
                } else {
                    // 不是最后一帧，取走剩余消息的前DATA_LEN位。
                    thisMessage = allMessage.substr(0, DATA_LEN);
                    allMessage = allMessage.substr(DATA_LEN);
                }
                // 把取出来的消息封装进帧。
                Frame readyFrame(appPort, seq, thisMessage, dstPort);
                packages[frame] = readyFrame;
            }
            // 所有消息封装完成，逐帧发送。
            for (int frame = 0; frame < sendTotal; ++frame) {
                selfMessage = packages[frame].stringify();
                // 发给对面。
                sock.sendToLowerAsBits(selfMessage);
                cout << "[Frame " << packages[frame].getSeq() << "] Sent."
                     << endl;
                // 处理对方的回复。
                memset(buffer, 0, sizeof(buffer));
                sock.recvFromLowerAsBits(buffer);
                // TODO: 如果没收到回复，也要重传。
                Frame response(buffer);
                string responseMessage = decode(response.getData());
                if (responseMessage == NAK) {
                    // 如果是NAK，就报错并重传。
                    cout << "[Frame " << packages[frame].getSeq() << "] NAK."
                         << endl;
                    --frame;
                } else if (responseMessage == ACK) {
                    // 如果是ACK，就打印成功信息。
                    cout << "[Frame " << packages[frame].getSeq() << "] ACK."
                         << endl;
                } else {
                    // 如果是其他信息，说明响应在传的时候也出错了。
                    // TODO: 要让对面重传一次响应吗？会不会变成套娃？
                    // 暂且认为无效响应均为ACK。
                    cout << "[Frame " << packages[frame].getSeq()
                         << "] Unknown response." << endl;
                }
            }
            // 全部发完，封装的帧可以丢弃。
            delete[] packages;

            cout << "---------------------------------------" << endl;

        } else if (mode == BROADCAST_MODE) {
            // TODO: 广播模式。

            cout << "---------------------------------------" << endl;

        } else if (mode == QUIT) {
            quit();
        }
    }
}
