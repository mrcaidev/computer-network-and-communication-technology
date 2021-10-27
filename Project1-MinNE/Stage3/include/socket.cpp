/**
 *  @file   socket.cpp
 *  @brief  封装各类套接字。
 *  @author 蔡与望
 */
#pragma once
#include <iostream>
#include <map>
#include <winsock2.h>
#include "param.h"
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
 *  @brief  各种套接字的父类。
 */
class CNTSocket {
  protected:
    SOCKET sock;
    SOCKADDR_IN addr;

  public:
    CNTSocket();
    CNTSocket(unsigned short port);
    ~CNTSocket();
    SOCKET getSocket();

    void setSendTimeout(int millisecond);
    void setRecvTimeout(int millisecond);

    void bindSelf(unsigned short port);

    static SOCKADDR_IN getAddress(CNTSocket sock);
    static unsigned short getPort(CNTSocket sock);
};

/**
 *  @brief  主机应用层套接字。
 */
class AppSocket : public CNTSocket {
  protected:
    SOCKADDR_IN netAddr;

  public:
    AppSocket();
    AppSocket(unsigned short port);
    ~AppSocket();

    void bindNet(unsigned short port);
    int sendToNet(string message);
    int recvFromNet(char *buffer, int timeout);
};

/**
 *  @brief  主机网络层套接字。
 */
class NetSocket : public CNTSocket {
  protected:
    SOCKADDR_IN appAddr;
    SOCKADDR_IN phyAddr;

  public:
    NetSocket();
    NetSocket(unsigned short port);
    ~NetSocket();

    void bindApp(unsigned short port);
    int sendToApp(string message);
    int recvFromApp(char *buffer, int timeout);

    void bindPhy(unsigned short port);
    int sendToPhy(string message);
    int recvFromPhy(char *buffer, int timeout);
};

/**
 *  @brief  交换机网络层套接字。
 */
class SwitchSocket : public CNTSocket {
  protected:
    map<unsigned short, CNTSocket> phySocks;
    map<unsigned short, unsigned short> addrTable;

  public:
    SwitchSocket();
    SwitchSocket(unsigned short port);
    ~SwitchSocket();

    void bindPhys(unsigned short routePhyPort, unsigned short *hostPhyPorts);
    int sendToPhy(string message, unsigned short port);
    int recvFromPhy(char *buffer, unsigned short port, int timeout);

    unsigned short selectReadyPort();
    void printPhySocks();
    void printAddrTable();
};

/**
 *  @brief  创建无连接IPv4套接字。
 */
CNTSocket::CNTSocket() {
    this->sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (this->sock == INVALID_SOCKET) {
        cout << "Error: socket() failed. (" << WSAGetLastError() << ")" << endl;
        exit(-1);
    }
    memset(&this->addr, 0, sizeof(SOCKADDR_IN));
    this->setSendTimeout(USER_TIMEOUT);
    this->setRecvTimeout(USER_TIMEOUT);
}

/**
 *  @brief  创建无连接IPv4套接字，同时绑定其端口。
 */
CNTSocket::CNTSocket(unsigned short port) {
    this->sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (this->sock == INVALID_SOCKET) {
        cout << "Error: socket() failed. (" << WSAGetLastError() << ")" << endl;
        exit(-1);
    }
    this->bindSelf(port);
    this->setSendTimeout(USER_TIMEOUT);
    this->setRecvTimeout(USER_TIMEOUT);
}

/**
 *  @brief  销毁套接字。
 */
CNTSocket::~CNTSocket() { closesocket(this->sock); }

/**
 *  @brief  获取套接字。
 */
SOCKET CNTSocket::getSocket() { return this->sock; }

/**
 *  @brief  设置发送超时。
 *  @param  millisecond 超时时间，单位为毫秒。
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
 *  @brief  设置接收超时。
 *  @param  millisecond 超时时间，单位为毫秒。
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
 *  @brief  绑定本层套接字与本层端口。
 *  @param  port    本层端口号。
 */
