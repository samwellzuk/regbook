# -*- coding: utf-8 -*-
# Created by samwell
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant, Qt, pyqtSignal

from data.members import MemberService
from data.model import Member


class MembersModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._models = []
        self._header = [
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
        item = self._models[index.row()]
        if role == Qt.DisplayRole:
            if column == 0:
                return item.name
            elif column == 1:
                return item.cname
            elif column == 2:
                return item.sex
            elif column == 3:
                return item.birthday.strftime('%b/%d/%Y')
            elif column == 4:
                return item.nation
            elif column == 5:
                return item.street
            elif column == 6:
                return item.city
            elif column == 7:
                return item.province
            elif column == 8:
                return item.homephone
            elif column == 9:
                return item.workphone
            elif column == 10:
                return item.cellphone
            elif column == 11:
                return item.education
            elif column == 12:
                return item.occupation
            elif column == 13:
                return item.father
            elif column == 14:
                return item.mother
            elif column == 15:
                return item.saved
            elif column == 16:
                return item.ledby
            elif column == 17:
                return item.minister
            elif column == 18:
                return item.baptizer
            elif column == 19:
                return item.baptismday.strftime('%b/%d/%Y')
            elif column == 20:
                return item.venue
        return QVariant()

    def initView(self, tableView):
        tableView.setColumnWidth(0, 100)  # name
        tableView.setColumnWidth(1, 100)  # cname
        tableView.setColumnWidth(2, 100)  # sex
        tableView.setColumnWidth(3, 100)  # birthday
        tableView.setColumnWidth(4, 100)  # nation
        tableView.setColumnWidth(5, 100)  # street
        tableView.setColumnWidth(6, 100)  # city
        tableView.setColumnWidth(7, 100)  # province
        tableView.setColumnWidth(8, 100)  # homephone
        tableView.setColumnWidth(9, 100)  # workphone
        tableView.setColumnWidth(10, 100)  # cellphone
        tableView.setColumnWidth(11, 100)  # education
        tableView.setColumnWidth(12, 100)  # occupation
        tableView.setColumnWidth(13, 100)  # father
        tableView.setColumnWidth(14, 100)  # mother
        tableView.setColumnWidth(15, 100)  # saved
        tableView.setColumnWidth(16, 100)  # ledby
        tableView.setColumnWidth(17, 100)  # minister
        tableView.setColumnWidth(18, 100)  # baptizer
        tableView.setColumnWidth(19, 100)  # baptismday
        tableView.setColumnWidth(20, 100)  # venue

    def add_model(self, m, pos=0):
        self.beginInsertRows(QModelIndex(), pos, pos)
        self._models.insert(pos, m)
        self.endInsertRows()

    def get_model(self, row):
        return self._models[row]

    def update_model(self, row, m):
        self._models[row] = m
        left = self.index(row, 0)
        rigth = self.index(row, len(self._header))
        self.dataChanged.emit(left, rigth)

    def remove_model(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._models[row]
        self.endRemoveRows()

    def reset_models(self, mlist=None):
        self.beginResetModel()
        self._models = [] if mlist is None else mlist
        self.endResetModel()
