/**
 *  @file   frame.cpp
 *  @brief  封装帧相关操作函数。
 *  @author 蔡与望
 */
#pragma once
#include <iostream>
#include "param.h"
#include "coding.cpp"
using namespace std;

/**
 *  @brief  KMP算法的先置函数，算出模式串的next数组。
 *  @param  pattern 目标子串。
 *  @return 整型数组，存储子串每一位的next值。
 */
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

/**
 *  @brief  KMP算法实现，在父串中查找指定子串。
 *  @param  str     父串。
 *  @param  pattern 子串。
 *  @return 子串首次出现的下标；如果找不到则返回-1。
 */
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

/**
 *  @brief  帧封装。
 */
class Frame {
  private:
    unsigned short srcPort;
    unsigned short seq;
    string data;
    unsigned short dstPort;
    unsigned short checksum;
    bool verified;
    string checkTarget;

    string extractMessage(string raw);
    static string transform(string message);
    static unsigned short generateChecksum(string message);
    static string addLocator(string message);

  public:
    Frame();
    Frame(string raw);
    Frame(unsigned short srcPort, unsigned short seq, string data,
          unsigned short dstPort);
    ~Frame();

    unsigned short getSrcPort();
    unsigned short getSeq();
    string getData();
    unsigned short getDstPort();
    bool isVerified();

    string stringify();
    static int calcTotal(int messageLen);
};

/**
 *  @brief  初始化空帧。
 */
Frame::Frame() {
    this->srcPort = 0;
    this->seq = 0;
    this->data = "";
    this->dstPort = 0;
    this->checksum = 0;
    this->checkTarget = "";
    this->verified = true;
}

/**
 *  @brief  供接收端使用，将01字符串自动解析为帧。
 *  @param  raw 接收端从物理层收到的01字符串。
 */
Frame::Frame(string raw) {
    this->checkTarget = "";
    this->verified = true;
    string temp = "";
    // 反变换。
    string message = this->extractMessage(raw);
    // 提取源地址。
    temp = message.substr(0, PORT_LEN);
    this->srcPort = binToDec(temp);
    this->checkTarget += temp;
    message = message.substr(PORT_LEN);
    // 提取序号。
    temp = message.substr(0, SEQ_LEN);
    this->seq = binToDec(temp);
    this->checkTarget += temp;
    message = message.substr(SEQ_LEN);
    // 提取checksum。
    temp = message.substr(message.length() - CHECKSUM_LEN);
    this->checksum = binToDec(temp);
    message = message.substr(0, message.length() - CHECKSUM_LEN);
    // 提取目的地址。
    temp = message.substr(message.length() - PORT_LEN);
    this->dstPort = binToDec(temp);
    message = message.substr(0, message.length() - PORT_LEN);
    // 提取消息。
    this->data = message;
    this->checkTarget += message;
    this->checkTarget += temp;
    // 如果extractMessage()就出错，那结果必为错；
    // 如果extractMessage()没出错，那就进一步检验校验和。
    this->verified =
        this->verified &&
        (this->checksum == Frame::generateChecksum(this->checkTarget));
}

/**
 *  @brief  供发送端使用，将数据手动封装成帧。
 *  @param  srcPort 源端口。
 *  @param  seq     序号。
 *  @param  data    01字符串形式的消息数据。
 *  @param  dstPort 目的端口。
 */
Frame::Frame(unsigned short srcPort, unsigned short seq, string data,
             unsigned short dstPort) {
    this->checkTarget = "";
    // 设置源地址。
    this->srcPort = srcPort;
    this->checkTarget += decToBin(srcPort, PORT_LEN);
    // 设置序号。
    this->seq = seq;
    this->checkTarget += decToBin(seq, SEQ_LEN);
    // 设置数据。
    this->data = data;
    this->checkTarget += data;
    // 设置目的端口。
    this->dstPort = dstPort;
    this->checkTarget += decToBin(dstPort, PORT_LEN);
    // 设置校验和。
    this->checksum = Frame::generateChecksum(this->checkTarget);
    this->verified = true;
}

/**
 *  @brief  销毁一帧。
 */
Frame::~Frame() {
    this->data.clear();
    this->checkTarget.clear();
}

/**
 *  @brief  获取源端口。
 */
