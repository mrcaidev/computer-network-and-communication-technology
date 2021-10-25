/**
 *  @file   coding.cpp
 *  @brief  编解码相关函数。
 *  @author 蔡与望
 */
#pragma once
#include <iostream>
#include <windows.h>
#include "param.h"
using namespace std;

/**
 *  @brief  将十进制数转化为指定位数的01字符串。
 *  @param  dec     十进制整型数。
 *  @param  bits    指定的二进制字符串位数。
 *  @return 一个01字符串，如"00001001"。
 */
string decToBin(int dec, int bits) {
    string bin = "";
    // 除二取余法，直到原数为0并且达到指定位数。
    while (dec || bin.length() != bits) {
        bin.insert(0, to_string(dec % 2));
        dec /= 2;
    }
    return bin;
}

/**
 *  @brief  将二进制字符串转化为十进制数。
 *  @param  bin 二进制字符串。
 *  @return 一个十进制整型数，如9。
 */
int binToDec(string bin) {
    int dec = 0;
    // 移位法。
    for (int i = 0; i < bin.length(); i++) {
        dec = (dec << 1) + bin[i] - '0';
    }
    return dec;
}

/**
 *  @brief  将含有Unicode的字符串编码为01字符串。
 *  @param  message 原字符串。
 *  @return 一个01字符串，代表编码后的消息。
 */
string encode(string message) {
    string secret = "";
    unsigned short decArr[MAX_CHAR_NUM] = {0};
    // 将字符串转为Unicode码。
    int len =
        MultiByteToWideChar(CP_ACP, 0, (LPCCH)message.c_str(), -1, nullptr, 0);
    MultiByteToWideChar(CP_ACP, 0, (LPCCH)message.c_str(), -1, (LPWSTR)decArr,
                        len);
    // 将每个Unicode码转为对应的16位01字符串。
    for (int i = 0; i < len - 1; i++) {
        secret += decToBin(decArr[i], BITS_PER_CHAR);
    }
    return secret;
}

/**
 *  @brief  将01字符串解码为含Unicode的字符串。
 *  @param  secret  原01字符串。
 *  @return 一个含有Unicode的字符串。
 */
string decode(string secret) {
    unsigned short decArr[MAX_CHAR_NUM] = {0};
    // 将01字符串每16位视作一个Unicode码。
    for (int i = 0; i < secret.length() / BITS_PER_CHAR; i++) {
        string bin = secret.substr(i * BITS_PER_CHAR, BITS_PER_CHAR);
        decArr[i] = binToDec(bin);
    }
    // 将Unicode码转为对应的字符串。
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