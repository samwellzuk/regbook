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

from .ProgressDlg import ProgressDlg
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
        self.progressdlg = ProgressDlg(parent=self)
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

        self.progressdlg.open()
        try:
            self.progressdlg.setLabelText(f'checking domain[{sip}] ...')
            self.progressdlg.setValue(30)

            yield AsyncTask(socket.gethostbyname, sip)

            self.progressdlg.setLabelText(f'connecting server[{sip}] ...')
            self.progressdlg.setValue(60)
            mgr = DBManager()

            rt = yield AsyncTask(mgr.auth, suser, spwd, sip)
            self.progressdlg.setValue(100)
            if not rt:
                raise RuntimeError('User name or password wrong, please retry!')
            self.progressdlg.close()
            super().accept()

        except socket.gaierror:
            QMessageBox.warning(self, 'Warning', f"Can't Find Domain[{sip}] , please input again!")
            self.progressdlg.close()
            self.server.setText('')
            self.server.setFocus()
        except Exception as e:
            QMessageBox.warning(self, 'Warning', str(e))
            self.progressdlg.close()

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
