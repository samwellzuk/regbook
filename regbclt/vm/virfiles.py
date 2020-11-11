# -*- coding: utf-8 -*-
import copy
from PyQt5.QtCore import QAbstractListModel, QModelIndex, QVariant, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox

from comm.utility import except_check
from comm.fileicon import query_file_icon

_filename_max = 12


class VirFileModel(QAbstractListModel):

    def __init__(self):
        super(VirFileModel, self).__init__()
        self._models = []

    @except_check
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return int(section + 1)
        else:
            return int(section + 1)

    @except_check
    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._models)

    @except_check
    def flags(self, index):
        if not index.isValid():
            return super().flags(index)
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    @except_check
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        row = index.row()
        m = self._models[row]
        if role == Qt.DisplayRole:
            return f'{m.filename[:_filename_max - 3]}...' if len(m.filename) > _filename_max else m.filename
        elif role == Qt.DecorationRole:
            if m.thumbnail:
                bmp = QPixmap()
                bmp.loadFromData(m.thumbnail)
                return bmp
            postfix = m.filename.split('.')[-1]
            imgbytes = query_file_icon(f'.{postfix.lower()}')
            if imgbytes:
                bmp = QPixmap()
                bmp.loadFromData(imgbytes)
                return bmp
            return QPixmap(":/images/default.ico")
        elif role == Qt.ToolTipRole:
            tooltip = [
                f'name: {m.filename}',
                f'length: {m.length / 1024 / 1024:.2f}M',
                f'upload date: {m.uploadDate.strftime("%Y-%m-%d %H:%M:%S")}',
                f'upload user: {m.upload_user}',
                f'md5 code: {m.md5}'
            ]
            return '\n'.join(tooltip)
        return QVariant()

    def add_model(self, m, pos=0):
        self.beginInsertRows(QModelIndex(), pos, pos)
        self._models.insert(pos, m)
        self.endInsertRows()

    def get_model(self, row):
        return self._models[row]

    def update_model(self, row, m):
        self._models[row] = m
        left = self.index(row, 0)
        rigth = self.index(row, 1)
        self.dataChanged.emit(left, rigth)

    def remove_model(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._models[row]
        self.endRemoveRows()

    def reset_models(self, mlist=None):
        self.beginResetModel()
        self._models = [] if mlist is None else mlist
        self.endResetModel()
