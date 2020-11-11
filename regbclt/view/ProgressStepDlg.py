# -*- coding: utf-8 -*-

"""
Module implementing ChangePwdDlg.
"""
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from .ui_ProgressStepDlg import Ui_ProgressStepDlg


class ProgressStepDlg(QDialog, Ui_ProgressStepDlg):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(ProgressStepDlg, self).__init__(parent)
        self.setupUi(self)

    @pyqtSlot(str)
    def setLabelText(self, txt):
        if not super(ProgressStepDlg, self).isHidden():
            self.progressTxt.setText(txt)

    @pyqtSlot(int)
    def setValue(self, progress):
        if not super(ProgressStepDlg, self).isHidden():
            self.progressBar.setValue(progress)

    @pyqtSlot(str)
    def setStepLabelText(self, txt):
        if not super(ProgressStepDlg, self).isHidden():
            self.progressSetpTxt.setText(txt)

    @pyqtSlot(int)
    def setStepValue(self, progress):
        if not super(ProgressStepDlg, self).isHidden():
            self.progressStepBar.setValue(progress)

    @pyqtSlot(str)
    def addErrorText(self, txt):
        if not super(ProgressStepDlg, self).isHidden():
            self.errinfoEdit.appendPlainText(txt)

    def getAllError(self):
        return self.errinfoEdit.toPlainText()

    def open(self):
        super().open()
        self.progressBar.setValue(0)
        self.progressTxt.clear()
        self.progressStepBar.setValue(0)
        self.progressSetpTxt.clear()
        self.errinfoEdit.clear()

    def close(self) -> bool:
        super().hide()
        return True

    def exec(self) -> int:
        raise NotImplemented('exec')

    def show(self):
        raise NotImplemented('show')

    def accept(self):
        return

    def done(self, r):
        return

    def reject(self):
        return
