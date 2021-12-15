def dec_to_bin(decimal: int, length: int) -> str:
    """将十进制数转换为对应的 01 字符串。

    Args:
        decimal: 十进制整型数。
        length: 转换后的 01 字符串长度。

    Returns:
        转换所得的 01 字符串。
    """
    if decimal >= 0:
        return bin(decimal)[2:].zfill(length)
    else:
        return f"1{bin(decimal)[3:].zfill(length-1)}"


def bin_to_dec(binary: str) -> int:
    """将 01 字符串转换为对应十进制数。

    Args:
        binary: 01 字符串。

    Returns:
        转换所得的十进制整型数。如果转换出错，就返回 0。
    """
    try:
        decimal = int(binary, 2)
    except Exception:
        return 0
    else:
        return decimal


def generate_crc(binary: str) -> int:
    """对任意长的 01 字符串生成 CRC-16 校验码。

    Args:
        binary: 任意 01 字符串。

    Returns:
        CRC-16 校验码对应的整型数。
    """
    cur = 0xFFFF
    poly = 0xA001
    for byte in hex(int(binary, 2))[2:]:
        cur ^= ord(byte)
        for _ in range(8):
            last = cur % 2
            cur >>= 1
            if last == 1:
                cur ^= poly
    return cur


class FrameParam:
    """帧参数。"""

    LOCATOR = "01111110"
    SUSPICIOUS = "11111"

    LOCATOR_LEN = 8
    SUSPICIOUS_LEN = 5
    PORT_LEN = 16
    SESSION_LEN = 2
    REPLY_LEN = 1
    SEQ_LEN = 1
    DATA_LEN = 32
    CRC_LEN = 16
    HEAD_LEN = PORT_LEN + SESSION_LEN + REPLY_LEN + SEQ_LEN
    TAIL_LEN = PORT_LEN + CRC_LEN


class SessionState:
    """当前会话状态。"""

    NORMAL = "00"
    FIN = "01"
    REQ_TXT = "10"
    REQ_IMG = "11"
    REQ_LIST = (REQ_TXT, REQ_IMG)


class ReplyState:
    ACK = "1"
    NAK = "0"


class Frame:
    """报文帧信息。"""

    def __init__(self, **kwargs) -> None:
        self.src = kwargs.get("src", "X")
        self.session_state = kwargs.get("session_state", "X")
        self.reply_state = kwargs.get("reply_state", "X")
        self.seq = kwargs.get("seq", 0)
        self.data = kwargs.get("data", "")
        self.dst = kwargs.get("dst", "X")

        self.binary = kwargs.get("binary", "")
        self.verified = kwargs.get("verified", False)
        self.length = kwargs.get("length", 0)

    def __str__(self) -> str:
        """打印帧信息。"""
        return f"[Frame {self.seq}] ({self.src}->{self.dst},{self.session_state}/{self.reply_state}) {self.data}"

    @staticmethod
    def calc_num(message: str) -> int:
        """计算消息需要分几帧发送。

        Args:
            message: 要发送的消息。

        Returns:
            计算所得的帧数。
        """
        length = len(message)
        return (
            length // FrameParam.DATA_LEN
            if length % FrameParam.DATA_LEN == 0
            else length // FrameParam.DATA_LEN + 1
        )


class FrameBuilder:
    """帧建造者。"""

    def __init__(self) -> None:
        self.__src = "0"
        self.__session_state = SessionState.NORMAL
        self.__reply_state = ReplyState.ACK
        self.__seq = 0
        self.__data = ""
        self.__dst = "0"

    def __set_src(self, src: str) -> None:
        """设置源端口。

        Args:
            src: 该帧的源端口。
        """
        self.__src = src if src != None else self.__src
        self.__binary += dec_to_bin(int(self.__src), FrameParam.PORT_LEN)

    def __set_session_state(self, session_state: str) -> None:
        """设置会话状态。

        Args:
            session_state: 会话状态，见 `SessionState`。
        """
        self.__session_state = (
            session_state if session_state != None else self.__session_state
        )
        self.__binary += self.__session_state

    def __set_reply_state(self, reply_state: str) -> None:
        """设置回复状态。

        Args:
            reply_state: 回复状态，见 `ReplyState`。
        """
        self.__reply_state = reply_state if reply_state != None else self.__reply_state
        self.__binary += self.__reply_state

    def __set_seq(self, step_seq: bool) -> None:
        """设置序号。

        Args:
            step_seq: 该次需递增序号为 `True`，不递增为 `False`。
        """
        self.__seq = int(not self.__seq) if step_seq else self.__seq
        self.__binary += dec_to_bin(self.__seq, FrameParam.SEQ_LEN)

    def __set_data(self, data: str) -> None:
        """设置数据。

        Args:
            data: 该帧中封装的数据。
        """
        self.__data = data if data != None else self.__data
        self.__binary += self.__data

    def __set_dst(self, dst: str) -> None:
        """设置目标端口。

        Args:
            dst: 该帧的目标端口。
        """
        self.__dst = dst if dst != None else self.__dst
        self.__binary += dec_to_bin(int(self.__dst), FrameParam.PORT_LEN)

    def __apply_crc(self) -> None:
        """生成 CRC-16 校验码。"""
        crc = generate_crc(self.__binary)
        self.__binary += dec_to_bin(crc, FrameParam.CRC_LEN)

    def __add_locator(self) -> None:
        """在帧前后添加定位串。"""
        pos = self.__binary.find(FrameParam.SUSPICIOUS)
        while pos != -1:
            self.__binary = f"{self.__binary[: pos + FrameParam.SUSPICIOUS_LEN]}0{self.__binary[pos + FrameParam.SUSPICIOUS_LEN :]}"
            pos = self.__binary.find(FrameParam.SUSPICIOUS, pos + 6)

        self.__binary = f"{FrameParam.LOCATOR}{self.__binary}{FrameParam.LOCATOR}"

    def build(self, step_seq: bool = True, **kwargs) -> Frame:
        """建造帧。

        如果没有指定某项属性的更改，则序号默认递增，其余属性默认不变。

        Args:
            step_seq: 该次需递增序号为 `True`，不递增为 `False`。
            **kwargs: 其它帧属性。
            - src: 该帧的源端口；
            - session_state: 当前会话状态；
            - reply_state: 回复状态；
            - data: 该帧封装的数据；
            - dst: 该帧的目标端口。

        Returns:
            建造所得的帧。
        """
        self.__binary = ""
        self.__set_src(kwargs.get("src", None))
        self.__set_session_state(kwargs.get("session_state", None))
        self.__set_reply_state(kwargs.get("reply_state", None))
        self.__set_seq(step_seq)
        self.__set_data(kwargs.get("data", None))
        self.__set_dst(kwargs.get("dst", None))
        self.__apply_crc()
        self.__add_locator()

        return Frame(
            src=self.__src,
            session_state=self.__session_state,
            reply_state=self.__reply_state,
            seq=self.__seq,
            data=self.__data,
            dst=self.__dst,
            binary=self.__binary,
            verified=True,
            length=len(self.__binary),
        )


