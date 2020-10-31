# -*- coding: utf-8 -*-
# Created by samwell
from typing import List, Optional, NoReturn, Tuple
import pymongo

from PyQt5.QtCore import QObject, pyqtSignal

from .model import Member

from .dbmgr import DBManager


class MemberService(QObject):

    def query_members(self, skip: int, limit: int = 0,
                      keyword: Optional[str] = None,
                      sortkey: Optional[str] = None,
                      direction: int = pymongo.ASCENDING):
        pass
