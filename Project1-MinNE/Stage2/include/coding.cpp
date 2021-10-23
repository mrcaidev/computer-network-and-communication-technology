#pragma once
#include <iostream>
#include <windows.h>
#include <cmath>
#include "param.h"
using namespace std;

string decToBin(int dec, int bits) {
    string bin = "";
    while (dec || bin.length() != bits) {
        bin.insert(0, to_string(dec % 2));
        dec /= 2;
    }
    return bin;
}

int binToDec(string bin, int bits) {
    int dec = 0;
    for (int i = 0; i < bits; i++) {
        if (bin[i] == '0')
            continue;
        dec += pow(2.0, bits - 1 - i);
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
        secret.append(decToBin(decArr[i], BITS_PER_CHAR));
    }
    return secret;
}

string decode(string secret) {
    unsigned short decArr[MAX_CHAR_NUM] = {0};
    for (int i = 0; i < secret.length() / BITS_PER_CHAR; i++) {
        string bin = secret.substr(i * BITS_PER_CHAR, BITS_PER_CHAR);
        decArr[i] = binToDec(bin, BITS_PER_CHAR);
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
//     cin >> raw; // 01001111011000000101100101111101
//     string secret = encode(raw);
//     string message = decode(secret);
//     cout << "Secret:  " << secret << endl;
//     cout << "Message: " << message << endl;
//     return 0;
// }