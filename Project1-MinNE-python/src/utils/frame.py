from utils.coding import bin_to_dec, dec_to_bin
from utils.params import FramePack


class Frame:
    """报文帧。

    实现了帧的封装与解封。
    """

    def __init__(self) -> None:
        """初始化帧属性为默认值。"""
        self.__src = ""
        self.__seq = 0
        self.__content = ""
        self.__dst = ""
        self.__crc = 0
        self.__verified = True
        self.__binary = ""
        self.__length = 0

    def __str__(self) -> str:
        """打印帧信息。"""
        return f"[Frame {self.__seq}] ({self.__src}→{self.__dst}) {self.__content}"

    @property
    def src(self) -> str:
        """将源地址设为只读。"""
        return self.__src

    @property
    def seq(self) -> int:
        """将序号设为只读。"""
        return self.__seq

    @property
    def content(self) -> str:
        """将封装数据设为只读。"""
        return self.__content

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
        """将帧对应的01字符串设为只读。"""
        return self.__binary

    @property
    def length(self) -> str:
        """将帧长度设为只读。"""
        return self.__length

    def write(self, info: dict) -> None:
        """将信息写入帧。

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
        self.__content = info["data"]
        self.__dst = info["dst"]

        # 生成CRC码。
        crc_target = f"{dec_to_bin(int(self.__src), FramePack.PORT_LEN)}{dec_to_bin(self.__seq, FramePack.SEQ_LEN)}{self.__content}{dec_to_bin(int(self.__dst), FramePack.PORT_LEN)}"
        self.__crc = Frame.__generate_crc(crc_target)
        self.__verified = True

        # 生成01字符串。
        self.__binary = Frame.__add_locator(
            f"{crc_target}{dec_to_bin(self.__crc, FramePack.CRC_LEN)}"
        )
        self.__length = len(self.__binary)

    def read(self, binary: str) -> None:
        """读入01字符串，解析为帧。

        Args:
            binary: 物理层中传输的01字符串。
        """
        message, extracted = Frame.__extract_message(binary)

        self.__src = str(bin_to_dec(message[: FramePack.PORT_LEN]))
        self.__seq = bin_to_dec(
            message[FramePack.PORT_LEN : FramePack.PORT_LEN + FramePack.SEQ_LEN]
        )
        self.__content = message[
            FramePack.PORT_LEN
            + FramePack.SEQ_LEN : -FramePack.CRC_LEN
            - FramePack.PORT_LEN
        ]
        self.__dst = str(
            bin_to_dec(
                message[-FramePack.CRC_LEN - FramePack.PORT_LEN : -FramePack.CRC_LEN]
            )
        )
        self.__crc = bin_to_dec(message[-FramePack.CRC_LEN :])
        self.__verified = extracted and self.__crc == Frame.__generate_crc(
            message[: -FramePack.CRC_LEN]
        )
        self.__binary = binary
        self.__length = len(message) + 2 * FramePack.LOCATOR_LEN

    @staticmethod
    def __extract_message(binary: str) -> tuple[str, bool]:
        """从有干扰的01字符串中提取帧序列。

        Args:
            binary: 物理层中传输的01字符串字符串。

        Returns:
            - [0] 提取的帧序列。
            - [1] 是否提取成功，成功为`True`，失败为`False`。
        """
        message = ""
        start = binary.find(FramePack.LOCATOR)

        # 如果没找到定位串，就返回空帧。
        if start == -1:
            return FramePack.EMPTY_FRAME, False

        # 向后反变换。
        start += FramePack.LOCATOR_LEN
        susp = binary.find(FramePack.SUSPICIOUS, start)
        while susp != -1:
            # 如果下标上溢，说明帧有问题。
            try:
                after_susp = binary[susp + FramePack.SUSPICIOUS_LEN]
            except IndexError:
                return FramePack.EMPTY_FRAME, False

            # 如果到达帧尾，就返回提取出的信息。
            if after_susp == "1":
                message += binary[start : susp - 1]
                return message, True

            # 如果只是连续5个1，就删除后面的0，然后继续寻找。
            else:
                message += binary[start : susp + FramePack.SUSPICIOUS_LEN]
                start = susp + FramePack.SUSPICIOUS_LEN + 1
                susp = binary.find(FramePack.SUSPICIOUS, start)

        # 如果只找到了1个定位串，也返回空帧。
        return FramePack.EMPTY_FRAME, False

    @staticmethod
    def __add_locator(binary: str) -> str:
        """变换01字符串，并加上定位串。

        Args:
            binary: 待操作的01字符串，包含帧内的所有信息。

        Returns:
            加上定位串后的01字符串。
        """
        # 变换，在连续的5个`1`之后添加1个`0`。
        cur = binary.find(FramePack.SUSPICIOUS)
        while cur != -1:
            binary = f"{binary[: cur + FramePack.SUSPICIOUS_LEN]}0{binary[cur + FramePack.SUSPICIOUS_LEN :]}"
            cur = binary.find(FramePack.SUSPICIOUS, cur + 6)

        return f"{FramePack.LOCATOR}{binary}{FramePack.LOCATOR}"

    @staticmethod
    def __generate_crc(binary: str) -> int:
        """生成CRC校验码。

        Args:
            binary: 要对其生成CRC校验码的01字符串。

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

    @staticmethod
    def calc_total(message: str) -> int:
        """计算消息需要分几帧发送。

        Args:
            message: 当前要发送的消息。

        Returns:
            计算所得的帧数。
        """
        length = len(message)
        return (
            length // FramePack.DATA_LEN
            if length % FramePack.DATA_LEN == 0
            else length // FramePack.DATA_LEN + 1
        )
