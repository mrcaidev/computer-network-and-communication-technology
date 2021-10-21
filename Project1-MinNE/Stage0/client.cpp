/**
 * @name: client.cpp
 * @author: MrCai
 * @description: 支持手动输入服务器 IP 与端口，并持续与服务端保持连接。
 */
#include <iostream>
#include <winsock2.h>
using namespace std;

#define MAX_BUFFER_SIZE 512

int main(int argc, char *argv[]) {
    // 初始化 DLL 与网络库。
    WSADATA wsaData;
    int state = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (state != 0) {
        cout << "Error: Windows socket asynchronous startup failed." << endl;
        return -1;
    }
    // 创建客户端套接字。
    SOCKET clientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (clientSocket == INVALID_SOCKET) {
        cout << "Error: Invalid client socket." << endl;
        return -1;
    }
    // 输入服务器地址。
    cout << "---------------------------------------" << endl;
    string serverIp = "";
    int serverPort = 0;
    cout << "Server IP: ";
    cin >> serverIp;
    cout << "Server port: ";
    cin >> serverPort;
    // string serverIp = "127.0.0.1";
    // int serverPort = 1234;
    SOCKADDR_IN serverAddress;
    int serverSize = sizeof(serverAddress);
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.S_un.S_addr = inet_addr(serverIp.c_str());
    serverAddress.sin_port = htons(serverPort);

    // 客户端套接字绑定服务器地址。
    state = connect(clientSocket, (SOCKADDR *)&serverAddress, serverSize);
    if (state == SOCKET_ERROR) {
        cout << "Error: Client failed to connect to server." << endl;
        closesocket(clientSocket);
        return -1;
    }

    // 接收分配到的端口号。
    char portStr[5];
    recv(clientSocket, portStr, 5, 0);
    cout << "Client port at: " << portStr << endl;

    // 给服务端发消息。
    while (true) {
        string message;
        cout << ">>> ";
        cin >> message;
        send(clientSocket, message.c_str(), message.length(), 0);
        if (message == "quit")
            break;
    }

    // 关闭服务。
    closesocket(clientSocket);
    WSACleanup();
    cout << "---------------------------------------" << endl;
    cout << "Client closed." << endl;
    return 0;
}