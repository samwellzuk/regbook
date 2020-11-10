# -*- coding: utf-8 -*-

"""
Module implementing PhotoEditorDlg.
"""
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QImage

from comm.utility import except_check

from .ui_PhotoEditorDlg import Ui_PhotoEditorDlg
from .PhotoWidget import PhotoWidget


class PhotoEditorDlg(QDialog, Ui_PhotoEditorDlg):
    """
    Class documentation goes here.
    """

    def __init__(self, img: QImage, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(PhotoEditorDlg, self).__init__(parent)
        self.setupUi(self, PhotoWidget(img, parent=self))

        self.photoWidget.ratioChanged.connect(self.zoomChanged)
        self.zoomSlider.valueChanged.connect(self.photoWidget.zoom)

        self.rorateLeft.clicked.connect(self.photoWidget.rotate_left)
        self.rorateRight.clicked.connect(self.photoWidget.rotate_right)
        self.avatar = None
        self.thumbnail = None

    @pyqtSlot(int)
    @except_check
    def zoomChanged(self, val: int):
        self.zoomSlider.setValue(val)

    @except_check
    def accept(self):
        self.avatar, self.thumbnail = self.photoWidget.save_image()
        super(PhotoEditorDlg, self).accept()
