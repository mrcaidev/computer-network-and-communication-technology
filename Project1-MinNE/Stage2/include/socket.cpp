/**
 *  @file   socket.cpp
 *  @brief  封装<winsock2.h>中的各类功能。
 *  @author 蔡与望
 */
#pragma once
#include <iostream>
#include <winsock2.h>
using namespace std;

/**
 *  @brief  初始化网络库与DLL。
 *  @return 存储网络库数据的结构。
 */
WSADATA initWSA() {
    WSADATA wsaData;
    int state = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (state != 0) {
        cout << "Error: WSAStartup() failed. (" << WSAGetLastError() << ")"
             << endl;
        exit(-1);
    }
    return wsaData;
}

/**
 *  @brief  清理网络库并退出。
 */
void quit() {
    WSACleanup();
    cout << "-------------END-------------" << endl;
    exit(0);
}

/**
 *  @brief  封装套接字的相关操作。
 */
class CNTSocket {
  private:
    SOCKET sock;
    SOCKADDR_IN addr;
    SOCKADDR_IN upperAddr;
    SOCKADDR_IN lowerAddr;

  public:
    CNTSocket(int type);
    ~CNTSocket();
    SOCKET getSocket();
    void setSendTimeout(int millisecond);
    void setRecvTimeout(int millisecond);
    void bindUpperPort(unsigned short port);
    void bindSelfPort(unsigned short port);
    void bindLowerPort(unsigned short port);
    int sendToUpper(string message);
    int sendToLower(string message);
    int sendToLowerAsBits(string message);
    int recvFromUpper(char *buffer);
    int recvFromLower(char *buffer);
    int recvFromLowerAsBits(char *buffer);
};

/**
 *  @brief  创建某一类型的套接字，类型为IPv4。
 *  @param  type    套接字类型
 *          （面向连接选SOCK_STREAM，面向无连接选SOCK_DGRAM）
 */
CNTSocket::CNTSocket(int type) {
    this->sock = socket(AF_INET, type, 0);
    if (this->sock == INVALID_SOCKET) {
        cout << "Error: socket() failed. (" << WSAGetLastError() << ")" << endl;
        exit(-1);
    }
}

/**
 *  @brief  关闭套接字。
 */
CNTSocket::~CNTSocket() { closesocket(this->sock); }

/**
 *  @brief  设置套接字发送超时。
 *  @param  millisecond 超时时间，单位是毫秒。
 */
void CNTSocket::setSendTimeout(int millisecond) {
    int state = setsockopt(this->sock, SOL_SOCKET, SO_SNDTIMEO,
                           (char *)&millisecond, sizeof(int));
    if (state == SOCKET_ERROR) {
        cout << "Error: setsockopt() failed. (" << WSAGetLastError() << ")"
             << endl;
        exit(-1);
    }
}

/**
 *  @brief  设置套接字接收超时。
 *  @param  millisecond 超时时间，单位是毫秒。
 */
void CNTSocket::setRecvTimeout(int millisecond) {
    int state = setsockopt(this->sock, SOL_SOCKET, SO_RCVTIMEO,
                           (char *)&millisecond, sizeof(int));
    if (state == SOCKET_ERROR) {
        cout << "Error: setsockopt() failed. (" << WSAGetLastError() << ")"
             << endl;
        exit(-1);
    }
}

/**
 *  @brief  绑定本层套接字与上层端口，上层地址默认为127.0.0.1。
 *  @param  port    上层端口号。
 */
void CNTSocket::bindUpperPort(unsigned short port) {
    this->upperAddr.sin_family = AF_INET;
    this->upperAddr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
    this->upperAddr.sin_port = htons(port);
}

/**
 *  @brief  绑定本层套接字与本层端口，本层地址默认为127.0.0.1。
 *  @param  port    本层端口号。
 */
