# -*- coding: utf-8 -*-
# Created by samwell
import weakref
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant, Qt, pyqtSignal, QByteArray
from PyQt5.QtGui import QPixmap

_avatar_high = 130
_avatar_width = 130

_member_header = [
    ('name', 260),
    ('cname', 80),
    ('sex', 60),
    ('birthday', 120),
    ('nation', 90),
    ('street', 500),
    ('city', 100),
    ('province', 100),
    ('homephone', 120),
    ('workphone', 120),
    ('cellphone', 120),
    ('education', 120),
    ('occupation', 200),
    ('father', 200),
    ('mother', 200),
    ('saved', 100),
    ('ledby', 200),
    ('minister', 200),
    ('baptizer', 200),
    ('baptismday', 120),
    ('venue', 250),
]


class MembersModel(QAbstractTableModel):
    sortChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._avatar_default = QPixmap(":/images/thumbnail.png")
        self._models = []
        self._avatars = []
        self._header = _member_header
        self.sortkey = None
        self.sortorder = None
        self.view = None

    def sort(self, column, order=Qt.AscendingOrder):
        if column == -1 or column == 0:
            self.sortkey = None
            self.sortorder = None
        else:
            self.sortkey = self._header[column - 1][0]
            self.sortorder = order
        self.sortChanged.emit()

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._models)

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._header) + 1

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if section == 0:
                return 'avatar'
            return self._header[section - 1][0]
        else:
            return int(section + 1)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._models)):
            return QVariant()
        column = index.column()
        row = index.row()
        item = self._models[row]
        if role == Qt.DecorationRole:
            if column == 0:
                if self._avatars[row]:
                    return self._avatars[row]
                else:
                    return self._avatar_default
        elif role == Qt.DisplayRole:
            if column != 0:
                key = self._header[column - 1][0]
                val = getattr(item, key)
                if column == 3+1:
                    return val.strftime('%b/%d/%Y') if val else None
                elif column == 19+1:
                    return val.strftime('%b/%d/%Y') if val else None
                else:
                    return val
        return QVariant()

    def initView(self, tableView):
        tableView.setColumnWidth(0, _avatar_width)  # name
        for i in range(len(self._header)):
            width = self._header[i][1]
            tableView.setColumnWidth(i+1, width)
        self.view = weakref.ref(tableView)

    def _update_high(self):
        tableview = self.view()
        if tableview:
            for i in range(len(self._models)):
                h = tableview.rowHeight(i)
                if h != _avatar_high:
                    tableview.setRowHeight(i, _avatar_high)

    def _load_pic(self, imgb):
        if imgb is None:
            return None
        b = QByteArray(imgb)
        bmp = QPixmap()
        bmp.loadFromData(b)
        return bmp

    def add_model(self, m, pos=0):
        self.beginInsertRows(QModelIndex(), pos, pos)
        self._models.insert(pos, m)
        self._avatars.insert(pos, self._load_pic(m.thumbnail))
        self.endInsertRows()
        self._update_high()

    def get_model(self, row):
        return self._models[row]

    def update_model(self, row, m):
        self._models[row] = m
        self._avatars[row] = self._load_pic(m.thumbnail)

        left = self.index(row, 0)
        rigth = self.index(row, len(self._header))
        self.dataChanged.emit(left, rigth)

    def remove_model(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._models[row]
        del self._avatars[row]
        self.endRemoveRows()

    def reset_models(self, mlist=None):
        self.beginResetModel()
        if mlist:
            self._models = mlist
            self._avatars = [self._load_pic(m.thumbnail) for m in mlist]
        else:
            self._models = []
            self._avatars = []
        self.endResetModel()
        self._update_high()
