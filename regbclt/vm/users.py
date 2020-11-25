# -*- coding: utf-8 -*-
# Created by samwell
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant, Qt
from comm.utility import except_check


class UsersModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._models = []
        self._header = [
            'User Name',
            'Is Admin',
        ]

    @except_check
    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._models)

    @except_check
    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._header)

    @except_check
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._header[section]
            else:
                return int(section + 1)
        return super(UsersModel, self).headerData(section, orientation, role)

    @except_check
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            column = index.column()
            item = self._models[index.row()]
            if role == Qt.DisplayRole:
                if column == 0:
                    return item.user
                elif column == 1:
                    return 'Yes' if item.is_admin() else ''
        return QVariant()

    def initView(self, tableView):
        tableView.setColumnWidth(0, 100)
        tableView.setColumnWidth(1, 100)

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
