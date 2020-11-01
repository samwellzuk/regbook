# -*- coding: utf-8 -*-
# Created by samwell
import weakref
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant, Qt, pyqtSignal, QByteArray
from PyQt5.QtGui import QPixmap

_avatar_high = 130
_avatar_width = 130


class MembersModel(QAbstractTableModel):
    sortChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._avatar_default = QPixmap(":/images/thumbnail.png")
        self._models = []
        self._avatars = []
        self._header = [
            'avatar',
            'name',
            'cname',
            'sex',
            'birthday',
            'nation',
            'street',
            'city',
            'province',
            'homephone',
            'workphone',
            'cellphone',
            'education',
            'occupation',
            'father',
            'mother',
            'saved',
            'ledby',
            'minister',
            'baptizer',
            'baptismday',
            'venue',
        ]
        self.sortkey = None
        self.sortorder = None
        self.view = None

    def sort(self, column, order=Qt.AscendingOrder):
        if column == -1 or column == 0:
            self.sortkey = None
            self.sortorder = None
        else:
            self.sortkey = self._header[column]
            self.sortorder = order
        self.sortChanged.emit()

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._models)

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._header)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._header[section]
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
            if column == 1:
                return item.name
            elif column == 2:
                return item.cname
            elif column == 3:
                return item.sex
            elif column == 4:
                return item.birthday.strftime('%b/%d/%Y') if item.birthday else None
            elif column == 5:
                return item.nation
            elif column == 6:
                return item.street
            elif column == 7:
                return item.city
            elif column == 8:
                return item.province
            elif column == 9:
                return item.homephone
            elif column == 10:
                return item.workphone
            elif column == 11:
                return item.cellphone
            elif column == 12:
                return item.education
            elif column == 13:
                return item.occupation
            elif column == 14:
                return item.father
            elif column == 15:
                return item.mother
            elif column == 16:
                return item.saved
            elif column == 17:
                return item.ledby
            elif column == 18:
                return item.minister
            elif column == 19:
                return item.baptizer
            elif column == 20:
                return item.baptismday.strftime('%b/%d/%Y') if item.baptismday else None
            elif column == 21:
                return item.venue
        return QVariant()

    def initView(self, tableView):
        tableView.setColumnWidth(0, _avatar_width)  # name
        tableView.setColumnWidth(1, 200)  # name
        tableView.setColumnWidth(2, 80)  # cname
        tableView.setColumnWidth(3, 60)  # sex
        tableView.setColumnWidth(4, 120)  # birthday
        tableView.setColumnWidth(5, 60)  # nation
        tableView.setColumnWidth(6, 400)  # street
        tableView.setColumnWidth(7, 100)  # city
        tableView.setColumnWidth(8, 100)  # province
        tableView.setColumnWidth(9, 120)  # homephone
        tableView.setColumnWidth(10, 120)  # workphone
        tableView.setColumnWidth(11, 120)  # cellphone
        tableView.setColumnWidth(12, 120)  # education
        tableView.setColumnWidth(13, 200)  # occupation
        tableView.setColumnWidth(14, 200)  # father
        tableView.setColumnWidth(15, 200)  # mother
        tableView.setColumnWidth(16, 100)  # saved
        tableView.setColumnWidth(17, 200)  # ledby
        tableView.setColumnWidth(18, 200)  # minister
        tableView.setColumnWidth(19, 200)  # baptizer
        tableView.setColumnWidth(20, 120)  # baptismday
        tableView.setColumnWidth(21, 250)  # venue
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
