/**
 * @name: client.cpp
 * @author: MrCai
 * @description:
 * 每`500ms`向服务器发送一个随机数，如果服务器有返回则立刻发送新随机数。
 */
#include <ctime>
#include <iostream>
#include <winsock2.h>
#include <windows.h>
using namespace std;

#define MAX_BUFFER_SIZE 512

int main(int argc, char *argv[]) {
    // 随机数的随机种子。
    srand(time(NULL));
    // 超时`500ms`未接到服务器返回值，则发送下一个数字。
    TIMEVAL timeout = {0, 500000};
    // 计时器。
    clock_t start, end;

    // 初始化 DLL 与网络库。
    WSADATA wsaData;
    int state = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (state != 0) {
        cout << "Error: WSAStartup() failed. (" << WSAGetLastError() << ")"
             << endl;
        return -1;
    }

    // 创建客户端套接字。
    SOCKET clientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (clientSocket == INVALID_SOCKET) {
        cout << "Error: Invalid client socket. (" << WSAGetLastError() << ")"
             << endl;
        return -1;
    }

    // 输入服务器地址。
    string serverIp = "";
    int serverPort = 0;
    cout << "Server IP: ";
    cin >> serverIp;
    cout << "Server port: ";
    cin >> serverPort;
    SOCKADDR_IN serverAddress;
    int serverSize = sizeof(serverAddress);
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.S_un.S_addr = inet_addr(serverIp.c_str());
    serverAddress.sin_port = htons(serverPort);

    // 客户端套接字绑定服务器地址。
    state = connect(clientSocket, (SOCKADDR *)&serverAddress, serverSize);
    if (state == SOCKET_ERROR) {
        cout << "Error: connect() failed. (" << WSAGetLastError() << ")"
             << endl;
        closesocket(clientSocket);
        return -1;
    }

    // 接收分配到的端口号。
    char portStr[5];
    recv(clientSocket, portStr, 5, 0);
    cout << "Client port at: " << portStr << endl;

    // 开始与服务器通信。
    cout << "---------------------------------------" << endl;
    char sumStr[MAX_BUFFER_SIZE];
    FD_SET rfds;
    start = clock();
    for (int index = 0; index < 20; index++) {
        // 清空接收区。
        memset(sumStr, '\0', sizeof(sumStr));
        // 产生随机数并发送。
        string sendStr = to_string(rand() % 500 + 1);
        cout << index + 1 << "\tGenerated: " << sendStr;
        send(clientSocket, sendStr.c_str(), sendStr.length(), 0);
        // 可能要接收服务器的返回值。
        FD_ZERO(&rfds);
        FD_SET(clientSocket, &rfds);
        int readyNum = select(0, &rfds, NULL, NULL, &timeout);
        if (!readyNum)
            cout << endl;
        else {
            recv(clientSocket, sumStr, MAX_BUFFER_SIZE, 0);
            cout << "\tSum: " << atoi(sumStr) << endl;
        }
    }
    end = clock();

    // 关闭服务。
    closesocket(clientSocket);
    WSACleanup();
    cout << "---------------------------------------" << endl;
    cout << "Client closed." << endl;
    cout << "Session cost " << (double)(end - start) / CLOCKS_PER_SEC
         << " second(s)." << endl
         << endl;
    return 0;
}