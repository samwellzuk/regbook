# -*- coding: utf-8 -*-

"""
Module implementing RegisterDlg.
"""

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog

from comm.utility import except_check
from .ui_RegisterDlg import Ui_RegisterDlg


class RegisterDlg(QDialog, Ui_RegisterDlg):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(RegisterDlg, self).__init__(parent)
        self.setupUi(self)
        self.suser = None
        self.spwd = None
        self.bisadmin = False

    @except_check
    def state_change(self):
        self.suser = self.username.text()
        self.bisadmin = self.isadmin.checkState() == Qt.Checked
        self.spwd = self.pwd.text()
        sconfirm = self.confirmpwd.text()
        if self.suser and self.spwd and sconfirm and self.spwd == sconfirm:
            self.okButton.setEnabled(True)
        else:
            self.okButton.setEnabled(False)

    @pyqtSlot(str)
    def on_username_textChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type str
        """
        self.state_change()

    @pyqtSlot(str)
    def on_pwd_textChanged(self, p0):
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
