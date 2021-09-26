from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel

import resource_rc


class AboutDialog(QDialog):
    def __init__(self):
        super(AboutDialog, self).__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('关于')
        self.resize(300, 100)
        self.sys_icon = QIcon(':images/icon.png')
        self.setWindowIcon(self.sys_icon)

        main_layout = QVBoxLayout()
        lab_version = QLabel()
        lab_version.setText('version: 0.1')
        lab_version.setAlignment(Qt.AlignCenter)
        lab_author = QLabel()
        lab_author.setText('作者: 飘逝的云')
        lab_author.setAlignment(Qt.AlignCenter)
        lab_visit = QLabel()
        lab_visit.setText("<A href='https://github.com/hongdou9022/WXWork_NoticeBot'>"
                          "https://github.com/hongdou9022/WXWork_NoticeBot</a>")
        lab_visit.setOpenExternalLinks(True)
        lab_visit.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(lab_version)
        main_layout.addWidget(lab_author)
        main_layout.addWidget(lab_visit)
        self.setLayout(main_layout)