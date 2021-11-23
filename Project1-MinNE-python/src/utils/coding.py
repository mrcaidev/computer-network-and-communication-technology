import base64
import re


def dec_to_bin(decimal: int, length: int) -> str:
    """
    将十进制转换为二进制。

    Args:
        decimal: 十进制整型数。
        length: 转换后的二进制字符串长度。

    Returns:
        二进制字符串。
    """
    if decimal >= 0:
        return bin(decimal)[2:].zfill(length)
    else:
        return f"1{bin(decimal)[3:].zfill(length-1)}"


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
        return 0
    else:
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


def encode_text(string: str) -> str:
    """
    将文本编码为01字符串。

    Args:
        string: 要编码的文本。

    Returns:
        编码所得的01字符串。
    """
    return "".join(str(bin(ord(char)))[2:].zfill(16) for char in string)


def decode_text(binary: str) -> str:
    """
    将01字符串解码为文本。

    Args:
        binary: 要解码的01字符串。

    Returns:
        解码所得的文本。
    """
    return "".join([chr(int(char, 2)) for char in re.findall(".{16}", binary)])


def encode_file(filepath: str) -> str:
    """
    将文件编码为01字符串。

    Args:
        filename: 要编码的文件的绝对路径。

    Returns:
        编码所得的01字符串。
    """
    with open(filepath, mode="rb") as fr:
        secret = base64.b64encode(fr.read()).decode("utf-8")
    return "".join(str(bin(ord(char)))[2:].zfill(8) for char in secret)


def decode_file(binary: str) -> bytes:
    """
    将01字符串解码为文件。

    Args:
        binary: 要解码的01字符串。

    Returns:
        解码所得的文件的字节串。
    """
    try:
        img_bytes = base64.b64decode(
            "".join([chr(int(char, 2)) for char in re.findall(".{8}", binary)]).encode(
                "utf-8"
            )
        )
    except Exception:
        return b""
    else:
        return img_bytes
