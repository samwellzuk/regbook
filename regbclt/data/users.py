#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List, Optional, NoReturn

from .model import User, admin_role, rw_role, change_self_role

from .dbmgr import DBManager


class UserService(object):
    @staticmethod
    def get_all_user() -> List[User]:
        mgr = DBManager()
        result = mgr.get_db().command('usersInfo')
        users: List[User] = []
        curname = mgr.cur_user.user
        for u in result['users']:
            if u['user'] == curname:
                continue
            users.append(User(**u))
        return users

    @staticmethod
    def get_user(username: str) -> Optional[User]:
        mgr = DBManager()
        if username == mgr.cur_user.user:
            raise RuntimeError("Can't get current login user!")
        result = mgr.get_db().command('usersInfo', username)
        if result['users']:
            return User(**result['users'][0])
        return None

    @staticmethod
    def del_user(username: str) -> NoReturn:
        mgr = DBManager()
        if username == mgr.cur_user.user:
            raise RuntimeError("Can't delete current login user!")
        mgr.get_db().command('dropUser', username)

    @staticmethod
    def add_user(name: str, pwd: str, isadmin: bool) -> User:
        mgr = DBManager()
        rs = [admin_role] if isadmin else [rw_role, change_self_role]
        mgr.get_db().command('createUser', name, pwd=pwd, roles=rs)
        u = UserService.get_user(name)
        if u is None:
            raise RuntimeError('Create ok, but query failed!')
        return u

    @staticmethod
    def reset_pwd(user: User, pwd: str) -> NoReturn:
        mgr = DBManager()
        if user.user == mgr.cur_user.user:
            raise RuntimeError("Can't reset password for current login user!")
        mgr.get_db().command('updateUser', user.user, pwd=pwd)
        # after change pwd , set back to user
        user.password = pwd