class FrameParser:
    """帧解析者。"""

    def __init__(self) -> None:
        pass

    def __get_src(self) -> None:
        """获取该帧的源端口。"""
        self.__src = str(bin_to_dec(self.__message[: FrameParam.PORT_LEN]))

    def __get_session_state(self) -> None:
        """获取当前会话状态。"""
        self.__session_state = self.__message[
            FrameParam.PORT_LEN : FrameParam.PORT_LEN + FrameParam.SESSION_LEN
        ]

    def __get_reply_state(self) -> None:
        """获取回复状态。"""
        self.__reply_state = self.__message[
            FrameParam.PORT_LEN + FrameParam.SESSION_LEN
        ]

    def __get_seq(self) -> None:
        """获取序号。"""
        self.__seq = bin_to_dec(self.__message[FrameParam.HEAD_LEN - 1])

    def __get_data(self) -> None:
        """获取该帧中封装的数据。"""
        self.__data = self.__message[FrameParam.HEAD_LEN : -FrameParam.TAIL_LEN]

    def __get_dst(self) -> None:
        """获取该帧的目标端口。"""
        self.__dst = str(
            bin_to_dec(self.__message[-FrameParam.TAIL_LEN : -FrameParam.CRC_LEN])
        )

    def __check_crc(self) -> None:
        """CRC-16 检验。"""
        actual_crc = bin_to_dec(self.__message[-FrameParam.CRC_LEN :])
        assumed_crc = generate_crc(self.__message[: -FrameParam.CRC_LEN])
        self.__verified = True if actual_crc == assumed_crc else False

    def parse(self, binary: str) -> Frame:
        """解析帧。

        Args:
            binary: 原始 01 字符串。

        Returns:
            解析所得的帧。
        """
        self.__message = FrameParser.__extract_message(binary)
        if not self.__message:
            return Frame()

        self.__get_src()
        self.__get_session_state()
        self.__get_reply_state()
        self.__get_seq()
        self.__get_data()
        self.__get_dst()
        self.__check_crc()

        return Frame(
            src=self.__src,
            session_state=self.__session_state,
            reply_state=self.__reply_state,
            seq=self.__seq,
            data=self.__data,
            dst=self.__dst,
            binary=binary,
            verified=self.__verified,
            length=len(binary),
        )

    @staticmethod
    def __extract_message(binary: str) -> str:
        """从 01 字符串中提取帧。

        Args:
            binary: 有外界干扰的 01 字符串。

        Returns:
            - 提取出的信息。如果提取失败则为""。
        """
        message = ""
        start = binary.find(FrameParam.LOCATOR)

        # 如果没找到定位串，就返回空帧。
        if start == -1:
            return ""

        # 向后反变换。
        start += FrameParam.LOCATOR_LEN
        susp = binary.find(FrameParam.SUSPICIOUS, start)
        while susp != -1:
            # 如果下标上溢，说明帧有问题。
            try:
                after_susp = binary[susp + FrameParam.SUSPICIOUS_LEN]
            except IndexError:
                return ""

            # 如果到达帧尾，就返回提取出的信息。
            if after_susp == "1":
                message += binary[start : susp - 1]
                return message

            # 如果只是连续5个1，就删除后面的0，然后继续寻找。
            else:
                message += binary[start : susp + FrameParam.SUSPICIOUS_LEN]
                start = susp + FrameParam.SUSPICIOUS_LEN + 1
                susp = binary.find(FrameParam.SUSPICIOUS, start)

        # 如果只找到了1个定位串，也返回空帧。
        return ""


if __name__ == "__main__":
    builder = FrameBuilder()
    parser = FrameParser()

    send_frame = builder.build(
        step_seq=False,
        src="11300",
        session_state=SessionState.REQ_TXT,
        reply_state=ReplyState.ACK,
        data="11111111",
        dst="12300",
    )
    print(f"send_frame: {send_frame}")

    send_frame = builder.build(reply_state=ReplyState.NAK, dst="14300")
    print(f"send_frame: {send_frame}")

    recv_frame = parser.parse(send_frame.binary)
    print(f"recv_frame: {recv_frame}")
