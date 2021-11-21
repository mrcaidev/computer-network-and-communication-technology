class Topology:
    """网络拓扑参数。"""

    HOST_PER_SWITCHER = 2
    SWITCHER_PER_ROUTER = 2
    BROADCAST_RECVER_NUM = 1
    BROADCAST_PORT = "65535"


class Mode:
    """网元模式。"""

    RECV = "1"
    UNICAST = "2"
    BROADCAST = "3"
    QUIT = "4"
    LIST = (RECV, UNICAST, BROADCAST, QUIT)


class Frame:
    """帧参数。"""

    LOCATOR = "01111110"
    LOCATOR_LEN = 8
    SUSPICIOUS = "11111"
    SUSPICIOUS_LEN = 5
    PORT_LEN = 16
    SEQ_LEN = 8
    DATA_LEN = 32
    CRC_LEN = 16

    ACK = "Y"
    NAK = "N"
    EMPTY_FRAME = "0" * 88


class Network:
    """流控与超时。"""

    INTER_NE_BUFSIZE = 1024
    IN_NE_BUFSIZE = 8096
    FLOW_INTERVAL = 0.03
    USER_TIMEOUT = 180
    RECV_TIMEOUT = 0.2
    SELECT_TIMEOUT = 0.5
    KEEPALIVE_MAX_RETRY = 5

    REMOTE_MAX_LIFE = 100


class InputType:
    """用户输入分类。"""

    MODE = 1
    PORT = 2
    MESSAGE_TYPE = 3
    TEXT = 4
    FILENAME = 5


class MessageType:
    """消息分类。"""

    TEXT = "1"
    FILENAME = "2"
    LIST = (TEXT, FILENAME)


class Others:
    """杂项参数。"""

    IMAGE_DIR = "img"
