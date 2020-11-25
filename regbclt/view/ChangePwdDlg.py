# -*- coding: utf-8 -*-

"""
Module implementing ChangePwdDlg.
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from comm.utility import except_check

from .ui_ChangePwdDlg import Ui_ChangePwdDlg


class ChangePwdDlg(QDialog, Ui_ChangePwdDlg):
    """
    Class documentation goes here.
    """

    def __init__(self, username, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(ChangePwdDlg, self).__init__(parent)
        self.setupUi(self)
        self.username.setText(username)
        self.soldpwd = None
        self.spwd = None
        self.sconfirm = None

    def state_change(self):
        self.soldpwd = self.oldpwd.text()
        self.spwd = self.newpwd.text()
        self.sconfirm = self.confirmpwd.text()
        if self.soldpwd and self.spwd and self.sconfirm and self.spwd == self.sconfirm:
            self.okButton.setEnabled(True)
        else:
            self.okButton.setEnabled(False)

    @pyqtSlot(str)
    @except_check
    def on_oldpwd_textChanged(self, p0):
        self.state_change()

    @pyqtSlot(str)
    @except_check
    def on_newpwd_textChanged(self, p0):
        self.state_change()

    @pyqtSlot(str)
    @except_check
    def on_confirmpwd_textChanged(self, p0):
        self.state_change()
