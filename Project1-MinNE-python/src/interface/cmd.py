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
        self.__mode = Mode.UNICAST
        self.__src = ""
        self.__dst = ""
        self.__msgtype = MessageType.TEXT
        self.__text = ""
        self.__filepath = ""
        self.__hosts = get_hosts()
        self.__init_ui()

    def __init_ui(self):
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
        self.__central = QWidget()
        self.setCentralWidget(self.__central)
        self.__Hwidget_1 = QWidget(self.__central)
        self.__Hwidget_1.setGeometry(QRect(140, 0, 150, 40))
        self.__Hlayout_1 = QHBoxLayout(self.__Hwidget_1)
        self.__Hlayout_1.setContentsMargins(0, 0, 0, 0)
        self.__Hwidget_2 = QWidget(self.__central)
        self.__Hwidget_2.setGeometry(QRect(10, 40, 280, 40))
        self.__Hlayout_2 = QHBoxLayout(self.__Hwidget_2)
        self.__Hlayout_2.setContentsMargins(0, 0, 0, 0)
        self.__Vwidget = QWidget(self.__central)
        self.__Vwidget.setGeometry(QRect(10, 80, 60, 80))
        self.__Vlayout = QVBoxLayout(self.__Vwidget)
        self.__Vlayout.setContentsMargins(0, 0, 0, 0)

        # 标题标签。
        self.__title = QLabel(self.__central)
        self.__title.setGeometry(QRect(10, 0, 130, 40))
        self.__title.setFont(QFont("Microsoft YaHei UI", pointSize=12, weight=75))
        self.__title.setText("💻 控制台")

        # 单播单选按钮。
        self.__unicast_radio = QRadioButton(self.__Hwidget_1)
        self.__unicast_radio.setText("单播")
        self.__unicast_radio.setChecked(True)
        self.__unicast_radio.clicked.connect(self.__onclick_unicast_radio)

        # 广播单选按钮。
        self.__broadcast_radio = QRadioButton(self.__Hwidget_1)
        self.__broadcast_radio.setText("广播")
        self.__broadcast_radio.clicked.connect(self.__onclick_broadcast_radio)

        # 源标签。
        self.__src_label = QLabel(self.__Hwidget_2)
        self.__src_label.setAlignment(Qt.AlignCenter)
        self.__src_label.setText("源")

        # 源下拉框。
        self.__src_combo = QComboBox(self.__Hwidget_2)
        self.__src_combo.addItems(self.__hosts)
        self.__src_combo.setCurrentIndex(-1)
        self.__src_combo.activated.connect(self.__onactivate_src_combo)

        # 目的标签。
        self.__dst_label = QLabel(self.__Hwidget_2)
        self.__dst_label.setAlignment(Qt.AlignCenter)
        self.__dst_label.setText("目标")

        # 目的下拉框。
        self.__dst_combo = QComboBox(self.__Hwidget_2)
        self.__dst_combo.addItems(self.__hosts)
        self.__dst_combo.setCurrentIndex(-1)
        self.__dst_combo.activated.connect(self.__onactivate_dst_combo)

        # 文本单选按钮。
        self.__text_radio = QRadioButton(self.__Vwidget)
        self.__text_radio.setText("文本")
        self.__text_radio.setChecked(True)
        self.__text_radio.clicked.connect(self.__onclick_text_radio)

        # 文本编辑框。
        self.__text_edit = QLineEdit(self.__central)
        self.__text_edit.setGeometry(QRect(80, 85, 210, 30))
        self.__text_edit.textChanged.connect(self.__onedit_text_edit)

        # 文件单选按钮。
        self.__file_radio = QRadioButton(self.__Vwidget)
        self.__file_radio.setText("图片")
        self.__file_radio.clicked.connect(self.__onclick_file_radio)

        # 文件按钮。
        self.__file_btn = QPushButton(self.__central)
        self.__file_btn.setGeometry(QRect(80, 125, 210, 30))
        self.__file_btn.setText("选择文件")
        self.__file_btn.clicked.connect(self.__onclick_file_btn)

        # 发送按钮。
        self.__send_btn = QPushButton(self.__central)
        self.__send_btn.setGeometry(QRect(10, 160, 280, 35))
        self.__send_btn.setText("发送")
        self.__send_btn.clicked.connect(self._onclick_send_btn)

        # 将组件添加进布局。
        self.__Hlayout_1.addWidget(self.__unicast_radio)
        self.__Hlayout_1.addWidget(self.__broadcast_radio)
        self.__Hlayout_2.addWidget(self.__src_label)
        self.__Hlayout_2.addWidget(self.__src_combo)
        self.__Hlayout_2.addWidget(self.__dst_label)
        self.__Hlayout_2.addWidget(self.__dst_combo)
        self.__Vlayout.addWidget(self.__text_radio)
        self.__Vlayout.addWidget(self.__file_radio)

    def __onclick_unicast_radio(self) -> None:
        self.__mode = Mode.UNICAST
        if not self.__dst_combo.isEnabled():
            self.__dst_combo.setEnabled(True)

    def __onclick_broadcast_radio(self) -> None:
        self.__mode = Mode.BROADCAST
        if self.__dst_combo.isEnabled():
            self.__dst_combo.setEnabled(False)

    def __onactivate_src_combo(self) -> None:
        self.__src = self.__src_combo.currentText()

    def __onactivate_dst_combo(self) -> None:
        self.__dst = self.__dst_combo.currentText()

    def __onclick_text_radio(self) -> None:
        self.__msgtype = MessageType.TEXT

    def __onclick_file_radio(self) -> None:
        self.__msgtype = MessageType.FILE

    def __onedit_text_edit(self) -> None:
        self.__text = self.__text_edit.text()
        if not self.__text_radio.isChecked():
            self.__text_radio.setChecked(True)
            self.__msgtype = MessageType.TEXT

    def __onclick_file_btn(self) -> None:
        filename = QFileDialog.getOpenFileName(
            self, "打开", "", "Image files (*.jpg *.png)"
        )
        imgname = filename[0].split("/")[-1]
        if imgname:
            self.__filepath = filename[0]
            self.__file_btn.setText(imgname)
            self.__file_radio.setChecked(True)
            self.__msgtype = MessageType.FILE

    def __is_valid(self) -> bool:
        if not self.__mode:
            CommandUI.__raise_critical("请选择发送模式！")
        elif self.__src_combo.currentIndex() == -1:
            CommandUI.__raise_critical("请选择源设备号！")
        elif self.__mode != Mode.BROADCAST and self.__dst_combo.currentIndex() == -1:
            CommandUI.__raise_critical("请选择目标设备号！")
        elif self.__src_combo.currentText() == self.__dst_combo.currentText():
            CommandUI.__raise_critical("源与目标不能相同！")
        elif not self.__msgtype:
            CommandUI.__raise_critical("请选择消息类型！")
        elif self.__msgtype == MessageType.TEXT and not self.__text:
            CommandUI.__raise_critical("请输入文本！")
        elif self.__msgtype == MessageType.FILE and not self.__filepath:
            CommandUI.__raise_critical("请选择文件！")
        else:
            return True
        return False

    def _onclick_send_btn(self) -> None:
        if not self.__is_valid():
            return
        self._user_input = {
            "src": f"1{self.__src}300",
            "dst": f"1{self.__dst}300"
            if self.__mode == Mode.UNICAST
            else Topology.BROADCAST_PORT,
            "msgtype": self.__msgtype,
            "text": self.__text,
            "file": self.__filepath,
        }
        print(self._user_input)

    @staticmethod
    def __raise_critical(message: str):
        """弹出错误窗口。

        Args:
            message: 错误信息。
        """
        # 错误弹窗。
        box = QMessageBox(QMessageBox.Critical, "错误", message)
        box.addButton("确定", QMessageBox.ButtonRole.YesRole)
        box.exec_()
