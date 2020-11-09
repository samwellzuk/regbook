# -*-coding: utf-8 -*-
# Created by samwell
import sys
# init environ
import settings
from comm import fileicon

from PyQt5.QtWidgets import QApplication, QMessageBox
from view.MainWnd import MainWindow
from view.LoginDlg import LoginDlg


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Christian Gospel Center")
    app.setOrganizationDomain("christian-gospel-center.business.site")
    app.setApplicationName("RegBook")

    # check file
    settings.initialize()
    fileicon.initialize()
    try:
        dlg = LoginDlg()
        if dlg.exec() != LoginDlg.Accepted:
            return -1
        wnd = MainWindow()
        wnd.show()
        rt = app.exec()
    finally:
        fileicon.uninialize()
    return rt


if __name__ == "__main__":
    rt = -1
    try:
        rt = main()
    except Exception as e:
        QMessageBox.critical(None, 'Error', str(e))
    sys.exit(rt)
