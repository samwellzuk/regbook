# -*-coding: utf-8 -*-
# Created by samwell
import sys
import time
from PyQt5.QtCore import pyqtSlot, QRect, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QPushButton

from comm.asynctask import coroutine, AsyncTask


class Ui_LoginDlg(object):
    def setupUi(self, LoginDlg):
        LoginDlg.setObjectName("LoginDlg")
        LoginDlg.resize(358, 118)
        LoginDlg.setSizeGripEnabled(False)
        LoginDlg.setModal(True)
        self.pushButton = QPushButton(LoginDlg)
        self.pushButton.setGeometry(QRect(30, 50, 93, 28))
        self.pushButton.setObjectName("pushButton")
        self.cancelButton = QPushButton(LoginDlg)
        self.cancelButton.setGeometry(QRect(228, 48, 93, 28))
        self.cancelButton.setObjectName("cancelButton")

        self.retranslateUi(LoginDlg)
        self.cancelButton.clicked.connect(LoginDlg.reject)
        self.pushButton.clicked.connect(LoginDlg.on_test)

    def retranslateUi(self, LoginDlg):
        _translate = QCoreApplication.translate
        LoginDlg.setWindowTitle(_translate("LoginDlg", "Login"))
        self.pushButton.setText(_translate("LoginDlg", "Test"))
        self.cancelButton.setText(_translate("LoginDlg", "Quit"))


def asy_func(count):
    for i in range(count):
        time.sleep(0.05)
    return count


class TestDlg(QDialog, Ui_LoginDlg):
    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(QDialog, self).__init__(parent)
        self.setupUi(self)

    @pyqtSlot()
    def on_test(self):
        for i in range(2000):
            print('call ', i)
            self.test()

    @coroutine(is_block=True)
    def test(self):
        count = yield AsyncTask(asy_func, 1)


def main():
    app = QApplication(sys.argv)
    dlg = TestDlg()
    return dlg.exec()


if __name__ == '__main__':
    main()
