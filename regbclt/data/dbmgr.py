#!/usr/bin/python
# -*- coding: utf-8 -*-

from hashlib import md5
from typing import NoReturn, Optional

import pymongo
import pymongo.errors
import pymongo.database

from .singleton import Singleton
from .model import User, admin_role, rw_role, change_self_role

_root_user: str = 'regbookroot'
# 3d31cf4b17814ef982d50895de864814
_root_pwd: str = md5(md5(_root_user.encode()).digest()).hexdigest()
_root_role: str = "root"


class DBManager(metaclass=Singleton):
    _client: Optional[pymongo.MongoClient]
    cur_user: Optional[User]

    def __init__(self):
        self._client = None
        self.cur_user = None

    def _init_db(self, user: str, pwd: str, host: str, port: int) -> NoReturn:
        # init db only in localhost
        if host.lower() != 'localhost' and host.lower() != '127.0.0.1':
            return
        # Localhost Exception: 根据文档，mongodb会添加第一个用户作为管理员，此处设置为内置账户,
        try:
            with pymongo.MongoClient(host, port) as client:
                db = client.admin
                # The ismaster command is cheap and does not require auth.
                db.command('ismaster')
                # if db was initialized before, it will raise OperationFailure
                db.command("createUser", _root_user, pwd=_root_pwd, roles=[_root_role])
            # login
            with pymongo.MongoClient(host, port,
                                     username=_root_user, password=_root_pwd,
                                     authSource='admin') as client:
                db = client.admin
                # The ismaster command is cheap and does not require auth.
                db.command('ismaster')

                db = client.regbook

                db.command('createRole', change_self_role,
                           privileges=[
                               {
                                   'resource': {'db': 'regbook', 'collection': ''},
                                   'actions': ['changeOwnPassword', 'changeOwnCustomData']
                               }],
                           roles=[]
                           )

                db.command("createUser", user, pwd=pwd, roles=[admin_role])

                db.create_collection('members')
                db.members.create_index(
                    [('$**', pymongo.TEXT), ],
                    name='_fulltext_index',
                )
        except pymongo.errors.ConnectionFailure as exc:
            raise RuntimeError("Server not available")
        except pymongo.errors.OperationFailure as exc:
            if exc.code == 13:
                return
            raise

    def auth(self, user: str, pwd: str, host: str, port: int = 27017) -> bool:
        self._init_db(user, pwd, host, port)

        client = pymongo.MongoClient(
            host,
            port,
            username=user,
            password=pwd,
            authSource='regbook')
        try:
            db = client.regbook
            # The ismaster command is cheap and does not require auth.
            db.command('ismaster')
            uinfo = db.command('usersInfo', user)
        except pymongo.errors.ConnectionFailure as exc:
            client.close()
            raise RuntimeError("Server not available")
        except pymongo.errors.OperationFailure as exc:
            client.close()
            if exc.code == 18:
                return False
            raise
        except Exception:
            client.close()
            raise
        else:
            # 如果没有异常，认证通过，此时才缓存连接
            self.cur_user = User(**uinfo['users'][0])
            self.cur_user.password = pwd
            self._client = client
        return True

    def logout(self):
        assert (self.cur_user and self._client)
        self._client.close()
        self._client = None
        self.cur_user = None

    def get_db(self) -> pymongo.database.Database:
        return self._client.regbook

    def change_pwd(self, old_pwd: str, new_pwd: str) -> NoReturn:
        assert (self.cur_user and self._client)
        if self.cur_user.password != old_pwd:
            raise Exception('Old password is wrong!')
        self._client.regbook.command('updateUser', self.cur_user.user, pwd=new_pwd)
        self.cur_user.password = new_pwd
