// #pragma once
#include <iostream>
#include "coding.cpp"
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

class Frame {
  private:
    unsigned short srcPort;
    unsigned short seq;
    string data;
    unsigned short dstPort;
    string CRC;

  public:
    Frame();
    Frame(string raw);
    Frame(unsigned short srcPort, unsigned short seq, string data,
          unsigned short dstPort);
    ~Frame();
    void setSrcPort(unsigned short port);
    void setDstPort(unsigned short port);
    void setSeq(unsigned short seq);
    void setData(string data);
    string getData();
    string generateCRC();
    bool verifyCRC();
    string stringify();
    static string transform(string message);
    static string addLocator(string message);
    static string extractMessage(string raw);
    static int calcNum(int messageLen);
};

Frame::Frame() {
    this->srcPort = 0;
    this->seq = 0;
    this->data = "";
    this->dstPort = 0;
    this->CRC = "";
}

Frame::Frame(string raw) {
    string message = extractMessage(raw);
    // 提取源地址。
    this->srcPort = binToDec(message.substr(0, PORT_LEN), PORT_LEN);
    message = message.substr(PORT_LEN);
    // 提取序号。
    this->seq = binToDec(message.substr(0, SEQ_LEN), SEQ_LEN);
    message = message.substr(SEQ_LEN);
    cout << "\rFrame[" << this->seq << "] ";
    // 提取CRC码。
    string CRC = message.substr(message.length() - CRC_LEN);
    message = message.substr(0, message.length() - CRC_LEN);
    // 提取目的地址。
    this->dstPort =
        binToDec(message.substr(message.length() - PORT_LEN), PORT_LEN);
    message = message.substr(0, message.length() - PORT_LEN);
    // 提取消息。
    this->data = message;
    cout << message << endl;
}

Frame::Frame(unsigned short srcPort, unsigned short seq, string data,
             unsigned short dstPort) {
    this->srcPort = srcPort;
    this->seq = seq;
    this->data = data;
    this->dstPort = dstPort;
    this->CRC = "";
}

Frame::~Frame() {
    this->srcPort = 0;
    this->seq = 0;
    this->data.clear();
    this->dstPort = 0;
    this->CRC.clear();
}

void Frame::setSrcPort(unsigned short port) { this->srcPort = port; }

void Frame::setDstPort(unsigned short port) { this->dstPort = port; }

void Frame::setSeq(unsigned short seq) { this->seq = seq; }

void Frame::setData(string data) { this->data = data; }

string Frame::getData() { return this->data; }

string Frame::generateCRC() {
    this->CRC = "00000000";
    return this->CRC;
}

bool Frame::verifyCRC() { return true; }

string Frame::stringify() {
    string message = "";
    message += decToBin(this->srcPort, PORT_LEN);
    message += decToBin(this->seq, SEQ_LEN);
    message += this->data;
    message += decToBin(this->dstPort, PORT_LEN);
    message += this->generateCRC();
    message = this->addLocator(message);
    return message;
}

string Frame::extractMessage(string raw) {
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

string Frame::transform(string message) {
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

string Frame::addLocator(string message) {
    string ret = "";
    // 对于字符串，`a += b`开销低于`a = a + b`。
    ret += LOCATOR;
    ret += transform(message);
    ret += LOCATOR;
    return ret;
}

int Frame::calcNum(int messageLen) {
    return messageLen % DATA_LEN ? messageLen / DATA_LEN + 1
                                 : messageLen / DATA_LEN;
}