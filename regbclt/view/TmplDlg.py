# -*- coding: utf-8 -*-

"""
Module implementing ChangePwdDlg.
"""
from enum import Enum

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from .ui_TmplDlg import Ui_TmplDlg


class NextAction(Enum):
    Nothing = 0
    Open = 1
    Print = 2


class TmplDlg(QDialog, Ui_TmplDlg):
    """
    Class documentation goes here.
    """

    def __init__(self, tmpls, showopen=True, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(TmplDlg, self).__init__(parent)
        self.setupUi(self)

        self.tmplBox.addItems(tmpls)
        self.tmplBox.setCurrentIndex(0)
        self.tmpl = None
        self.nextaction = NextAction.Nothing
        if not showopen:
            self.openButton.setVisible(False)

    def accept(self) -> None:
        super(TmplDlg, self).accept()
        self.tmpl = self.tmplBox.currentText()
        if self.nothingButton.isChecked():
            self.nextaction = NextAction.Nothing
        elif self.openButton.isChecked():
            self.nextaction = NextAction.Open
        elif self.printButton.isChecked():
            self.nextaction = NextAction.Print
