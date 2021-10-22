/**
 * @name: server.cpp
 * @author: MrCai
 * @description: 网元应用层。
 */
#include <iostream>
#include <winsock2.h>
#include "include/CNTSocket.cpp"
using namespace std;

#define MAX_BUFFER_SIZE 65536

int main(int argc, char *argv[]) {
    cout << "---------------App Layer---------------" << endl;
    int port = 0;
    int mode = 0;
    char buffer[MAX_BUFFER_SIZE];
    string message = "";

    WSADATA wsaData = initWSA();
    CNTSocket sock(SOCK_DGRAM);

    cout << "App port at: ";
    cin >> port;
    sock.bindOwnPort(port);

    cout << "Net port at: ";
    cin >> port;
    sock.bindLowerPort(port);

    while (true) {
        cout << "Select mode: (1::Send, 2::Recv)" << endl << ">>> ";
        cin >> mode;
        if (mode == 1) {
            cout << "Message to send: ";
            cin >> message;
            sock.sendToLower(message);
        } else if (mode == 2) {
            sock.recvFromUpper(buffer);
            cout << "Message received: " << buffer << endl;
        }
    }
}