from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, QListWidget,
                               QMenu, QHBoxLayout, QVBoxLayout, QSystemTrayIcon, QMessageBox)
from about_dialog import AboutDialog
from notice_bot import NoticeBot

import resource_rc


class ControlUI(QMainWindow):
    __bot = None

    def __init__(self):
        super(ControlUI, self).__init__()

        self.init_ui()
        self.start_job()

    # 重写父类关闭事件处理, 不关闭，只隐藏
    def closeEvent(self, event):
        if self.__tray_icon.isVisible():
            self.hide()
            event.ignore()

    def init_ui(self):
        self.setWindowTitle('企业微信通知机器人助手')
        self.resize(400, 300)
        self.sys_icon = QIcon(':images/icon.png')
        self.setWindowIcon(self.sys_icon)

        self.create_tray_icon()
        self.create_menu()

        main_frame = QWidget()
        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        log_layout = QHBoxLayout()

        self.__btn_start = QPushButton('开始')
        self.__btn_start.setDefault(True)
        self.__btn_start.clicked.connect(self.start_job)
        btn_layout.addWidget(self.__btn_start)
        self.__btn_stop = QPushButton('停止')
        self.__btn_stop.setDefault(True)
        self.__btn_stop.clicked.connect(self.stop_job)
        btn_layout.addWidget(self.__btn_stop)

        self.__list_log = QListWidget()
        self.__list_log.itemDoubleClicked.connect(self.list_log_double_clicked)
        log_layout.addWidget(self.__list_log)

        main_layout.addLayout(btn_layout, 1)
        main_layout.addLayout(log_layout, 8)

        main_frame.setLayout(main_layout)
        self.setCentralWidget(main_frame)

    def create_tray_icon(self):
        action_restore = QAction('恢复', self, triggered=self.showNormal)
        action_quit = QAction('退出', self, triggered=QApplication.instance().quit)

        menu = QMenu(self)
        menu.addAction(action_restore)
        menu.addAction(action_quit)

        self.__tray_icon = QSystemTrayIcon(self)
        self.__tray_icon.setIcon(self.sys_icon)
        self.__tray_icon.setContextMenu(menu)
        self.__tray_icon.show()

    def create_menu(self):
        menubar = self.menuBar()
        menu_file = menubar.addMenu('文件')
        action_exit = QAction('退出', self, triggered=QApplication.instance().quit)
        menu_file.addAction(action_exit)
        action_about = QAction('关于', self, triggered=self.open_about)
        menubar.addAction(action_about)

    def list_log_double_clicked(self, item):
        QMessageBox.information(self, "Info", item.text())

    def open_about(self):
        self.dialog_about = AboutDialog()
        self.dialog_about.show()

    def start_job(self):
        self.__bot = NoticeBot(False)
        self.__bot.set_log_callback(self.log_callback)
        self.__bot.create_jobs()
        self.__bot.start()
        if self.__bot.is_start:
            self.__btn_start.setEnabled(False)
            self.__btn_stop.setEnabled(True)
        else:
            self.__btn_start.setEnabled(True)
            self.__btn_stop.setEnabled(False)

    def stop_job(self):
        if self.__bot is not None:
            self.__bot.close()
            self.__bot = None
        self.__btn_start.setEnabled(True)
        self.__btn_stop.setEnabled(False)

    def log_callback(self, log):
        count = self.__list_log.count()
        if count == 30:
            self.__list_log.takeItem(0)
            count -= 1
        self.__list_log.addItem(log)
        self.__list_log.setCurrentRow(count)