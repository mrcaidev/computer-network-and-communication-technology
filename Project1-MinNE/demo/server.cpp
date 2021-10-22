/**
 * @name: server.cpp
 * @author: MrCai
 * @description: 支持修改宏以修改服务器 IP 与端口，并持续与客户端通信。
 */
#include <iostream>
#include <winsock2.h>
using namespace std;

#define MAX_BUFFER_SIZE 512
#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 1234

int main(int argc, char *argv[]) {
    // 初始化 DLL 与网络库。
    WSADATA wsaData;
    int state = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (state != 0) {
        cout << "Error: Windows socket asynchronous startup failed." << endl;
        return -1;
    }
    // 创建服务器套接字。
    SOCKET serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (serverSocket == INVALID_SOCKET) {
        cout << "Error: Invalid server socket." << endl;
        return -1;
    }
    // 确定服务器地址。
    SOCKADDR_IN serverAddress;
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.S_un.S_addr = inet_addr(SERVER_IP);
    serverAddress.sin_port = htons(SERVER_PORT);
    // 绑定服务器套接字与地址。
    state =
        bind(serverSocket, (SOCKADDR *)&serverAddress, sizeof(serverAddress));
    if (state == SOCKET_ERROR) {
        cout << "Error: Server failed to bind socket and address." << endl;
        closesocket(serverSocket);
        return -1;
    }

    // 服务端开始监听。
    state = listen(serverSocket, 5);
    if (state == SOCKET_ERROR) {
        cout << "Error: Server failed to listen." << endl;
        closesocket(serverSocket);
        return -1;
    }

    // 接受客户端连接请求，分配客户端端口号。
    SOCKADDR_IN clientAddress;
    int clientSize = sizeof(clientAddress);
    SOCKET clientSocket =
        accept(serverSocket, (SOCKADDR *)&clientAddress, &clientSize);
    if (clientSocket == INVALID_SOCKET) {
        cout << "Error: Invalid client socket." << endl;
        return -1;
    }
    cout << "---------------------------------------" << endl;
    cout << "Client connection accepted: " << inet_ntoa(clientAddress.sin_addr)
         << ":" << clientAddress.sin_port << endl;
    // 通知客户端其端口号。
    char portStr[5];
    itoa(clientAddress.sin_port, portStr, 10);
    send(clientSocket, portStr, strlen(portStr), 0);

    char recvData[MAX_BUFFER_SIZE];
    while (true) {
        memset(recvData, '\0', sizeof(recvData));
        int recvLen = recv(clientSocket, recvData, MAX_BUFFER_SIZE, 0);
        if (recvLen <= 0)
            continue;
        else
            recvData[recvLen] = '\0';
        if (strcmp(recvData, "quit") == 0)
            break;
        cout << "Received data: " << recvData << endl;
    }

    closesocket(clientSocket);
    closesocket(serverSocket);
    WSACleanup();
    cout << "---------------------------------------" << endl;
    cout << "Server closed." << endl;
    return 0;
}