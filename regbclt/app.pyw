# -*-coding: utf-8 -*-
# Created by samwell
import sys
# sys.coinit_flags set to COINIT_APARTMENTTHREADED|COINIT_DISABLE_OLE1DDE == 6
# for ShellExecute https://docs.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shellexecutea
sys.coinit_flags = 6
# import after sys.coinit_flags set
import pythoncom

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
