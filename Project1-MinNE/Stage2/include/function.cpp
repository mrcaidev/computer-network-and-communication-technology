#include <iostream>
#include <cmath>
using namespace std;

string charToBin(char ascii) {
    string bin = "";
    int asciiNum = int(ascii);
    while (asciiNum || bin.length() != 8) {
        bin.insert(0, to_string(asciiNum % 2));
        asciiNum /= 2;
    }
    return bin;
}

char binToChar(string bin) {
    int len = bin.length();
    int sum = 0;
    for (int i = 0; i <= len - 1; i++) {
        if (bin[i] == '0')
            continue;
        sum += pow(2.0, len - 1 - i);
    }
    return char(sum);
}
