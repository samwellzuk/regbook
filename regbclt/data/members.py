# -*- coding: utf-8 -*-
# Created by samwell
from typing import List, Optional, NoReturn, Tuple
from datetime import datetime
import pymongo

from PyQt5.QtCore import QObject, pyqtSignal, Qt

from .model import Member

from .dbmgr import DBManager


class MemberService(QObject):
    progressUpdated = pyqtSignal(int)
    progressTxtChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def query_members(self, skip: int, limit: int = 0,
                      keyword: Optional[str] = None,
                      sortkey: Optional[str] = None,
                      sortorder: Optional[int] = None) -> Tuple[int, List[Member]]:
        filter = {}
        if keyword:
            filter['$text'] = {'$search': keyword}
        projection = {'avatar': False}
        if sortkey and sortorder == Qt.AscendingOrder:
            sort = [(sortkey, pymongo.ASCENDING)]
        elif sortkey and sortorder == Qt.DescendingOrder:
            sort = [(sortkey, pymongo.DESCENDING)]
        else:
            sort = [('_ts', pymongo.DESCENDING)]
        self.progressTxtChanged.emit('Counting members ...')
        self.progressUpdated.emit(0)
        mgr = DBManager()
        coll = mgr.get_db().get_collection('members')
        total = coll.count_documents(filter)
        self.progressTxtChanged.emit('Querying members ...')
        self.progressUpdated.emit(10)
        batch_total = limit if limit else total
        batch_count = 0
        members = []
        cur = coll.find(filter=filter, projection=projection, skip=skip, limit=limit, sort=sort)
        for doc in cur:
            m = Member(**doc)
            members.append(m)
            batch_count += 1
            progress = 10 + int(batch_count / batch_total * 90)
            self.progressUpdated.emit(progress)
        self.progressUpdated.emit(100)
        return total, members

    def add_member(self, member: Member) -> Member:
        self.progressTxtChanged.emit('Inserting member...')
        self.progressUpdated.emit(0)
        doc = member.to_db_dict()
        doc.pop('_id')
        doc['_ts'] = datetime.now()
        coll = DBManager().get_db().get_collection('members')
        result = coll.insert_one(doc)
        member._id = result.inserted_id
        member._ts = doc['_ts']
        self.progressUpdated.emit(100)
        return member

    def del_member(self, member: Member) -> NoReturn:
        self.progressTxtChanged.emit('Inserting member...')
        self.progressUpdated.emit(0)
        coll = DBManager().get_db().get_collection('members')
        result = coll.delete_one({'_id': member._id})
        if result.deleted_count != 1:
            raise RuntimeError("Can't find member, please refresh!")
        self.progressUpdated.emit(100)

    def update_member(self, oldm: Member, newm: Member) -> Member:
        self.progressTxtChanged.emit('Inserting member...')
        self.progressUpdated.emit(0)
        olddi = oldm.to_db_dict()
        olddi.pop('_id')
        olddi.pop('_ts')
        newdi = newm.to_db_dict()
        newdi.pop('_id')
        newdi.pop('_ts')
        changedi = {}
        for k in olddi:
            if olddi[k] != newdi[k]:
                changedi[k] = newdi[k]
        # if no change pass
        if changedi:
            changedi['_ts'] = datetime.now()
            coll = DBManager().get_db().get_collection('members')
            result = coll.update_one({'_id': oldm._id, '_ts': oldm._ts},
                                     {'$set': changedi})
            if result.modified_count != 1:
                raise RuntimeError("Can't find member, please refresh!")
            newm._ts = changedi['_ts']
        self.progressUpdated.emit(100)
        return newm

    def get_member_avatar(self, member: Member) -> Member:
        self.progressTxtChanged.emit('Querying avatar...')
        self.progressUpdated.emit(0)
        coll = DBManager().get_db().get_collection('members')
        doc = coll.find_one({'_id': member._id, '_ts': member._ts},
                            projection={'photo': True, 'photofmt': True, 'avatar': True})
        if not doc:
            raise RuntimeError("Can't find member, please refresh!")
        member.photo = doc['photo'] if 'photo' in doc else None
        member.photofmt = doc['photofmt'] if 'photofmt' in doc else None
        member.avatar = doc['avatar'] if 'avatar' in doc else None
        self.progressUpdated.emit(100)
        return member
