# -*- coding: utf-8 -*-

"""
Module implementing MediaManageDlg.
"""
from PyQt5.QtCore import pyqtSlot, QByteArray
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap

from comm.utility import except_check

from .ui_MediaManageDlg import Ui_MediaManagDlg


class MediaManageDlg(QDialog, Ui_MediaManagDlg):
    """
    Class documentation goes here.
    """

    def __init__(self, member, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(MediaManageDlg, self).__init__(parent)
        self.setupUi(self)
        with open(r'D:\ChruchProjects\regbook\regbclt\exiftool\1.html') as f:
            context = f.read()
            self.exifText.setHtml(context)
