import sys
from PySide6.QtWidgets import QApplication
from control_ui import ControlUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = ControlUI()
    window.show()
    app.exit(app.exec())