# -*- coding: utf-8 -*-

"""
Module implementing ChangePwdDlg.
"""
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPalette, QColor

from .ui_MediaPlayDlg import Ui_MediaPlayDlg


class MediaPlayDlg(QDialog, Ui_MediaPlayDlg):
    """
    Class documentation goes here.
    """

    def __init__(self, vfile, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(MediaPlayDlg, self).__init__(parent)
        self.setupUi(self)
        self.videofile = vfile
        self.setWindowTitle(f'{vfile.filename} - Vlc Media Player')



