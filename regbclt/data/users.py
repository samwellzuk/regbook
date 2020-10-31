# -*- coding: utf-8 -*-
# Created by samwell
import time
from typing import List, Optional, NoReturn
from PyQt5.QtCore import QObject, pyqtSignal

from .model import User, admin_role, rw_role, change_self_role

from .dbmgr import DBManager
import time


class UserService(QObject):
    progressUpdated = pyqtSignal(int)

    def get_all_user(self) -> List[User]:
        for i in range(11):
            time.sleep(0.01)
        return []

    def test_get_all_user(self) -> List[User]:
        self.progressUpdated.emit(0)
        mgr = DBManager()
        result = mgr.get_db().command('usersInfo')
        self.progressUpdated.emit(50)
        users: List[User] = []
        curname = mgr.cur_user.user
        total = len(result['users'])
        cur = 0
        for u in result['users']:
            self.progressUpdated.emit(50 + int(cur / total * 50))
            cur += 1
            if u['user'] == curname:
                continue
            users.append(User(**u))
        self.progressUpdated.emit(100)
        return users

    def get_user(self, username: str) -> Optional[User]:
        mgr = DBManager()
        if username == mgr.cur_user.user:
            raise RuntimeError("Can't get current login user!")
        result = mgr.get_db().command('usersInfo', username)
        if result['users']:
            return User(**result['users'][0])
        return None

    def del_user(self, username: str) -> NoReturn:
        mgr = DBManager()
        if username == mgr.cur_user.user:
            raise RuntimeError("Can't delete current login user!")
        mgr.get_db().command('dropUser', username)

    def add_user(self, name: str, pwd: str, isadmin: bool) -> User:
        mgr = DBManager()
        rs = [admin_role] if isadmin else [rw_role, change_self_role]
        mgr.get_db().command('createUser', name, pwd=pwd, roles=rs)
        u = self.get_user(name)
        if u is None:
            raise RuntimeError('Create ok, but query failed!')
        return u

    def reset_pwd(self, user: User, pwd: str) -> NoReturn:
        mgr = DBManager()
        if user.user == mgr.cur_user.user:
            raise RuntimeError("Can't reset password for current login user!")
        mgr.get_db().command('updateUser', user.user, pwd=pwd)
        # after change pwd , set back to user
        user.password = pwd
