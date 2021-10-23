#include <iostream>
#include <windows.h>
#include <cmath>
#include "param.h"
using namespace std;

string decToBin(unsigned short dec) {
    string bin = "";
    while (dec || bin.length() != BITS_PER_CHAR) {
        bin.insert(0, to_string(dec % 2));
        dec /= 2;
    }
    return bin;
}

unsigned short binToDec(string bin) {
    unsigned short dec = 0;
    for (int i = 0; i < BITS_PER_CHAR; i++) {
        if (bin[i] == '0')
            continue;
        dec += pow(2.0, BITS_PER_CHAR - 1 - i);
    }
    return dec;
}

string encode(string unicode) {
    string secret = "";
    unsigned short decArr[MAX_CHAR_NUM] = {0};
    int len =
        MultiByteToWideChar(CP_ACP, 0, (LPCCH)unicode.c_str(), -1, nullptr, 0);
    MultiByteToWideChar(CP_ACP, 0, (LPCCH)unicode.c_str(), -1, (LPWSTR)decArr,
                        len);
    for (int i = 0; i < len - 1; i++) {
        secret.append(decToBin(decArr[i]));
    }
    return secret;
}

string decode(string secret) {
    unsigned short decArr[MAX_CHAR_NUM] = {0};
    for (int i = 0; i < secret.length() / BITS_PER_CHAR; i++) {
        string bin = secret.substr(i * BITS_PER_CHAR, BITS_PER_CHAR);
        decArr[i] = binToDec(bin);
    }

    int len = WideCharToMultiByte(CP_ACP, 0, (LPCWCH)decArr, -1, nullptr, 0,
                                  nullptr, FALSE);
    char *temp = new char[len];
    memset(temp, 0, len);
    WideCharToMultiByte(CP_ACP, 0, (LPCWCH)decArr, -1, temp, len, nullptr,
                        FALSE);

    string message = temp;
    delete[] temp;
    return message;
}

// int main() {
//     string raw = "";
//     cout << "Raw:     ";
//     cin >> raw;
//     string secret = encode(raw);
//     string message = decode(secret);
//     cout << "Secret:  " << secret << endl;
//     cout << "Message: " << message << endl;
//     return 0;
// }