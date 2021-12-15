from base64 import b64decode, b64encode
from re import findall

BITS_PER_ASCII = 8
BITS_PER_UNICODE = 16


def string_to_bits(string: str) -> str:
    """将01字符串转换为01比特流。

    Args:
        string: 01字符串。

    Returns:
        转换后的01比特流。
    """
    return "".join(list(map(lambda char: chr(ord(char) - ord("0")), string)))


def bits_to_string(bits: str) -> str:
    """将01比特流转换为01字符串。

    Args:
        bits: 01比特流。

    Returns:
        转换后的01字符串。
    """
    return "".join(list(map(lambda bit: chr(ord(bit) + ord("0")), bits)))


def encode_ascii(ascii: str) -> str:
    """将ASCII字符编码为01字符串。

    Args:
        ascii: 要编码的ASCII字符。

    Returns:
        编码所得的01字符串。
    """
    return "".join(
        str(bin(ord(char)))[2:].zfill(BITS_PER_ASCII) for char in ascii
    )


def decode_ascii(binary: str) -> str:
    """将01字符串解码为ASCII字符。

    Args:
        binary: 要解码的01字符串。

    Returns:
        解码所得的ASCII字符。
    """
    return "".join(
        [
            chr(int(char, 2))
            for char in findall(f".{{{BITS_PER_ASCII}}}", binary)
        ]
    )


def encode_unicode(unicode: str) -> str:
    """将Unicode字符编码为01字符串。

    Args:
        unicode: 要编码的Unicode字符。

    Returns:
        编码所得的01字符串。
    """
    return "".join(
        str(bin(ord(char)))[2:].zfill(BITS_PER_UNICODE) for char in unicode
    )


def decode_unicode(binary: str) -> str:
    """将01字符串解码为Unicode字符。

    Args:
        binary: 要解码的01字符串。

    Returns:
        解码所得的Unicode字符。
    """
    return "".join(
        [
            chr(int(char, 2))
            for char in findall(f".{{{BITS_PER_UNICODE}}}", binary)
        ]
    )


def encode_file(filepath: str) -> str:
    """将文件编码为01字符串。

    Args:
        filename: 要编码的文件的绝对路径。

    Returns:
        编码所得的01字符串。
    """
    with open(filepath, mode="rb") as fr:
        secret = b64encode(fr.read()).decode("utf-8")
    return encode_ascii(secret)


def decode_file(binary: str) -> tuple[bytes, bool]:
    """将01字符串解码为文件。

    Args:
        binary: 要解码的01字符串。

    Returns:
        - [0] 解码所得的文件的字节串。
        - [1] 是否成功解码，成功为`True`，失败为`False`。
    """
    try:
        data = b64decode(decode_ascii(binary).encode("utf-8"))
    except Exception:
        return b"", False
    else:
        return data, True


if __name__ == "__main__":
    message = "Hello"

    message_bits = string_to_bits(message)
    message_string = bits_to_string(message_bits)
    print(f"{message_bits=}")
    print(f"{message_string=}")

    ascii_encoded = encode_ascii(message)
    ascii_decoded = decode_ascii(ascii_encoded)
    print(f"{ascii_encoded=}")
    print(f"{ascii_decoded=}")

    unicode_encoded = encode_unicode(message)
    unicode_decoded = decode_unicode(unicode_encoded)
    print(f"{unicode_encoded=}")
    print(f"{unicode_decoded=}")
