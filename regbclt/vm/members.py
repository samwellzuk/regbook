# -*- coding: utf-8 -*-
# Created by samwell
import weakref
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant, Qt, pyqtSignal, QByteArray
from PyQt5.QtGui import QPixmap

from comm.utility import except_check
from data.model import head_high, head_width, get_flat_top_fields
from .delegate import Qt_ItemDataRole_Field, Qt_ItemDataRole_FieldData


class MembersModel(QAbstractTableModel):
    sortChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.avatar_default = QPixmap(":/images/thumbnail.png")
        self.models = []
        self.avatars = []
        self.headers = get_flat_top_fields()
        self.sortkey = None
        self.sortorder = None
        self.view = None

    @except_check
    def sort(self, column, order=Qt.AscendingOrder):
        if column == -1 or column == 0:
            self.sortkey = None
            self.sortorder = None
        else:
            k1, k2, fobj = self.headers[column - 1]
            if fobj.is_readonly():
                self.sortkey = None
                self.sortorder = None
            else:
                self.sortkey = f'{k1}.{k2}' if k2 else k1
                self.sortorder = order
        self.sortChanged.emit()

    @except_check
    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.models)

    @except_check
    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.headers) + 1

    @except_check
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return 'avatar'
                k1, k2, _ = self.headers[section - 1]
                return f'{k1}.{k2}' if k2 else k1
            else:
                return int(section + 1)
        return super(MembersModel, self).headerData(section, orientation, role)

    @except_check
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            column = index.column()
            row = index.row()
            item = self.models[row]
            if column == 0:
                if role == Qt.DecorationRole:
                    if self.avatars[row]:
                        return self.avatars[row]
                    else:
                        return self.avatar_default
            else:
                k1, k2, fobj = self.headers[column - 1]
                if role == Qt.DisplayRole:
                    if fobj.is_readonly():
                        obj = item
                        val = None
                        if k2:
                            obj = getattr(obj, k1)
                    else:
                        obj = item
                        val = getattr(obj, k1)
                        if k2:
                            obj = val
                            val = getattr(obj, k2)
                    return fobj.outputobj.to_str(obj, val)
                elif role == Qt.ToolTipRole:
                    return fobj.title
                elif role == Qt.TextAlignmentRole:
                    if fobj.horizontal == 'left':
                        aligrole = Qt.AlignLeft
                    elif fobj.horizontal == 'right':
                        aligrole = Qt.AlignRight
                    else:
                        aligrole = Qt.AlignHCenter
                    if fobj.vertical == 'top':
                        aligrole |= Qt.AlignTop
                    elif fobj.vertical == 'bottom':
                        aligrole |= Qt.AlignBottom
                    else:
                        aligrole |= Qt.AlignVCenter
                    return aligrole
        return QVariant()

    def initView(self, tableView):
        tableView.setColumnWidth(0, head_width)  # name
        for i, item in enumerate(self.headers):
            _, _, fobj = item
            tableView.setColumnWidth(i + 1, fobj.width)
        self.view = weakref.ref(tableView)

    def _update_high(self):
        tableview = self.view()
        if tableview:
            for i in range(len(self.models)):
                h = tableview.rowHeight(i)
                if h != head_high:
                    tableview.setRowHeight(i, head_high)

    def _load_pic(self, imgb):
        if imgb is None:
            return None
        b = QByteArray(imgb)
        bmp = QPixmap()
        bmp.loadFromData(b)
        return bmp

    def add_model(self, m, pos=0):
        self.beginInsertRows(QModelIndex(), pos, pos)
        self.models.insert(pos, m)
        self.avatars.insert(pos, self._load_pic(m.thumbnail))
        self.endInsertRows()
        self._update_high()

    def get_model(self, row):
        return self.models[row]

    def update_model(self, row, m):
        self.models[row] = m
        self.avatars[row] = self._load_pic(m.thumbnail)

        left = self.index(row, 0)
        rigth = self.index(row, len(self.headers))
        self.dataChanged.emit(left, rigth)

    def remove_model(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        del self.models[row]
        del self.avatars[row]
        self.endRemoveRows()

    def reset_models(self, mlist=None):
        self.beginResetModel()
        if mlist:
            self.models = mlist
            self.avatars = [self._load_pic(m.thumbnail) for m in mlist]
        else:
            self.models = []
            self.avatars = []
        self.endResetModel()
        self._update_high()


class ObjModel(QAbstractTableModel):
    def __init__(self, model, headers, parent=None):
        super().__init__(parent=parent)
        self.model = model
        self.headers = headers

    @except_check
    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.headers)

    @except_check
    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return 2

    @except_check
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return 'Name'
                else:
                    return 'Value'
            else:
                return int(section + 1)
        return super(ObjModel, self).headerData(section, orientation, role)

    @except_check
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            column = index.column()
            row = index.row()
            item = self.model
            field, fobj = self.headers[row]
            if column == 0:
                if role == Qt.DisplayRole:
                    return fobj.title
                elif role == Qt.TextAlignmentRole:
                    return Qt.AlignLeft | Qt.AlignVCenter
            elif column == 1:
                if role == Qt.DisplayRole:
                    val = getattr(item, field)
                    return fobj.outputobj.to_str(item, val)
                elif role == Qt.EditRole:
                    val = getattr(item, field)
                    return val
                elif role == Qt.TextAlignmentRole:
                    if fobj.horizontal == 'left':
                        aligrole = Qt.AlignLeft
                    elif fobj.horizontal == 'right':
                        aligrole = Qt.AlignRight
                    else:
                        aligrole = Qt.AlignHCenter
                    if fobj.vertical == 'top':
                        aligrole |= Qt.AlignTop
                    elif fobj.vertical == 'bottom':
                        aligrole |= Qt.AlignBottom
                    else:
                        aligrole |= Qt.AlignVCenter
                    return aligrole
                elif role == Qt_ItemDataRole_Field:
                    return fobj
                elif role == Qt_ItemDataRole_FieldData:
                    val = getattr(item, field)
                    return item, val
        return QVariant()

    @except_check
    def flags(self, index):
        if index.isValid():
            column = index.column()
            if column == 1:
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
            else:
                return Qt.NoItemFlags
        return super(ObjModel, self).flags(index)

    @except_check
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            row = index.row()
            column = index.column()
            item = self.model
            field, _ = self.headers[row]
            if column == 1 and role == Qt.EditRole:
                setattr(item, field, value)
                self.dataChanged.emit(index, index)
                return True
        return super(ObjModel, self).setData(index, value, role)

    def initView(self, tableView):
        tableView.setColumnWidth(0, 150)
        tableView.setColumnWidth(1, 350)


