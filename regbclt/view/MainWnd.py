# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from data.dbmgr import DBManager
from comm.utility import except_check
from .MemberManageView import MemberManageView
from .UserManageView import UserManageView
from .ChangePwdDlg import ChangePwdDlg

from .ui_MainWnd import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        mgr = DBManager()
        self.userTitle.setText(f'Welcome {mgr.cur_user.user}！')

        self._membermgrview = MemberManageView()
        self.workspace.addWidget(self._membermgrview)
        self._membermgrview.activeView()

        if mgr.cur_user.is_admin():
            self._usermgrview = UserManageView()
            self.workspace.addWidget(self._usermgrview)
            self.userManage.setVisible(True)
        else:
            self._usermgrview = None
            self.userManage.setVisible(False)

    @pyqtSlot()
    @except_check
    def on_changePwd_clicked(self):
        """
        Slot documentation goes here.
        """
        db = DBManager()
        dlg = ChangePwdDlg(db.cur_user.user, parent=self)
        if dlg.exec() != ChangePwdDlg.Accepted:
            return
        db.change_pwd(dlg.soldpwd, dlg.spwd)
        QMessageBox.information(self, 'Information', 'Update success!')

    @pyqtSlot()
    @except_check
    def on_memberManage_clicked(self):
        """
        Slot documentation goes here.
        """
        self.workspace.setCurrentWidget(self._membermgrview)
        self._membermgrview.activeView()

    @pyqtSlot()
    @except_check
    def on_userManage_clicked(self):
        """
        Slot documentation goes here.
        """
        self.workspace.setCurrentWidget(self._usermgrview)
        self._usermgrview.activeView()
