import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class GUI(QMainWindow):
    """控制台主界面。"""

    def __init__(self) -> None:
        super().__init__()
        self.setup_UI()

    def setup_UI(self):
        """初始化UI。"""
        # 窗口外观。
        self.setFixedSize(300, 200)
        self.setWindowTitle("控制台")
        self.setFont(QFont("Microsoft YaHei UI", pointSize=11))

        # 窗口位置。
        screen = QDesktopWidget().screenGeometry()
        size = self.frameGeometry()
        size.moveCenter(screen.center())
        self.move(size.topLeft())

        # 窗口布局。
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.Hwidget_1 = QWidget(self.central)
        self.Hwidget_1.setGeometry(QRect(140, 0, 150, 40))
        self.Hlayout_1 = QHBoxLayout(self.Hwidget_1)
        self.Hlayout_1.setContentsMargins(0, 0, 0, 0)
        self.Hwidget_2 = QWidget(self.central)
        self.Hwidget_2.setGeometry(QRect(10, 40, 280, 40))
        self.Hlayout_2 = QHBoxLayout(self.Hwidget_2)
        self.Hlayout_2.setContentsMargins(0, 0, 0, 0)
        self.Vwidget = QWidget(self.central)
        self.Vwidget.setGeometry(QRect(10, 80, 60, 80))
        self.Vlayout = QVBoxLayout(self.Vwidget)
        self.Vlayout.setContentsMargins(0, 0, 0, 0)

        # 标题标签。
        self.title = QLabel(self.central)
        self.title.setGeometry(QRect(10, 0, 130, 40))
        self.title.setFont(QFont("Microsoft YaHei UI", pointSize=12, weight=75))
        self.title.setText("💻 控制台")

        # 单播单选按钮。
        self.unicast_radio = QRadioButton(self.Hwidget_1)
        self.unicast_radio.setText("单播")

        # 广播单选按钮。
        self.broadcast_radio = QRadioButton(self.Hwidget_1)
        self.broadcast_radio.setText("广播")

        # 源标签。
        self.src_label = QLabel(self.Hwidget_2)
        self.src_label.setAlignment(Qt.AlignCenter)
        self.src_label.setText("源")

        # 源下拉框。
        self.src_combo = QComboBox(self.Hwidget_2)

        # 目的标签。
        self.dst_label = QLabel(self.Hwidget_2)
        self.dst_label.setAlignment(Qt.AlignCenter)
        self.dst_label.setText("目的")

        # 目的下拉框。
        self.dst_combo = QComboBox(self.Hwidget_2)

        # 文本单选按钮。
        self.text_radio = QRadioButton(self.Vwidget)
        self.text_radio.setText("文本")

        # 文本编辑框。
        self.text_edit = QLineEdit(self.central)
        self.text_edit.setGeometry(QRect(80, 85, 210, 30))

        # 文件单选按钮。
        self.file_radio = QRadioButton(self.Vwidget)
        self.file_radio.setText("图片")

        # 文件按钮。
        self.file_btn = QPushButton(self.central)
        self.file_btn.setGeometry(QRect(80, 125, 210, 30))
        self.file_btn.setMinimumSize(QSize(210, 0))
        self.file_btn.setText("选择文件")

        # 发送按钮。
        self.send_btn = QPushButton(self.central)
        self.send_btn.setGeometry(QRect(10, 160, 280, 35))
        self.send_btn.setText("发送")

        # 将组件添加进布局。
        self.Hlayout_1.addWidget(self.unicast_radio)
        self.Hlayout_1.addWidget(self.broadcast_radio)
        self.Hlayout_2.addWidget(self.src_label)
        self.Hlayout_2.addWidget(self.src_combo)
        self.Hlayout_2.addWidget(self.dst_label)
        self.Hlayout_2.addWidget(self.dst_combo)
        self.Vlayout.addWidget(self.text_radio)
        self.Vlayout.addWidget(self.file_radio)

    @staticmethod
    def raise_critical(message: str):
        """弹出错误窗口。

        Args:
            message: 错误信息。
        """
        # 错误弹窗。
        box = QMessageBox(QMessageBox.Critical, "错误", message)
        box.addButton("确定", QMessageBox.ButtonRole.YesRole)
        box.exec_()


if __name__ == "__main__":
    cmd_app = QApplication(sys.argv)
    cmd = GUI()
    cmd.show()
    sys.exit(cmd_app.exec_())
