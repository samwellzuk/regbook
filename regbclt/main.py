# -*-coding: utf-8 -*-
# Created by samwell

import sys
from PyQt5.QtWidgets import QApplication
from view.mainwindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    sys.exit(app.exec_())
