import os
from json import loads

from layer.net import NetLayer


class NetEntity(NetLayer):
    """主机网络层实体。"""

    def __init__(self, port: str) -> None:
        super().__init__(port)
