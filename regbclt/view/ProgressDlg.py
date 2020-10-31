# -*- coding: utf-8 -*-

"""
Module implementing ChangePwdDlg.
"""
from typing import NoReturn
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

    def setLabelText(self, txt: str) -> NoReturn:
        self.progressTxt.setText(txt)

    def setValue(self, progress: int) -> NoReturn:
        self.progressBar.setValue(progress)

    def open(self) -> NoReturn:
        super().open()
        self.progressBar.setValue(0)

    def close(self) -> bool:
        super().hide()
        return True

    def is_open(self):
        return not super(ProgressDlg, self).isHidden()

    def exec(self) -> int:
        raise NotImplemented('exec')

    def show(self) -> None:
        raise NotImplemented('show')

    def accept(self) -> NoReturn:
        return

    def done(self, r: int) -> NoReturn:
        return

    def reject(self) -> NoReturn:
        return