void CNTSocket::bindSelf(unsigned short port) {
    this->addr.sin_family = AF_INET;
    this->addr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
    this->addr.sin_port = htons(port);
    int state = bind(this->sock, (SOCKADDR *)&this->addr, sizeof(SOCKADDR));
    if (state == SOCKET_ERROR) {
        cout << "Error: bind() failed. (" << WSAGetLastError() << ")" << endl;
        exit(-1);
    }
}

/**
 *  @brief  查询某套接字的地址。
 *  @param  sock    要查询的套接字。
 *  @retval 该套接字的地址。
 */
SOCKADDR_IN CNTSocket::getAddress(CNTSocket sock) {
    SOCKADDR_IN addr;
    int size = sizeof(SOCKADDR);
    getsockname(sock.getSocket(), (SOCKADDR *)&addr, &size);
    return addr;
}

/**
 *  @brief  查询某套接字的端口号。
 *  @param  sock    要查询的套接字。
 *  @retval 该套接字的端口号。
 */
unsigned short CNTSocket::getPort(CNTSocket sock) {
    SOCKADDR_IN addr = CNTSocket::getAddress(sock);
    unsigned short port = ntohs(addr.sin_port);
    return port;
}

/**
 *  @brief  创建应用层套接字。
 */
AppSocket::AppSocket() : CNTSocket() {
    memset(&this->netAddr, 0, sizeof(SOCKADDR_IN));
}

/**
 *  @brief  创建应用层套接字，同时绑定其端口。
 */
AppSocket::AppSocket(unsigned short port) : CNTSocket(port) {
    memset(&this->netAddr, 0, sizeof(SOCKADDR_IN));
}

/**
 *  @brief  销毁应用层套接字。
 */
AppSocket::~AppSocket() {}

/**
 *  @brief  绑定本层套接字与网络层端口。
 *  @param  port    网络层端口号。
 *  @note   不是真绑定，只是存储网络层地址。
 */
void AppSocket::bindNet(unsigned short port) {
    this->netAddr.sin_family = AF_INET;
    this->netAddr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
    this->netAddr.sin_port = htons(port);
}

/**
 *  @brief  向网络层发消息。
 *  @param  message 要发的消息。
 *  @retval 发送的字节数。
 */
int AppSocket::sendToNet(string message) {
    int sentBytes = sendto(this->sock, message.c_str(), message.length(), 0,
                           (SOCKADDR *)&this->netAddr, sizeof(SOCKADDR));
    return sentBytes;
}

/**
 *  @brief  从网络层接收消息。
 *  @param  buffer  接收消息的缓存区。
 *  @param  timeout 接收超时时间。
 *  @retval 收到的字节数。
 */
int AppSocket::recvFromNet(char *buffer, int timeout) {
    memset(buffer, 0, sizeof(buffer));
    int size = sizeof(SOCKADDR);
    this->setRecvTimeout(timeout);
    int recvBytes = recvfrom(this->sock, buffer, MAX_BUFFER_SIZE, 0,
                             (SOCKADDR *)&this->netAddr, &size);
    if (recvBytes != 0) {
        buffer[recvBytes] = '\0';
    }
    return recvBytes;
}

/**
 *  @brief  创建网络层套接字。
 */
NetSocket::NetSocket() : CNTSocket() {
    memset(&this->appAddr, 0, sizeof(SOCKADDR_IN));
    memset(&this->phyAddr, 0, sizeof(SOCKADDR_IN));
}

/**
 *  @brief  创建网络层套接字，同时绑定其端口。
 */
NetSocket::NetSocket(unsigned short port) : CNTSocket(port) {
    memset(&this->appAddr, 0, sizeof(SOCKADDR_IN));
    memset(&this->phyAddr, 0, sizeof(SOCKADDR_IN));
}

/**
 *  @brief  销毁网络层套接字。
 */
NetSocket::~NetSocket() {}

/**
 *  @brief  绑定本层套接字与应用层端口。
 *  @param  port    应用层端口号。
 *  @note   不是真绑定，只是存储应用层地址。
 */
