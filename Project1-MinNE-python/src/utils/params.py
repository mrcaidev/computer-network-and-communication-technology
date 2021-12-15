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
