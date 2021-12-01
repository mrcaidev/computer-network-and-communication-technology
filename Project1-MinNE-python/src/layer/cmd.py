from interface.cmd import CommandUI
from utils.params import *

from layer._abstract import AbstractLayer


class CommandLayer(AbstractLayer, CommandUI):
    """控制台。

    实现的消息收发：GUI->控制台->主机应用层。
    """

    def __init__(self) -> None:
        """初始化控制台。"""
        AbstractLayer.__init__(self, Topology.CMD_PORT)
        CommandUI.__init__(self)

    def __str__(self) -> str:
        """打印端口号。"""
        return f"[CMD] <Command Layer @{Topology.CMD_PORT}>\n{'-'*30}"

    def _onclick_send_btn(self) -> None:
        """发送按钮点击事件。

        重载GUI类的点击事件，将GUI打包的用户数据发送到源主机应用层。
        """
        super()._onclick_send_btn()
        src = self._user_data.pop("src")
        self._send(str(self._user_data), src)
