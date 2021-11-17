class Constant:
    """程序会用到的各种常数。"""

    MAX_BUFFER_SIZE = 1024
    MAX_CHAR_NUM = 50
    FLOW_INTERVAL = 0.1
    USER_TIMEOUT = 60
    RECV_TIMEOUT = 5
    SELECT_TIMEOUT = 0.5
    KEEPALIVE_CNT = 3

    LOCATOR = "01111110"
    SUSPICIOUS = "11111"
    ACK = "Y"
    NAK = "N"
    EMPTY_FRAME = "0" * 88
    BROADCAST_PORT = 65535

    BITS_PER_CHAR = 16
    HOST_PER_SWITCHER = 2
    SWITCHER_PER_ROUTER = 2
    BROADCAST_RECVER_NUM = 3
    LOCATOR_LEN = 8
    SUSPICIOUS_LEN = 5
    PORT_LEN = 16
    SEQ_LEN = 8
    CHECKSUM_LEN = 16
    DATA_LEN = 32

    RECV = "1"
    UNICAST = "2"
    BROADCAST = "3"
    QUIT = "4"
