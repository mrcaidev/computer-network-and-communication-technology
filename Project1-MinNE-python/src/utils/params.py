class Constant:
    """常数。"""

    BITS_PER_ASCII = 8
    BITS_PER_UNICODE = 16


class File:
    """目录与文件。"""

    CONFIG_DIR = "config"
    RSC_DIR = "resource"

    BATCH_DIR = "batch-backup"
    DEVICEMAP_DIR = "devicemap-backup"
    NE_DIR = "ne-backup"

    BATCH = "batch"
    DEVICEMAP = "devicemap"
    NE = "ne"

    FULL_TIME = "datetime.now().strftime('%H:%M:%S.%f')[:-3]"
    ABBR_TIME = "datetime.now().strftime('%H-%M-%S')"


class FramePack:
    """帧封装。"""

    LOCATOR = "01111110"
    SUSPICIOUS = "11111"

    LOCATOR_LEN = 8
    SUSPICIOUS_LEN = 5
    PORT_LEN = 16
    SEQ_LEN = 8
    DATA_LEN = 32
    CRC_LEN = 16

    ACK = "Y"
    NAK = "N"
    EMPTY_FRAME = "0" * 88


class MessageType:
    """消息类型。"""

    TEXT = "1"
    FILE = "2"


class Mode:
    """发送模式。"""

    UNICAST = "1"
    BROADCAST = "2"


class Network:
    """通信网络约束。"""

    INTER_NE_BUFSIZE = 1024
    IN_NE_BUFSIZE = 8 * 1024 * 1024
    MESSAGE_MAX_LEN = IN_NE_BUFSIZE // Constant.BITS_PER_UNICODE

    USER_TIMEOUT = 180
    SELECT_TIMEOUT = 0.5
    RECV_TIMEOUT = 0.5
    FLOW_INTERVAL = 0.02

    KEEPALIVE_MAX_RETRY = 8

    REMOTE_MAX_LIFE = 100

    ROUTER_SPREAD_INTERVAL = 10


class Topology:
    """网络拓扑。"""

    CMD_PORT = "20000"
    BROADCAST_PORT = "65535"
