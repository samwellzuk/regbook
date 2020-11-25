# -*- coding: utf-8 -*-
# Created by samwell
from typing import List, NoReturn, Optional

from PyQt5.QtCore import QObject, pyqtSignal

from .dbmgr import DBManager, User, admin_role, rw_role, change_self_role


class UserService(QObject):
    progressUpdated = pyqtSignal(int)
    progressTxtChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def get_all_user(self) -> List[User]:
        self.progressTxtChanged.emit('Query user information ...')
        self.progressUpdated.emit(0)
        mgr = DBManager()
        result = mgr.get_db().command('usersInfo')
        self.progressUpdated.emit(50)
        users: List[User] = []
        curname = mgr.cur_user.user
        for u in result['users']:
            if u['user'] == curname:
                continue
            users.append(User(**u))
        self.progressUpdated.emit(100)
        return users

    def get_user(self, username: str) -> Optional[User]:
        self.progressTxtChanged.emit('Get user information ...')
        self.progressUpdated.emit(0)
        mgr = DBManager()
        if username == mgr.cur_user.user:
            raise RuntimeError("Can't get current login user!")
        result = mgr.get_db().command('usersInfo', username)
        self.progressUpdated.emit(100)
        if result['users']:
            return User(**result['users'][0])
        return None

    def del_user(self, username: str) -> NoReturn:
        self.progressTxtChanged.emit('Delete user ...')
        self.progressUpdated.emit(0)
        mgr = DBManager()
        if username == mgr.cur_user.user:
            raise RuntimeError("Can't delete current login user!")
        mgr.get_db().command('dropUser', username)
        self.progressUpdated.emit(100)

    def add_user(self, name: str, pwd: str, isadmin: bool) -> User:
        self.progressTxtChanged.emit('Add user ...')
        self.progressUpdated.emit(0)
        mgr = DBManager()
        rs = [admin_role] if isadmin else [rw_role, change_self_role]
        mgr.get_db().command('createUser', name, pwd=pwd, roles=rs)
        user = self.get_user(name)
        if user is None:
            raise RuntimeError('Create ok, but query failed!')
        self.progressUpdated.emit(100)
        return user

    def reset_pwd(self, user: User, pwd: str) -> User:
        self.progressTxtChanged.emit('Reset password...')
        self.progressUpdated.emit(0)
        mgr = DBManager()
        if user.user == mgr.cur_user.user:
            raise RuntimeError("Can't reset password for current login user!")
        mgr.get_db().command('updateUser', user.user, pwd=pwd)
        # after change pwd , set back to user
        user.password = pwd
        self.progressUpdated.emit(100)
        return user
