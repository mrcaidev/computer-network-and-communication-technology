import utils.constant as const
from utils.coding import *


class Frame:
    """报文帧。"""

    def __init__(self) -> None:
        """初始化帧属性为默认值。"""
        self.__src = ""
        self.__seq = 0
        self.__data = ""
        self.__dst = ""
        self.__crc = 0
        self.__verified = True
        self.__binary = ""
        self.__length = 0

    def __str__(self) -> str:
        """打印帧信息。"""
        return f"[Frame {self.__seq}] ({self.__src}→{self.__dst}, {self.__verified}) {self.__data}"

    @property
    def src(self) -> str:
        """将源地址设为只读。"""
        return self.__src

    @property
    def seq(self) -> int:
        """将序号设为只读。"""
        return self.__seq

    @property
    def data(self) -> str:
        """将封装数据设为只读。"""
        return self.__data

    @property
    def dst(self) -> str:
        """将目的地址设为只读。"""
        return self.__dst

    @property
    def verified(self) -> bool:
        """将检验结果设为只读。"""
        return self.__verified

    @property
    def binary(self) -> str:
        """将帧对应的01序列设为只读。"""
        return self.__binary

    @property
    def length(self) -> str:
        """将帧长度设为只读。"""
        return self.__length

    def write(self, info: dict) -> None:
        """
        将信息写入帧。

        Args:
            info: 包含帧信息的字典，必须包含以下几个键：
            - src: 帧的源端口。
            - seq: 帧的序号。
            - data: 要封装的消息。
            - dst: 帧的目的端口。
        """
        # 存储参数。
        self.__src = info["src"]
        self.__seq = info["seq"]
        self.__data = info["data"]
        self.__dst = info["dst"]

        # 生成CRC码。
        crc_target = f"{dec_to_bin(int(self.__src), const.Frame.PORT_LEN)}{dec_to_bin(self.__seq, const.Frame.SEQ_LEN)}{self.__data}{dec_to_bin(int(self.__dst), const.Frame.PORT_LEN)}"
        self.__crc = Frame.__generate_crc(crc_target)
        self.__verified = True

        # 生成01序列。
        self.__binary = Frame.__add_locator(
            f"{crc_target}{dec_to_bin(self.__crc, const.Frame.CRC_LEN)}"
        )
        self.__length = len(self.__binary)

    def read(self, binary: str) -> None:
        """
        读入01序列，解析为帧。

        Args:
            binary: 物理层中传输的01序列字符串。
        """
        message, extracted = Frame.__extract_message(binary)

        self.__src = str(bin_to_dec(message[: const.Frame.PORT_LEN]))
        self.__seq = bin_to_dec(
            message[const.Frame.PORT_LEN : const.Frame.PORT_LEN + const.Frame.SEQ_LEN]
        )
        self.__data = message[
            const.Frame.PORT_LEN
            + const.Frame.SEQ_LEN : -const.Frame.CRC_LEN
            - const.Frame.PORT_LEN
        ]
        self.__dst = str(
            bin_to_dec(
                message[
                    -const.Frame.CRC_LEN - const.Frame.PORT_LEN : -const.Frame.CRC_LEN
                ]
            )
        )
        self.__crc = bin_to_dec(message[-const.Frame.CRC_LEN :])
        self.__verified = extracted and self.__crc == Frame.__generate_crc(
            message[: -const.Frame.CRC_LEN]
        )
        self.__binary = binary
        self.__length = len(message) + 2 * const.Frame.LOCATOR_LEN

    def __extract_message(binary: str) -> tuple[str, bool]:
        """
        从有干扰的01序列中提取帧序列。

        Args:
            binary: 物理层中传输的01序列字符串。

        Returns:
            一个二元元组。
            - [0] 提取的帧序列。
            - [1] 是否提取成功，成功为True，失败为False。
        """
        message = ""
        start = binary.find(const.Frame.LOCATOR)

        # 如果没找到定位串，就返回空帧。
        if start == -1:
            return const.Frame.EMPTY_FRAME, False

        # 向后反变换。
        start += const.Frame.LOCATOR_LEN
        susp = binary.find(const.Frame.SUSPICIOUS, start)
        while susp != -1:
            # 如果到达帧尾，就返回提取出的信息。
            if binary[susp + const.Frame.SUSPICIOUS_LEN] == "1":
                message += binary[start : susp - 1]
                return message, True
            # 如果只是连续5个1，就删除后面的0，然后继续寻找。
            else:
                message += binary[start : susp + const.Frame.SUSPICIOUS_LEN]
                start = susp + const.Frame.SUSPICIOUS_LEN + 1
                susp = binary.find(const.Frame.SUSPICIOUS, start)

        # 如果只找到了1个定位串，也返回空帧。
        return const.Frame.EMPTY_FRAME, False

    def __add_locator(binary: str) -> str:
        """
        变换01序列，并加上定位串。

        Args:
            binary: 待操作的01序列，包含帧内的所有信息。

        Returns:
            加上定位串后的01序列。
        """
        # 变换，在连续的5个`1`之后添加1个`0`。
        cur = binary.find(const.Frame.SUSPICIOUS)
        while cur != -1:
            binary = f"{binary[: cur + const.Frame.SUSPICIOUS_LEN]}0{binary[cur + const.Frame.SUSPICIOUS_LEN :]}"
            cur = binary.find(const.Frame.SUSPICIOUS, cur + 6)

        return f"{const.Frame.LOCATOR}{binary}{const.Frame.LOCATOR}"

    def __generate_crc(binary: str) -> int:
        """
        生成CRC校验码。

        Args:
            binary: 要对其生成CRC校验码的01序列。

        Returns:
            16位CRC校验码，以十进制整型形式返回。
        """
        poly = 0xFFFF
        try:
            bytes_array = bytearray.fromhex(hex(int(binary, 2))[2:])
        except Exception:
            return -1
        for byte in bytes_array:
            poly ^= byte
            for _ in range(8):
                if poly & 1 != 0:
                    poly >>= 1
                    poly ^= 0xA001
                else:
                    poly >>= 1
        return ((poly & 0xFF) << 8) + (poly >> 8)

    def calc_frame_num(message: str) -> int:
        """
        计算消息需要分几帧发送。

        Args:
            message: 当前要发送的消息。

        Returns:
            计算所得的帧数。
        """
        length = len(message)
        return (
            length // const.Frame.DATA_LEN
            if length % const.Frame.DATA_LEN == 0
            else length // const.Frame.DATA_LEN + 1
        )
