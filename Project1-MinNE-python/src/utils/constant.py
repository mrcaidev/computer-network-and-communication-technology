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

    MAX_BUFFER_SIZE = 1024

    FLOW_INTERVAL = 0.1
    USER_TIMEOUT = 180
    RECV_TIMEOUT = 3
    SELECT_TIMEOUT = 0.5
    KEEPALIVE_MAX_RETRY = 5

    REMOTE_LIFE = 5
