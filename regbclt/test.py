# -*-coding: utf-8 -*-
# Created by samwell
import sys
import time
from PyQt5.QtCore import pyqtSlot, QRect, QCoreApplication, Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton

from comm.asynctask import coroutine, AsyncTask
from comm.utility import except_check

from data.dbmgr import DBManager

from view.ProgressDlg import ProgressDlg


class UserService(QObject):
    progressUpdated = pyqtSignal(int)

    def get_all_user(self):
        for i in range(10):
            self.progressUpdated.emit(i * 10)
            time.sleep(1)
        self.progressUpdated.emit(100)
        return []


class Ui_LoginDlg(object):
    def setupUi(self, LoginDlg):
        LoginDlg.setObjectName("LoginDlg")
        LoginDlg.setWindowModality(Qt.ApplicationModal)
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


class TestDlg(QDialog, Ui_LoginDlg):
    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(QDialog, self).__init__(parent)
        self.setupUi(self)

        self.progressdlg = ProgressDlg(parent=self)
        self.svc = UserService()
        self.svc.progressUpdated.connect(self._update_progress)

    @pyqtSlot(int)
    @except_check
    def _update_progress(self, progress):
        print("update: ", progress)
        if self.progressdlg.is_open():
            self.progressdlg.setValue(progress)

    @pyqtSlot()
    @except_check
    def on_test(self):
        self.test()

    @coroutine(is_block=True)
    def test(self):
        self.progressdlg.setLabelText(f'Query user information ...')
        self.progressdlg.open()
        try:
            yield AsyncTask(self.svc.get_all_user)
        finally:
            self.progressdlg.close()
            print('is open:' , self.progressdlg.is_open())


from view.MainWnd import MainWindow


def main():
    app = QApplication(sys.argv)
    mgr = DBManager()
    mgr.auth('zy', '123', 'localhost')
    # wmd = MainWindow()
    # wmd.show()
    # dlg = TestDlg(wmd)
    dlg = TestDlg()
    dlg.show()
    return app.exec()


if __name__ == '__main__':
    main()
