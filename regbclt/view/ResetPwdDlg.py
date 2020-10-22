# -*- coding: utf-8 -*-

"""
Module implementing RestPwdDlg.
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from ui.Ui_ResetPwdDlg import Ui_RestPwdDlg


class RestPwdDlg(QDialog, Ui_RestPwdDlg):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(RestPwdDlg, self).__init__(parent)
        self.setupUi(self)
    
    @pyqtSlot(str)
    def on_newpwd_textChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type str
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSlot(str)
    def on_confirmpwd_textChanged(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type str
        """
        # TODO: not implemented yet
        raise NotImplementedError
