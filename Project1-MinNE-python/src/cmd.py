import sys

from PyQt5.QtWidgets import QApplication

from layer import CommandLayer
from utils import *

if __name__ == "__main__":
    cmd_app = QApplication(sys.argv)
    cmd = CommandLayer()
    print(cmd)

    cmd.show()
    sys.exit(cmd_app.exec_())
