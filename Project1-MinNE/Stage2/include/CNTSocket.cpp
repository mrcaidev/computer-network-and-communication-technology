#include <iostream>
#include <winsock2.h>
using namespace std;

#define MAX_BUFFER_SIZE 65536

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
    void bindOwnPort(int port);
    void bindLowerPort(int port);
    void sendToLower(string message);
    void recvFromUpper(char *buffer);
};

CNTSocket::CNTSocket(int type) {
    this->sock = socket(AF_INET, type, 0);

    if (this->sock == INVALID_SOCKET) {
        cout << "Error: socket() failed. (" << WSAGetLastError() << ")" << endl;
        exit(-1);
    }
}

CNTSocket::~CNTSocket() { closesocket(this->sock); }

SOCKET CNTSocket::getSocket() { return this->sock; }

void CNTSocket::bindOwnPort(int port) {
    this->addr.sin_family = AF_INET;
    this->addr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
    this->addr.sin_port = htons(port);

    int state = bind(this->sock, (SOCKADDR *)&this->addr, sizeof(SOCKADDR));

    if (state == SOCKET_ERROR) {
        cout << "Error: bind() failed. (" << WSAGetLastError() << ")" << endl;
        exit(-1);
    }
}

void CNTSocket::bindLowerPort(int port) {
    this->lowerAddr.sin_family = AF_INET;
    this->lowerAddr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
    this->lowerAddr.sin_port = htons(port);
}

void CNTSocket::sendToLower(string message) {
    int sentBytes = sendto(this->sock, message.c_str(), message.length(), 0,
                           (SOCKADDR *)&this->lowerAddr, sizeof(SOCKADDR));

    if (sentBytes == 0) {
        cout << "0 bytes of message is sent. (" << WSAGetLastError() << ")"
             << endl;
    }
}

void CNTSocket::recvFromUpper(char *buffer) {
    int size = sizeof(SOCKADDR);

    int recvBytes = recvfrom(this->sock, buffer, MAX_BUFFER_SIZE, 0,
                             (SOCKADDR *)&this->upperAddr, &size);

    if (recvBytes == 0) {
        cout << "0 bytes of message is received. (" << WSAGetLastError() << ")"
             << endl;
    } else {
        buffer[recvBytes] = '\0';
    }
}