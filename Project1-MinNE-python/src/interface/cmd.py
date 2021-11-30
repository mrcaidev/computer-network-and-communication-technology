from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from utils.io import get_hosts
from utils.params import *


class CommandUI(QMainWindow):
    """控制台主界面。"""

    def __init__(self) -> None:
        """初始化窗口与属性。"""
        super().__init__()
        self.mode = Mode.UNICAST
        self.src = ""
        self.dst = ""
        self.msgtype = MessageType.TEXT
        self.text = ""
        self.filepath = ""
        self.hosts = get_hosts()
        self.init_ui()

    def init_ui(self):
        """初始化UI。"""
        # 窗口外观。
        self.setFixedSize(300, 200)
        self.setWindowTitle(" ")
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
        self.unicast_radio.setChecked(True)
        self.unicast_radio.clicked.connect(self.onclick_unicast_radio)

        # 广播单选按钮。
        self.broadcast_radio = QRadioButton(self.Hwidget_1)
        self.broadcast_radio.setText("广播")
        self.broadcast_radio.clicked.connect(self.onclick_broadcast_radio)

        # 源标签。
        self.src_label = QLabel(self.Hwidget_2)
        self.src_label.setAlignment(Qt.AlignCenter)
        self.src_label.setText("源")

        # 源下拉框。
        self.src_combo = QComboBox(self.Hwidget_2)
        self.src_combo.addItems(self.hosts)
        self.src_combo.setCurrentIndex(-1)
        self.src_combo.activated.connect(self.onactivate_src_combo)

        # 目的标签。
        self.dst_label = QLabel(self.Hwidget_2)
        self.dst_label.setAlignment(Qt.AlignCenter)
        self.dst_label.setText("目标")

        # 目的下拉框。
        self.dst_combo = QComboBox(self.Hwidget_2)
        self.dst_combo.addItems(self.hosts)
        self.dst_combo.setCurrentIndex(-1)
        self.dst_combo.activated.connect(self.onactivate_dst_combo)

        # 文本单选按钮。
        self.text_radio = QRadioButton(self.Vwidget)
        self.text_radio.setText("文本")
        self.text_radio.setChecked(True)
        self.text_radio.clicked.connect(self.onclick_text_radio)

        # 文本编辑框。
        self.text_edit = QLineEdit(self.central)
        self.text_edit.setGeometry(QRect(80, 85, 210, 30))
        self.text_edit.textChanged.connect(self.onedit_text_edit)

        # 文件单选按钮。
        self.file_radio = QRadioButton(self.Vwidget)
        self.file_radio.setText("图片")
        self.file_radio.clicked.connect(self.onclick_file_radio)

        # 文件按钮。
        self.file_btn = QPushButton(self.central)
        self.file_btn.setGeometry(QRect(80, 125, 210, 30))
        self.file_btn.setText("选择文件")
        self.file_btn.clicked.connect(self.onclick_file_btn)

        # 发送按钮。
        self.send_btn = QPushButton(self.central)
        self.send_btn.setGeometry(QRect(10, 160, 280, 35))
        self.send_btn.setText("发送")
        self.send_btn.clicked.connect(self.onclick_send_btn)

        # 将组件添加进布局。
        self.Hlayout_1.addWidget(self.unicast_radio)
        self.Hlayout_1.addWidget(self.broadcast_radio)
        self.Hlayout_2.addWidget(self.src_label)
        self.Hlayout_2.addWidget(self.src_combo)
        self.Hlayout_2.addWidget(self.dst_label)
        self.Hlayout_2.addWidget(self.dst_combo)
        self.Vlayout.addWidget(self.text_radio)
        self.Vlayout.addWidget(self.file_radio)

    def onclick_unicast_radio(self) -> None:
        self.mode = Mode.UNICAST
        if not self.dst_combo.isEnabled():
            self.dst_combo.setEnabled(True)

    def onclick_broadcast_radio(self) -> None:
        self.mode = Mode.BROADCAST
        if self.dst_combo.isEnabled():
            self.dst_combo.setEnabled(False)

    def onactivate_src_combo(self) -> None:
        self.src = self.src_combo.currentText()

    def onactivate_dst_combo(self) -> None:
        self.dst = self.dst_combo.currentText()

    def onclick_text_radio(self) -> None:
        self.msgtype = MessageType.TEXT

    def onclick_file_radio(self) -> None:
        self.msgtype = MessageType.FILE

    def onedit_text_edit(self) -> None:
        self.text = self.text_edit.text()
        if not self.text_radio.isChecked():
            self.text_radio.setChecked(True)
            self.msgtype = MessageType.TEXT

    def onclick_file_btn(self) -> None:
        filename = QFileDialog.getOpenFileName(
            self, "打开", "", "Image files (*.jpg *.png)"
        )
        imgname = filename[0].split("/")[-1]
        if imgname:
            self.filepath = filename[0]
            self.file_btn.setText(imgname)
            self.file_radio.setChecked(True)
            self.msgtype = MessageType.FILE

    def validate(self) -> bool:
        if not self.mode:
            CommandUI.raise_critical("请选择发送模式！")
        elif self.src_combo.currentIndex() == -1:
            CommandUI.raise_critical("请选择源设备号！")
        elif self.dst_combo.currentIndex() == -1:
            CommandUI.raise_critical("请选择目标设备号！")
        elif self.src_combo.currentText() == self.dst_combo.currentText():
            CommandUI.raise_critical("源与目标不能相同！")
        elif not self.msgtype:
            CommandUI.raise_critical("请选择消息类型！")
        elif self.msgtype == MessageType.TEXT and not self.text:
            CommandUI.raise_critical("请输入文本！")
        elif self.msgtype == MessageType.FILE and not self.filepath:
            CommandUI.raise_critical("请选择文件！")
        else:
            return True
        return False

    def onclick_send_btn(self) -> None:
        if not self.validate():
            return
        data = {
            "mode": self.mode,
            "src": self.src,
            "dst": self.dst,
            "msgtype": self.msgtype,
            "text": self.text,
            "filepath": self.filepath,
        }
        print(data)

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
