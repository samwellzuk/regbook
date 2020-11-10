# -*- coding: utf-8 -*-

"""
Module implementing LoginDlg.
"""
import socket

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog, QMessageBox, QProgressDialog

from data.dbmgr import DBManager
from comm.asynctask import coroutine, AsyncTask
from comm.utility import except_check

from .ui_LoginDlg import Ui_LoginDlg


class LoginDlg(QDialog, Ui_LoginDlg):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(LoginDlg, self).__init__(parent)
        self.setupUi(self)
        self.username.setFocus()

    @except_check
    def _check_status(self):
        sip = self.server.text()
        suser = self.username.text()
        spwd = self.password.text()
        self.okButton.setEnabled(True if sip and suser and spwd else False)

    @pyqtSlot()
    @coroutine(is_block=True)
    def accept(self):
        sip = self.server.text()
        suser = self.username.text()
        spwd = self.password.text()

        progressdlg = QProgressDialog(parent=self)
        progressdlg.setWindowModality(Qt.WindowModal)
        progressdlg.setAutoClose(False)
        progressdlg.setAutoReset(False)
        progressdlg.setCancelButton(None)
        progressdlg.show()
        progressdlg.setValue(10)
        try:
            progressdlg.setLabelText(f'checking domain[{sip}] ...')
            progressdlg.setValue(30)

            yield AsyncTask(socket.gethostbyname, sip)

            progressdlg.setLabelText(f'connecting server[{sip}] ...')
            progressdlg.setValue(60)
            mgr = DBManager()

            rt = yield AsyncTask(mgr.auth, suser, spwd, sip)
            progressdlg.setValue(100)
            if not rt:
                raise RuntimeError('User name or password wrong, please retry!')
            progressdlg.done(0)
            super().accept()

        except socket.gaierror:
            QMessageBox.warning(self, 'Warning', f"Can't Find Domain[{sip}] , please input again!")
            self.server.setText('')
            self.server.setFocus()
            progressdlg.done(0)
        except Exception as e:
            QMessageBox.warning(self, 'Warning', str(e))
            progressdlg.done(0)

    @pyqtSlot(str)
    def on_server_textChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type str
        """
        self._check_status()

    @pyqtSlot(str)
    def on_username_textChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type str
        """
        self._check_status()

    @pyqtSlot(str)
    def on_password_textChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type str
        """
        self._check_status()
