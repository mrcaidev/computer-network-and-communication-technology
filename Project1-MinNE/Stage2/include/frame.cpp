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

int kmp(string str, string pattern) {
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

string trans(string message) {
    string transMessage = "";
    int suspiciousPos = kmp(message, "11111");
    while (suspiciousPos != -1) {
        transMessage += message.substr(0, suspiciousPos + 5);
        transMessage += "0";
        message = message.substr(suspiciousPos + 5);
        suspiciousPos = kmp(message, "11111");
    }
    transMessage += message;
    return transMessage;
}

string invTrans(string raw) {
    string message = "";
    string remainedMessage = raw.substr(kmp(raw, LOCATOR) + LOCATOR_LEN);
    int suspiciousPos = kmp(remainedMessage, "11111");
    while (suspiciousPos != -1) {
        if (remainedMessage[suspiciousPos + 5] == '1') {
            // 到达帧尾。
            message += remainedMessage.substr(0, suspiciousPos - 1);
            return message;
        } else {
            // 删除这个0。
            message += remainedMessage.substr(0, suspiciousPos + 5);
            remainedMessage = remainedMessage.substr(suspiciousPos + 6);
            suspiciousPos = kmp(remainedMessage, "11111");
        }
    }
    return message;
}

string addLocator(string message) {
    string ret;
    // 对于字符串，`a += b`开销低于`a = a + b`。
    ret += LOCATOR;
    ret += message;
    ret += LOCATOR;
    return ret;
}

int calcFrameNum(int messageLen) {
    return messageLen % DATA_LEN ? messageLen / DATA_LEN + 1
                                 : messageLen / DATA_LEN;
}

// int main(int argc, char const *argv[]) { return 0; }