void NetSocket::bindApp(unsigned short port) {
    this->appAddr.sin_family = AF_INET;
    this->appAddr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
    this->appAddr.sin_port = htons(port);
}

/**
 *  @brief  向应用层发消息。
 *  @param  message 要发的消息。
 *  @retval 发送的字节数。
 */
int NetSocket::sendToApp(string message) {
    int sentBytes = sendto(this->sock, message.c_str(), message.length(), 0,
                           (SOCKADDR *)&this->appAddr, sizeof(SOCKADDR));
    return sentBytes;
}

/**
 *  @brief  从应用层接收消息。
 *  @param  buffer  接收消息的缓存区。
 *  @param  timeout 接收超时时间。
 *  @retval 收到的字节数。
 */
int NetSocket::recvFromApp(char *buffer, int timeout) {
    memset(buffer, 0, sizeof(buffer));
    int size = sizeof(SOCKADDR);
    this->setRecvTimeout(timeout);
    int recvBytes = recvfrom(this->sock, buffer, MAX_BUFFER_SIZE, 0,
                             (SOCKADDR *)&this->appAddr, &size);
    if (recvBytes != 0) {
        buffer[recvBytes] = '\0';
    }
    return recvBytes;
}

/**
 *  @brief  绑定本层套接字与物理层端口。
 *  @param  port    物理层端口号。
 *  @note   不是真绑定，只是存储物理层地址。
 */
void NetSocket::bindPhy(unsigned short port) {
    this->phyAddr.sin_family = AF_INET;
    this->phyAddr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
    this->phyAddr.sin_port = htons(port);
}

/**
 *  @brief  向物理层发消息。
 *  @param  message 要发的消息。
 *  @retval 发送的字节数。
 */
int NetSocket::sendToPhy(string message) {
    // 将01字符串转化为01序列。
    char *bitsArr = new char[message.length()];
    for (int i = 0; i < message.length(); i++) {
        bitsArr[i] = message[i] - '0';
    }
    // 流量控制。
    Sleep(FLOW_INTERVAL);
    // 发送01序列。
    int sentBytes = sendto(this->sock, bitsArr, message.length(), 0,
                           (SOCKADDR *)&this->phyAddr, sizeof(SOCKADDR));
    // 释放01序列空间。
    delete[] bitsArr;
    return sentBytes;
}

/**
 *  @brief  从物理层接收消息。
 *  @param  buffer  接收消息的缓存区。
 *  @param  timeout 接收超时时间。
 *  @retval 收到的字节数。
 */
int NetSocket::recvFromPhy(char *buffer, int timeout) {
    memset(buffer, 0, sizeof(buffer));
    // 接收01序列。
    int size = sizeof(SOCKADDR);
    this->setRecvTimeout(timeout);
    int recvBytes = recvfrom(this->sock, buffer, MAX_BUFFER_SIZE, 0,
                             (SOCKADDR *)&this->phyAddr, &size);
    if (recvBytes != 0) {
        buffer[recvBytes] = '\0';
    }
    // 将01序列转换为01字符串。
    for (int i = 0; i < recvBytes; i++) {
        buffer[i] += '0';
    }
    return recvBytes;
}

/**
 *  @brief  创建交换机网络层套接字。
 */
SwitchSocket::SwitchSocket() : CNTSocket() {}

/**
 *  @brief  创建交换机网络层套接字，同时绑定其端口。
 */
SwitchSocket::SwitchSocket(unsigned short port) : CNTSocket(port) {}

/**
 *  @brief  销毁交换机网络层套接字。
 */
SwitchSocket::~SwitchSocket() {
    this->phySocks.clear();
    this->addrTable.clear();
}

/**
 *  @brief  绑定本层套接字与各个物理层端口。
 *  @param  routePhyPort    对接路由器的物理层的端口号。
 *  @param  hostPhyPorts    对接主机的物理层的端口号。
 */
