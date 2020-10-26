# -*- coding: utf-8 -*-

"""
Module implementing MemberManageView.
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget

from .ui_MemberManageView import Ui_MemberManageView


class MemberManageView(QWidget, Ui_MemberManageView):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MemberManageView, self).__init__(parent)
        self.setupUi(self)