class ListModel(QAbstractTableModel):
    def __init__(self, models, headers, parent=None):
        super().__init__(parent=parent)
        self.models = models
        self.headers = headers

    @except_check
    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.models)

    @except_check
    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.headers)

    @except_check
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section][0]
            else:
                return int(section + 1)
        return super(ListModel, self).headerData(section, orientation, role)

    @except_check
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            column = index.column()
            row = index.row()
            item = self.models[row]
            field, fobj = self.headers[column]
            if role == Qt.DisplayRole:
                val = getattr(item, field)
                return fobj.outputobj.to_str(item, val)
            elif role == Qt.EditRole:
                val = getattr(item, field)
                return val
            elif role == Qt.ToolTipRole:
                return fobj.title
            elif role == Qt.TextAlignmentRole:
                if fobj.horizontal == 'left':
                    aligrole = Qt.AlignLeft
                elif fobj.horizontal == 'right':
                    aligrole = Qt.AlignRight
                else:
                    aligrole = Qt.AlignHCenter
                if fobj.vertical == 'top':
                    aligrole |= Qt.AlignTop
                elif fobj.vertical == 'bottom':
                    aligrole |= Qt.AlignBottom
                else:
                    aligrole |= Qt.AlignVCenter
                return aligrole
            elif role == Qt_ItemDataRole_Field:
                return fobj
            elif role == Qt_ItemDataRole_FieldData:
                val = getattr(item, field)
                return item, val
        return QVariant()

    @except_check
    def flags(self, index):
        if index.isValid():
            column = index.column()
            if 0 <= column < len(self.headers):
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        return super(ListModel, self).flags(index)

    @except_check
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            row = index.row()
            column = index.column()
            item = self.models[row]
            field, _ = self.headers[column]
            if role == Qt.EditRole:
                setattr(item, field, value)
                self.dataChanged.emit(index, index)
                return True
        return super(ListModel, self).setData(index, value, role)

    def add_model(self, m, pos=0):
        self.beginInsertRows(QModelIndex(), pos, pos)
        self.models.insert(pos, m)
        self.endInsertRows()

    def remove_model(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        del self.models[row]
        self.endRemoveRows()

    def count_model(self):
        return len(self.models)

    def initView(self, tableView):
        for i, item in enumerate(self.headers):
            _, fobj = item
            tableView.setColumnWidth(i, fobj.width)