unsigned short Frame::getSrcPort() { return this->srcPort; }

/**
 *  @brief  获取序号。
 */
unsigned short Frame::getSeq() { return this->seq; }

/**
 *  @brief  获取数据。
 */
string Frame::getData() { return this->data; }

/**
 *  @brief  获取目的端口。
 */
unsigned short Frame::getDstPort() { return this->dstPort; }

/**
 *  @brief  检测校验和是否正确。
 */
bool Frame::isVerified() { return this->verified; }

/**
 *  @brief  供发送端使用，自动序列化帧。
 *  @return 能够直接发到物理层的01字符串。
 */
string Frame::stringify() {
    string message = this->checkTarget;
    message += decToBin(this->checksum, CHECKSUM_LEN);
    message = Frame::addLocator(message);
    return message;
}

/**
 *  @brief  供接收端解析时使用，无需手动调用，反变换01序列。
 *  @param  raw 从物理层收到的01字符串。
 */
string Frame::extractMessage(string raw) {
    string message = "";
    // 异常一：帧头帧尾同时出错，程序找不到定位串，就提前返回空消息。
    int startPos = kmp(raw, LOCATOR);
    if (startPos == -1) {
        this->verified = false;
        return EMPTY_FRAME;
    }
    // 找到了帧头，就对剩下的字符串进行反变换。
    string remainedMessage = raw.substr(startPos + LOCATOR_LEN);
    int suspiciousPos = kmp(remainedMessage, TRANSFORM_TARGET);
    while (suspiciousPos != -1) {
        if (remainedMessage[suspiciousPos + 5] == '1') {
            // 到达帧尾。
            message += remainedMessage.substr(0, suspiciousPos - 1);
            return message;
        } else {
            // 删除这个0，继续寻找。
            message += remainedMessage.substr(0, suspiciousPos + 5);
            remainedMessage = remainedMessage.substr(suspiciousPos + 6);
            suspiciousPos = kmp(remainedMessage, TRANSFORM_TARGET);
        }
    }
    // 程序会走到这里，说明只找到了一个定位串。提前设verify=False。
    this->verified = false;
    // 异常二：帧头出错，帧尾没错，程序会误认为帧尾是帧头。此时message为空。
    // 异常三：帧头没错，帧尾出错。此时message不为空，但有可能已经写入了帧外乱码，不能相信。
    // 无论如何都应该返回空帧。
    return EMPTY_FRAME;
}

/**
 *  @brief  供发送端帧同步时使用，无需手动调用，变换01序列。
 *  @param  message 帧内的控制信息与数据。
 */
string Frame::transform(string message) {
    string transMessage = "";
    // 破坏所有"11111X"的结构。
    int suspiciousPos = kmp(message, TRANSFORM_TARGET);
    while (suspiciousPos != -1) {
        transMessage += message.substr(0, suspiciousPos + 5);
        transMessage += "0";
        message = message.substr(suspiciousPos + 5);
        suspiciousPos = kmp(message, TRANSFORM_TARGET);
    }
    transMessage += message;
    return transMessage;
}

/**
 *  @brief  给任意长度为8的倍数的字符串生成校验和。
 *  @param  message 目标字符串。
 */
unsigned short Frame::generateChecksum(string message) {
    unsigned short checksum = 0;
    int len = message.length() / 8;
    // 每8位视作一个整数。
    for (int i = 0; i < len; i++) {
        string piece = message.substr(i * 8, 8);
        checksum += binToDec(piece);
    }
    return checksum;
}

/**
 *  @brief  供发送端使用，无需手动调用，实现帧同步。
 *  @param  message 帧内的控制信息与数据。
 *  @return 实现帧同步后的字符串，可以直接发给物理层。
 */
string Frame::addLocator(string message) {
    string syncMessage = "";
    syncMessage += LOCATOR;
    syncMessage += transform(message);
    syncMessage += LOCATOR;
    return syncMessage;
}

/**
 *  @brief  供发送端使用，根据应用层发来的消息，计算需要分多少帧发送。
 *  @param  messageLen  消息的总长度。
 *  @retval 需要封装的帧数。
 */
int Frame::calcTotal(int messageLen) {
    // 向上取整。
    return messageLen % DATA_LEN ? messageLen / DATA_LEN + 1
                                 : messageLen / DATA_LEN;
}