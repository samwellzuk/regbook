# -*- coding: utf-8 -*-

"""
Module implementing RestPwdDlg.
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from comm.utility import except_check
from .ui_ResetPwdDlg import Ui_RestPwdDlg


class RestPwdDlg(QDialog, Ui_RestPwdDlg):
    """
    Class documentation goes here.
    """

    def __init__(self, username, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(RestPwdDlg, self).__init__(parent)
        self.setupUi(self)
        self.username.setText(username)
        self.snewpwd = None
        self.sconfirm = None

    @except_check
    def state_change(self):
        self.snewpwd = self.newpwd.text()
        self.sconfirm = self.confirmpwd.text()
        if self.snewpwd and self.sconfirm and self.snewpwd == self.sconfirm:
            self.okButton.setEnabled(True)
        else:
            self.okButton.setEnabled(False)

    @pyqtSlot(str)
    def on_newpwd_textChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type str
        """
        self.state_change()

    @pyqtSlot(str)
    def on_confirmpwd_textChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type str
        """
        self.state_change()
