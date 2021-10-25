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
    cout << "-------------NET-------------" << endl;
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
    unsigned short srcPort = 0;
    unsigned short dstPort = 0;
    int mode = 0;
    unsigned short seq = 0;
    char buffer[MAX_BUFFER_SIZE];
    string allMessage = "";
    string selfMessage = "";
    string thisMessage = "";
    string lastData = "";
    int sendTotal = 0;
    int recvTotal = 0;
    int recvBytes = 0;
    // 初始化网络库与套接字。
    WSADATA wsaData = initWSA();
    CNTSocket sock(SOCK_DGRAM);
    sock.bindUpperPort(appPort);
    sock.bindSelfPort(netPort);
    sock.bindLowerPort(phyPort);
    sock.setSendTimeout(USER_TIMEOUT);
    sock.setRecvTimeout(USER_TIMEOUT);

    cout << "---------Initialized---------" << endl;

    while (true) {
        /* ----------------------上层通知当前模式。----------------------- */
        sock.recvFromUpper(buffer, USER_TIMEOUT);
        mode = atoi(buffer);
        /* --------------------进入与应用层相同的模式。-------------------- */
        if (mode == RECV_MODE) {
            // 从对面那里得知要收多少帧。
            sock.recvFromLowerAsBits(buffer, USER_TIMEOUT);
            Frame request(buffer);
            recvTotal = binToDec(request.getData());
            srcPort = request.getSrcPort();
            cout << "[Frame " << request.getSeq() << "] Receiving " << recvTotal
                 << " frames in total." << endl;
            // 逐帧接收。
            for (int frame = 0; frame < recvTotal; frame++) {
                // 接收一帧。
                recvBytes = sock.recvFromLowerAsBits(buffer, RECV_TIMEOUT);
                // 如果超时没收到消息，回复NAK。
                if (recvBytes == 0) {
                    cout << "[Frame " << seq + 1 << "] Timeout." << endl;
                    Frame nak(appPort, seq + 1, encode(NAK), srcPort);
                    sock.sendToLowerAsBits(nak.stringify());
                    --frame;
                    continue;
                }
                // 解封。
                Frame recvFrame(buffer);
                // 如果发来的帧序号和数据都重复了，说明这帧是接收端收到了不明回复后重传的。
                // 回复ACK，但不接收这帧。
                // ! 这里有一个潜在的漏洞：
                // 如果这帧是对面重传的误帧，而且刚好数据错在同样的位置上，那么这里就会丢弃这一帧。
                // 造成的结果是，双端都以为这帧传对了，但其实接收端少收了这一帧。
                // 但出现这种情况的可能性很小，在此忽略不计。
                if (seq == recvFrame.getSeq() &&
                    lastData == recvFrame.getData()) {
                    cout << "[Frame " << seq << "] Repeated." << endl;
                    Frame ack(appPort, seq, encode(ACK), srcPort);
                    sock.sendToLowerAsBits(ack.stringify());
                    --frame;
                    continue;
                }
                // 如果没重复，那就更新序号。
                seq = recvFrame.getSeq();
                cout << "[Frame " << seq << "] ";
                // 验证并回复。
                if (recvFrame.isVerified()) {
                    // 拼接消息，回复ACK。
                    cout << "Verified. (" << decode(recvFrame.getData()) << ")"
                         << endl;
                    selfMessage += recvFrame.getData();
                    lastData = recvFrame.getData();
                    Frame ack(appPort, seq, encode(ACK), srcPort);
                    sock.sendToLowerAsBits(ack.stringify());
                } else {
                    // 回复NAK。
                    cout << "Invalid. (" << decode(recvFrame.getData()) << ")"
                         << endl;
                    Frame nak(appPort, seq, encode(NAK), srcPort);
                    sock.sendToLowerAsBits(nak.stringify());
                    --frame;
                }
            }
            // 通知上层接收完毕。
            sock.sendToUpper(selfMessage);

            cout << "-------Recv completed--------" << endl;

        } else if (mode == SEND_MODE) {
            // 目标端口。
            sock.recvFromUpper(buffer, USER_TIMEOUT);
            dstPort = atoi(buffer);
            cout << "Sending to port " << dstPort << "." << endl;
            // 要发的消息的所有位。
            sock.recvFromUpper(buffer, USER_TIMEOUT);
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
                // 接收对方的回复。
                recvBytes = sock.recvFromLowerAsBits(buffer, RECV_TIMEOUT);
                // 如果没收到回复，重传。
                if (recvBytes == 0) {
                    cout << "[Frame " << packages[frame].getSeq()
                         << "] Timeout." << endl;
                    --frame;
                    continue;
                }
                // 解封。
                Frame response(buffer);
                string responseMessage = decode(response.getData());
                if (responseMessage == ACK) {
                    // 如果是ACK，就打印成功信息。
                    cout << "[Frame " << packages[frame].getSeq() << "] ACK."
                         << endl;
                } else if (responseMessage == NAK) {
                    // 如果是NAK，就报错并重传。
                    cout << "[Frame " << packages[frame].getSeq() << "] NAK."
                         << endl;
                    --frame;
                } else {
                    // 如果是其他信息，说明对面的回复在传的时候也出错了，还是要重传这一帧。
                    cout << "[Frame " << packages[frame].getSeq()
                         << "] Unknown response." << endl;
                    --frame;
                }
            }
            // 全部发完，封装的帧可以丢弃。
            delete[] packages;

            cout << "-------Send completed-------" << endl;

        } else if (mode == BROADCAST_MODE) {
            // TODO: 广播模式。

            cout << "-----Broadcast completed-----" << endl;

        } else if (mode == QUIT) {
            quit();
        }
    }
}
