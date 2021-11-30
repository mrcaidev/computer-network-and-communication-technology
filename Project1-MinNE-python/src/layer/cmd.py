from interface.cmd import CommandUI
from utils.params import *

from layer._abstract import AbstractLayer


class CommandLayer(AbstractLayer, CommandUI):
    """控制台。"""

    def __init__(self) -> None:
        """初始化控制台。"""
        AbstractLayer.__init__(self, Topology.CMD_PORT)
        CommandUI.__init__(self)

    def __str__(self) -> str:
        """打印控制台信息。"""
        return f"[CMD] <Cmd layer @{Topology.CMD_PORT}>"

    def _onclick_send_btn(self) -> None:
        super()._onclick_send_btn()
        src = self._user_input.pop("src")
        self._send(str(self._user_input), src)