void SwitchSocket::bindPhys(unsigned short routePhyPort,
                            unsigned short *hostPhyPorts) {
    CNTSocket *socks = new CNTSocket[HOST_PER_SWITCHER + 1];
    // 先存储对接路由器的物理层的套接字。
    socks[0].bindSelf(routePhyPort);
    this->phySocks[routePhyPort] = socks[0];
    // 再存储对接主机的物理层地址。
    for (int i = 1; i <= HOST_PER_SWITCHER; i++) {
        socks[i].bindSelf(hostPhyPorts[i - 1]);
        this->phySocks[hostPhyPorts[i - 1]] = socks[i];
    }
}

/**
 *  @brief  向指定物理层发消息。
 *  @param  message 要发的消息。
 *  @param  port    指定物理层的端口号。
 *  @retval 发送的字节数。
 */
int SwitchSocket::sendToPhy(string message, unsigned short port) {
    // 将01字符串转化为01序列。
    char *bitsArr = new char[message.length()];
    for (int i = 0; i < message.length(); i++) {
        bitsArr[i] = message[i] - '0';
    }
    // 流量控制。
    Sleep(FLOW_INTERVAL);
    // 发送01序列。
    SOCKADDR_IN addr = CNTSocket::getAddress(this->phySocks[port]);
    int sentBytes = sendto(this->sock, bitsArr, message.length(), 0,
                           (SOCKADDR *)&addr, sizeof(SOCKADDR));
    // 释放01序列空间。
    delete[] bitsArr;
    return sentBytes;
}

/**
 *  @brief  从指定物理层接收消息。
 *  @param  buffer  接收消息的缓存区。
 *  @param  port    指定物理层的端口号。
 *  @param  timeout 接收超时时间。
 *  @retval 收到的字节数。
 */
int SwitchSocket::recvFromPhy(char *buffer, unsigned short port, int timeout) {
    memset(buffer, 0, sizeof(buffer));
    // 接收01序列。
    int size = sizeof(SOCKADDR);
    SOCKADDR_IN addr = CNTSocket::getAddress(this->phySocks[port]);
    this->setRecvTimeout(timeout);
    int recvBytes = recvfrom(this->sock, buffer, MAX_BUFFER_SIZE, 0,
                             (SOCKADDR *)&addr, &size);
    if (recvBytes != 0) {
        buffer[recvBytes] = '\0';
    }
    // 将01序列转换为01字符串。
    for (int i = 0; i < recvBytes; i++) {
        buffer[i] += '0';
    }
    return recvBytes;
}

unsigned short SwitchSocket::selectReadyPort() {
    FD_SET rfds;
    FD_ZERO(&rfds);
    // 把交换机所有物理层端口都加入rfds。
    map<unsigned short, CNTSocket>::iterator iter;
    for (iter = this->phySocks.begin(); iter != this->phySocks.end(); iter++) {
        FD_SET(iter->second.getSocket(), &rfds);
    }
    // 在时限内检查是否有套接字可读。
    TIMEVAL timeout = {SELECT_TIMEOUT, 0};
    int readyNum = select(0, &rfds, nullptr, nullptr, &timeout);
    if (readyNum == 0) {
        // 如果没有套接字可读，就返回0。
        return 0;
    } else {
        // 如果有套接字可读，就找到它并返回它的端口号。
        for (iter = this->phySocks.begin(); iter != this->phySocks.end();
             iter++) {
            if (FD_ISSET(iter->second.getSocket(), &rfds)) {
                return iter->first;
            }
        }
        // 程序照理不会走到这里，但还是加一层保险。
        return 0;
    }
}

void SwitchSocket::printPhySocks() {
    map<unsigned short, CNTSocket>::iterator iter;
    for (iter = this->phySocks.begin(); iter != this->phySocks.end(); iter++) {
        cout << iter->first << " : " << CNTSocket::getPort(iter->second)
             << endl;
    }
}

void SwitchSocket::printAddrTable() {
    cout << "| Local | Remote |" << endl;
    cout << "|-------|--------|" << endl;
    map<unsigned short, unsigned short>::iterator iter;
    for (iter = this->addrTable.begin(); iter != this->addrTable.end();
         iter++) {
        cout << "| " << iter->first << " | " << iter->second << " |" << endl;
    }
}