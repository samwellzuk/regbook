# -*- coding: utf-8 -*-

"""
Module implementing UserManageView.
"""

from PyQt5.QtCore import pyqtSlot, QModelIndex
from PyQt5.QtWidgets import QWidget, QMessageBox

from comm.asynctask import coroutine, AsyncTask
from comm.utility import except_check
from data.users import UserService
from vm.users import UsersModel

from .RegisterDlg import RegisterDlg
from .ResetPwdDlg import RestPwdDlg
from .ProgressDlg import ProgressDlg

from .ui_UserManageView import Ui_UserManageView


class UserManageView(QWidget, Ui_UserManageView):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(UserManageView, self).__init__(parent)
        self.setupUi(self)
        self._usersmodel = UsersModel()
        self.usersView.setModel(self._usersmodel)
        self._usersmodel.initView(self.usersView)

        self._selectmodel = self.usersView.selectionModel()
        self._selectmodel.currentRowChanged.connect(self.on_table_change)

        self.svc = UserService()
        self.progressdlg = ProgressDlg(parent=self)
        self.svc.progressUpdated.connect(self.progressdlg.setValue)
        self.svc.progressTxtChanged.connect(self.progressdlg.setLabelText)

    @coroutine(is_block=True)
    def _refresh_users(self):
        self.progressdlg.open()
        try:
            self._selectmodel.clear()
            self.findnameEdit.setText('')
            users = yield AsyncTask(self.svc.get_all_user)
            self._usersmodel.reset_models(users)
        finally:
            self.progressdlg.close()

    @pyqtSlot(QModelIndex, QModelIndex)
    @except_check
    def on_table_change(self, current, previous):
        if current.isValid():
            self.delButton.setEnabled(True)
            self.resetButton.setEnabled(True)
        else:
            self.delButton.setEnabled(False)
            self.resetButton.setEnabled(False)

    @except_check
    def activeView(self):
        self._refresh_users()

    @pyqtSlot()
    @except_check
    def on_findButton_clicked(self):
        self._selectmodel.clear()
        name = self.findnameEdit.text()
        if name:
            users = []
            if u := self.svc.get_user(name):
                users.append(u)
            self._usersmodel.reset_models(users)
        else:
            QMessageBox.information(self, 'Notice', 'Please input user name for search')

    @pyqtSlot()
    @except_check
    def on_refreshButton_clicked(self):
        self._refresh_users()

    @pyqtSlot()
    @except_check
    def on_addButton_clicked(self):
        dlg = RegisterDlg(parent=self)
        if dlg.exec() != RegisterDlg.Accepted:
            return
        user = self.svc.add_user(dlg.suser, dlg.spwd, dlg.bisadmin)
        self._usersmodel.add_model(user)

    @pyqtSlot()
    @except_check
    def on_delButton_clicked(self):
        index = self._selectmodel.currentIndex()
        user = self._usersmodel.get_model(index.row())
        result = QMessageBox.question(self, "Delete", f"Are you sure to delete {user.user} ?")
        if result != QMessageBox.Yes:
            return
        self.svc.del_user(user.user)
        self._usersmodel.remove_model(index.row())

    @pyqtSlot()
    @except_check
    def on_resetButton_clicked(self):
        index = self._selectmodel.currentIndex()
        user = self._usersmodel.get_model(index.row())
        dlg = RestPwdDlg(user.user, parent=self)
        if dlg.exec() != RestPwdDlg.Accepted:
            return
        user = self.svc.reset_pwd(user, dlg.snewpwd)
        self._usersmodel.update_model(index.row(), user)
