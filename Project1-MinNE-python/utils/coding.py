import re

from utils.param import Constant as const


def dec_to_bin(decimal: int, length: int) -> str:
    """
    将十进制转换为二进制。

    :param decimal: 十进制整型数。
    :param bits: 转换后的二进制字符串长度。
    :returns: 二进制字符串。
    """
    return bin(decimal)[2:].zfill(length)


def bin_to_dec(binary: str) -> int:
    """
    将二进制转换为十进制。

    :param binary: 二进制字符串。
    :returns: 十进制整型数。
    """
    return int(binary, 2)


def encode(message: str) -> str:
    """
    将用户消息编码为二进制。

    :param message: 要编码的Unicode消息。
    :returns: 编码所得的二进制字符串。
    """
    return "".join(
        str(bin(ord(char)))[2:].zfill(const.BITS_PER_CHAR) for char in message
    )


def decode(binary: str) -> str:
    """
    将二进制解码为可理解的信息。

    :param binary: 要解码的二进制字符串。
    :returns: 解码所得的消息。
    """
    return "".join(
        [
            chr(int(char, 2))
            for char in re.findall(f".{{{const.BITS_PER_CHAR}}}", binary)
        ]
    )


if __name__ == "__main__":
    message = input(">>> ")
    binary = encode(message)
    result = decode(binary)
    print(f"Message:{message}")
    print(f"Encoded:{binary}")
    print(f"Decoded:{result}")
