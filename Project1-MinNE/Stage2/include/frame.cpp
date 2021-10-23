#include <iostream>
#include "param.h"
using namespace std;

int *getNext(string pattern) {
    int len = pattern.length();
    int *next = new int[len];
    next[0] = -1;
    int j = 0, k = -1;
    while (j < len) {
        if (k == -1 || pattern[k] == pattern[j]) {
            j++;
            k++;
            next[j] = k;
        } else {
            k = next[k];
        }
    }
    return next;
}

int kmpOrder(string str, string pattern) {
    int *next = getNext(pattern);
    int strLen = str.length();
    int patternLen = pattern.length();
    int i = 0, j = 0;
    while (i < strLen && j < patternLen) {
        if (j == -1 || str[i] == pattern[j]) {
            i++;
            j++;
        } else {
            j = next[j];
        }
    }
    if (j == patternLen) {
        return i - patternLen;
    }
    return -1;
}

int kmpRev(string str, string pattern) {
    string strRev(str.rbegin(), str.rend());
    string patternRev(pattern.rbegin(), pattern.rend());
    int res = kmpOrder(strRev, patternRev);
    return str.length() - res - 8;
}

string addLocator(string message) {
    string ret;
    // 对于字符串，`a += b`开销低于`a = a + b`。
    ret += LOCATOR;
    ret += message;
    ret += LOCATOR;
    return ret;
}

string findFrame(string raw) {
    int start = kmpOrder(raw, LOCATOR);
    int end = kmpRev(raw, LOCATOR);
    return raw.substr(start + 8, end - start - 8);
}

int calcFrameNum(int messageLen) {
    int totalLen = 8 + 8 + 4 + messageLen + 8 + 8 + 8;
}

void capsulate(string message) {
    // 数据之前加上序号。
    // 前面加源端口。
    // 后面加目的端口。
    // 后面加校验码。
    // 帧头帧尾加定位码。
}

// int main(int argc, char const *argv[]) {
//     string raw = "00101010111";
//     string secret = addLocator(raw);
//     string message = findFrame(secret);
//     cout << "Raw:             " << raw << endl;
//     cout << "Secret:  " << secret << endl;
//     cout << "Message:         " << message << endl;
//     return 0;
// }
