import re


def dec_to_bin(decimal: int, length: int) -> str:
    """
    将十进制转换为二进制。

    Args:
        decimal: 十进制整型数。
        bits: 转换后的二进制字符串长度。

    Returns:
        二进制字符串。
    """
    return bin(decimal)[2:].zfill(length)


def bin_to_dec(binary: str) -> int:
    """
    将二进制转换为十进制。

    Args:
        binary: 二进制字符串。

    Returns:
        十进制整型数。
    """
    try:
        decimal = int(binary, 2)
    except Exception:
        decimal = 0
    return decimal


def string_to_bits(string: str) -> str:
    """
    将01字符串转换为01比特流。

    Args:
        string: 01字符串。

    Returns:
        转换后的01比特流。
    """
    return "".join(list(map(lambda char: chr(ord(char) - ord("0")), string)))


def bits_to_string(bits: str) -> str:
    """
    将01比特流转换为01字符串。

    Args:
        bits: 01比特流。

    Returns:
        转换后的01字符串。
    """
    return "".join(list(map(lambda bit: chr(ord(bit) + ord("0")), bits)))


def encode(message: str) -> str:
    """
    将用户消息编码为二进制。

    Args:
        message: 要编码的Unicode消息。

    Returns:
        编码所得的二进制字符串。
    """
    return "".join(str(bin(ord(char)))[2:].zfill(16) for char in message)


def decode(binary: str) -> str:
    """
    将二进制解码为可理解的信息。

    Args:
        binary: 要解码的二进制字符串。

    Returns:
        解码所得的消息。
    """
    return "".join([chr(int(char, 2)) for char in re.findall(".{16}", binary)])
