# -*- coding: utf-8 -*-
# Created by samwell
from typing import List, Optional, NoReturn
from PyQt5.QtCore import QObject, pyqtSignal

from .model import VirFile
from .dbmgr import DBManager


class VirFileService(QObject):
    progressUpdated = pyqtSignal(int)
    progressTxtChanged = pyqtSignal(str)


