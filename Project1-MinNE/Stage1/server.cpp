/**
 * @name: server.cpp
 * @author: MrCai
 * @description:
 * 接收客户端的随机数，并产生新随机数；如果总和超过上限，则将总和返回给客户端。
 */
#include <ctime>
#include <iostream>
#include <winsock2.h>
#include <windows.h>
using namespace std;

#define MAX_BUFFER_SIZE 512
#define SUM_BORDER 100

int main(int argc, char *argv[]) {
    // 随机数的随机种子。
    srand(time(NULL));

    // 初始化 DLL 与网络库。
    WSADATA wsaData;
    int state = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (state != 0) {
        cout << "Error: WSAStartup() failed. (" << WSAGetLastError() << ")"
             << endl;
        return -1;
    }

    // 创建服务器套接字。
    SOCKET serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (serverSocket == INVALID_SOCKET) {
        cout << "Error: Invalid server socket. (" << WSAGetLastError() << ")"
             << endl;
        return -1;
    }

    // 确定服务器地址。
    SOCKADDR_IN serverAddress;
    int serverSize = sizeof(serverAddress);
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
    serverAddress.sin_port = htons(1234);

    // 绑定服务器套接字与地址。
    state = bind(serverSocket, (SOCKADDR *)&serverAddress, serverSize);
    if (state == SOCKET_ERROR) {
        cout << "Error: bind() failed. (" << WSAGetLastError() << ")" << endl;
        closesocket(serverSocket);
        return -1;
    }

    // 服务端开始监听。
    state = listen(serverSocket, 5);
    if (state == SOCKET_ERROR) {
        cout << "Error: listen() failed. (" << WSAGetLastError() << ")" << endl;
        closesocket(serverSocket);
        return -1;
    }

    // 接受客户端连接请求，系统分配客户端端口号。
    SOCKADDR_IN clientAddress;
    int clientSize = sizeof(clientAddress);
    SOCKET clientSocket =
        accept(serverSocket, (SOCKADDR *)&clientAddress, &clientSize);
    if (clientSocket == INVALID_SOCKET) {
        cout << "Error: Invalid client socket. (" << WSAGetLastError() << ")"
             << endl;
        return -1;
    }
    cout << "Client connection accepted: " << inet_ntoa(clientAddress.sin_addr)
         << ":" << clientAddress.sin_port << endl;

    // 通知客户端其端口号。
    string portStr;
    portStr = to_string(clientAddress.sin_port);
    send(clientSocket, portStr.c_str(), portStr.length(), 0);

    // 开始与客户端通信。
    cout << "---------------------------------------" << endl;
    char recvStr[MAX_BUFFER_SIZE];
    int returnCnt = 0;
    for (int index = 0; index < 20; index++) {
        // 清空接收区。
        memset(recvStr, '\0', sizeof(recvStr));
        // 接收客户端发来的数字。
        int recvLen = recv(clientSocket, recvStr, MAX_BUFFER_SIZE, 0);
        if (recvLen > 0)
            recvStr[recvLen] = '\0';
        else
            continue;
        int recvNum = atoi(recvStr);
        cout << index + 1 << "\tReceived: " << recvNum;
        // 产生随机数并相加。
        int randNum = rand() % 500 + 1;
        cout << "\tGenerated: " << randNum << endl;
        int sum = recvNum + randNum;
        // 如果超过上限，则把结果返回客户端。
        if (sum > SUM_BORDER) {
            string sumStr = to_string(sum);
            send(clientSocket, sumStr.c_str(), sumStr.length(), 0);
            returnCnt++;
        }
    }

    // 关闭服务。
    closesocket(serverSocket);
    WSACleanup();
    cout << "---------------------------------------" << endl;
    cout << "Server closed. " << endl;
    cout << returnCnt << " return(s), time expected: " << 10 - 0.5 * returnCnt
         << " second(s)." << endl
         << endl;
    return 0;
}