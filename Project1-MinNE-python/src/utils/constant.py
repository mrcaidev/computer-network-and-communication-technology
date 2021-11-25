class File:
    """目录与文件。"""

    CONFIG_DIR = "config"
    LOG_DIR = "log"
    RSC_DIR = "resource"
    DEVICE_MAP = "device_map.json"
    ROUTER_ENV = "router_env.json"
    LOG = "log.txt"
    FULL_TIME = "datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]"
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


class InputType:
    """用户输入类型。"""

    MODE = 1
    DST = 2
    MSGTYPE = 3
    TEXT = 4
    FILE = 5


class MessageType:
    """消息类型。"""

    TEXT = "1"
    FILE = "2"
    LIST = (TEXT, FILE)


class Mode:
    """网元模式。"""

    RECEIVE = "1"
    UNICAST = "2"
    BROADCAST = "3"
    QUIT = "4"
    LIST = (RECEIVE, UNICAST, BROADCAST, QUIT)


class Network:
    """通信网络约束。"""

    INTER_NE_BUFSIZE = 1024
    IN_NE_BUFSIZE = 8 * 1024 * 1024

    USER_TIMEOUT = 180
    SELECT_TIMEOUT = 0.5
    RECV_TIMEOUT = 0.15
    FLOW_INTERVAL = 0.03

    KEEPALIVE_MAX_RETRY = 8

    REMOTE_MAX_LIFE = 100


class Topology:
    """网络拓扑。"""

    BROADCAST_RECVER_NUM = 1
    BROADCAST_PORT = "65535"
    DEFAULT_ROUTER = "1"
    ROUTER_NUM = 3
