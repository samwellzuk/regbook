# -*- coding: utf-8 -*-

"""
Module implementing ChangePwdDlg.
"""
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog


from .ui_ProgressDlg import Ui_ProgressDlg


class ProgressDlg(QDialog, Ui_ProgressDlg):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(ProgressDlg, self).__init__(parent)
        self.setupUi(self)

    @pyqtSlot(str)
    def setLabelText(self, txt):
        if not super(ProgressDlg, self).isHidden():
            self.progressTxt.setText(txt)

    @pyqtSlot(int)
    def setValue(self, progress):
        if not super(ProgressDlg, self).isHidden():
            self.progressBar.setValue(progress)

    def open(self):
        super().open()
        self.progressBar.setValue(0)

    def close(self) -> bool:
        super().hide()
        return True

    def exec(self) -> int:
        raise NotImplementedError('exec')

    def show(self):
        raise NotImplementedError('show')

    def accept(self):
        return

    def done(self, r):
        return

    def reject(self):
        return
