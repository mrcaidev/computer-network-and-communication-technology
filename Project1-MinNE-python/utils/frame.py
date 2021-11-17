from utils.coding import *
from utils.param import Constant as const


class Frame:
    """报文帧。"""

    def __init__(self) -> None:
        """初始化帧属性为默认值。"""
        self.__src = 0
        self.__seq = 0
        self.__data = ""
        self.__dst = 0
        self.__checksum = 0
        self.__verified = True
        self.__binary = ""

    def __str__(self) -> str:
        return f"[Frame {self.__seq}] ({self.__src}→{self.__dst}, {self.__verified}) {self.__data}"

    @property
    def src(self):
        return self.__src

    @property
    def seq(self):
        return self.__seq

    @property
    def data(self):
        return self.__data

    @property
    def dst(self):
        return self.__dst

    @property
    def binary(self):
        return self.__binary

    @property
    def verified(self):
        return self.__verified

    def read(self, raw: str) -> None:
        self.__verified = True
        self.__binary = raw
        message = self.extract_message(raw)

        self.__src = bin_to_dec(message[: const.PORT_LEN])
        self.__seq = bin_to_dec(
            message[const.PORT_LEN : const.PORT_LEN + const.SEQ_LEN]
        )
        self.__checksum = bin_to_dec(message[-const.CHECKSUM_LEN :])
        self.__dst = bin_to_dec(
            message[-const.CHECKSUM_LEN - const.PORT_LEN : -const.CHECKSUM_LEN]
        )
        self.__data = message[
            const.PORT_LEN + const.SEQ_LEN : -const.CHECKSUM_LEN - const.PORT_LEN
        ]
        # 如果extract_message()就出错，那结果必为错；
        # 如果extract_message()没出错，那就进一步检验校验和。
        self.__verified = (
            self.__verified
            and self.__checksum
            == Frame.generate_checksum(message[: -const.CHECKSUM_LEN])
        )

    def write(self, src: int, seq: int, data: str, dst: int) -> None:
        self.__src = src
        self.__seq = seq
        self.__data = data
        self.__dst = dst
        target = f"{dec_to_bin(src, const.PORT_LEN)}{dec_to_bin(seq, const.SEQ_LEN)}{data}{dec_to_bin(dst, const.PORT_LEN)}"
        self.__checksum = Frame.generate_checksum(target)
        self.__verified = True
        self.__binary = Frame.add_locator(
            f"{target}{dec_to_bin(self.__checksum, const.CHECKSUM_LEN)}"
        )

    def extract_message(self, raw: str) -> str:
        message = ""

        # 寻找帧头。
        start = raw.find(const.LOCATOR)
        # 异常一：帧头帧尾同时出错，程序找不到定位串，就提前返回空消息。
        if start == -1:
            self.__verified = False
            return const.EMPTY_FRAME

        # 反变换。
        start += const.LOCATOR_LEN
        next = raw.find(const.SUSPICIOUS, start)
        while next != -1:
            if raw[next + const.SUSPICIOUS_LEN] == "1":
                # 到达帧尾。
                message += raw[start : next - 1]
                return message
            else:
                # 删除后面的0，然后继续寻找。
                message += raw[start : next + const.SUSPICIOUS_LEN]
                start = next + const.SUSPICIOUS_LEN + 1
                next = raw.find(const.SUSPICIOUS, start)

        # 程序会走到这里，说明只找到了一个定位串。提前设verify=False。
        self.__verified = False
        # 异常二：帧头出错，帧尾没错，程序会误认为帧尾是帧头。此时message为空。
        # 异常三：帧头没错，帧尾出错。此时message不为空，但有可能已经写入了帧外乱码，不能相信。
        # 无论如何都应该返回空帧。
        return const.EMPTY_FRAME

    def transform(message: str) -> str:
        cur = message.find(const.SUSPICIOUS)
        while cur != -1:
            message = f"{message[: cur + const.SUSPICIOUS_LEN]}0{message[cur + const.SUSPICIOUS_LEN :]}"
            cur = message.find(const.SUSPICIOUS, cur + 6)
        return message

    def add_locator(message: str) -> str:
        return f"{const.LOCATOR}{Frame.transform(message)}{const.LOCATOR}"

    def generate_checksum(target: str) -> int:
        return sum(
            [bin_to_dec(target[i * 8 : i * 8 + 8]) for i in range(len(target) // 8)]
        )

    def calcTotal(length: int) -> int:
        return (
            length // const.DATA_LEN
            if length % const.DATA_LEN == 0
            else length // const.DATA_LEN + 1
        )
