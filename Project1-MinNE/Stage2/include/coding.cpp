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

string encode(string message) {
    string secret = "";
    for (int i = 0; i < message.length(); i++) {
        secret.append(charToBin(message[i]));
    }
    return secret;
}

char binToChar(string bin) {
    int sum = 0;
    for (int i = 0; i < 8; i++) {
        if (bin[i] == '0')
            continue;
        sum += pow(2.0, 7 - i);
    }
    return char(sum);
}

string decode(char *secret) {
    string secretString = secret;
    string message = "";
    int len = secretString.length();
    for (int index = 0; index < len; index += 8) {
        string bin = secretString.substr(index, 8);
        char ascii = binToChar(bin);
        message.append(1, ascii);
    }
    return message;
}

// int main(int argc, char const *argv[]) {
//     string raw = "Hello";
//     string secret = encode(raw);
//     string message = decode(secret);
//     cout << "Secret: " << secret << endl;
//     cout << "Message: " << message << endl;
//     return 0;
// }
