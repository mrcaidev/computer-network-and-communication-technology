import base64
import os
import re

from utils.constant import File


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


def encode_text(string: str) -> str:
    """
    将用户消息编码为二进制。

    Args:
        string: 要编码的Unicode消息。

    Returns:
        编码所得的二进制字符串。
    """
    return "".join(str(bin(ord(char)))[2:].zfill(16) for char in string)


def decode_text(binary: str) -> str:
    """
    将二进制解码为可理解的信息。

    Args:
        binary: 要解码的二进制字符串。

    Returns:
        解码所得的消息。
    """
    return "".join([chr(int(char, 2)) for char in re.findall(".{16}", binary)])


def encode_picture(filepath: str) -> str:
    """
    将图片编码为二进制。

    Args:
        filename: 图片绝对路径。

    Returns:
        编码所得的二进制字符串。
    """
    with open(filepath, "rb") as fr:
        secret = base64.b64encode(fr.read()).decode("utf-8")
    return "".join(str(bin(ord(char)))[2:].zfill(8) for char in secret)


def decode_picture(binary: str) -> bool:
    """
    将二进制解码为图片。

    Args:
        binary: 要解码的二进制字符串。

    Returns:
        是否成功解码，成功为True，失败为False。
    """
    # 解码字符串。
    try:
        img_bytes = base64.b64decode(
            "".join([chr(int(char, 2)) for char in re.findall(".{8}", binary)]).encode(
                "utf-8"
            )
        )
    except Exception:
        return False

    # 写入图片。
    try:
        with open(
            os.path.join(os.path.dirname(os.getcwd()), File.IMAGE_DIR, "received.png"),
            mode="wb",
        ) as fw:
            fw.write(img_bytes)
    except Exception:
        return False
    else:
        return True