void CNTSocket::bindSelfPort(unsigned short port) {
    this->addr.sin_family = AF_INET;
    this->addr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
    this->addr.sin_port = htons(port);
    // 只有这个绑定函数是真正意义上的绑定，其他两个的实质是在类内存储上下层地址。
    int state = bind(this->sock, (SOCKADDR *)&this->addr, sizeof(SOCKADDR));
    if (state == SOCKET_ERROR) {
        cout << "Error: bind() failed. (" << WSAGetLastError() << ")" << endl;
        exit(-1);
    }
}

/**
 *  @brief  绑定本层套接字与下层端口，下层地址默认为127.0.0.1。
 *  @param  port    下层端口号。
 */
void CNTSocket::bindLowerPort(unsigned short port) {
    this->lowerAddr.sin_family = AF_INET;
    this->lowerAddr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
    this->lowerAddr.sin_port = htons(port);
}

/**
 *  @brief  给上层发消息。
 *  @param  message 要传的字符串。
 */
int CNTSocket::sendToUpper(string message) {
    int sentBytes = sendto(this->sock, message.c_str(), message.length(), 0,
                           (SOCKADDR *)&this->upperAddr, sizeof(SOCKADDR));
    return sentBytes;
}

/**
 *  @brief  给下层发消息。
 *  @param  message 要传的字符串。
 */
int CNTSocket::sendToLower(string message) {
    int sentBytes = sendto(this->sock, message.c_str(), message.length(), 0,
                           (SOCKADDR *)&this->lowerAddr, sizeof(SOCKADDR));
    return sentBytes;
}

/**
 *  @brief  给下层以bits数组形式发消息。
 *  @param  message 要传的字符串。
 */
int CNTSocket::sendToLowerAsBits(string message) {
    // 将01字符串转化为01序列。
    char *bitsArr = new char[message.length()];
    for (int i = 0; i < message.length(); i++) {
        bitsArr[i] = message[i] - '0';
    }
    // 流量控制。
    Sleep(FLOW_INTERVAL);
    // 发送01序列。
    int sentBytes = sendto(this->sock, bitsArr, message.length(), 0,
                           (SOCKADDR *)&this->lowerAddr, sizeof(SOCKADDR));
    // 释放01序列空间。
    delete[] bitsArr;
    return sentBytes;
}

/**
 *  @brief  从上层收消息。
 *  @param  buffer  存放消息的缓存区。
 */
int CNTSocket::recvFromUpper(char *buffer) {
    int size = sizeof(SOCKADDR);
    int recvBytes = recvfrom(this->sock, buffer, MAX_BUFFER_SIZE, 0,
                             (SOCKADDR *)&this->upperAddr, &size);
    if (recvBytes != 0) {
        buffer[recvBytes] = '\0';
    }
    return recvBytes;
}

/**
 *  @brief  从下层收消息。
 *  @param  buffer  存放消息的缓存区。
 */
int CNTSocket::recvFromLower(char *buffer) {
    int size = sizeof(SOCKADDR);
    int recvBytes = recvfrom(this->sock, buffer, MAX_BUFFER_SIZE, 0,
                             (SOCKADDR *)&this->lowerAddr, &size);
    if (recvBytes != 0) {
        buffer[recvBytes] = '\0';
    }
    return recvBytes;
}

/**
 *  @brief  从下层以bits数组形式收消息。
 *  @param  buffer  存放消息的缓存区。
 */
int CNTSocket::recvFromLowerAsBits(char *buffer) {
    // 接收01序列。
    int size = sizeof(SOCKADDR);
    int recvBytes = recvfrom(this->sock, buffer, MAX_BUFFER_SIZE, 0,
                             (SOCKADDR *)&this->lowerAddr, &size);
    if (recvBytes != 0) {
        buffer[recvBytes] = '\0';
    }
    // 将01序列转换为01字符串。
    for (int i = 0; i < recvBytes; i++) {
        buffer[i] += '0';
    }
    return recvBytes;
}