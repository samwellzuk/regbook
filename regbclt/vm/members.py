# -*- coding: utf-8 -*-
# Created by samwell
import weakref
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant, Qt, pyqtSignal, QByteArray
from PyQt5.QtGui import QPixmap

from data.model import head_high, head_width, get_flat_top_fields


class MembersModel(QAbstractTableModel):
    sortChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._avatar_default = QPixmap(":/images/thumbnail.png")
        self._models = []
        self._avatars = []
        self._header = get_flat_top_fields()
        self.sortkey = None
        self.sortorder = None
        self.view = None

    def sort(self, column, order=Qt.AscendingOrder):
        if column == -1 or column == 0:
            self.sortkey = None
            self.sortorder = None
        else:
            k1, k2, fobj = self._header[column - 1]
            if fobj.is_readonly():
                self.sortkey = None
                self.sortorder = None
            else:
                self.sortkey = f'{k1}.{k2}' if k2 else k1
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
            k1, k2, _ = self._header[section - 1]
            return f'{k1}.{k2}' if k2 else k1
        else:
            return int(section + 1)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._models)):
            return QVariant()
        column = index.column()
        row = index.row()
        item = self._models[row]
        if column == 0:
            if role == Qt.DecorationRole:
                if self._avatars[row]:
                    return self._avatars[row]
                else:
                    return self._avatar_default
        else:
            k1, k2, fobj = self._header[column - 1]
            if role == Qt.DisplayRole:
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
        for i, item in enumerate(self._header):
            _, _, fobj = item
            tableView.setColumnWidth(i + 1, fobj.width)
        self.view = weakref.ref(tableView)

    def _update_high(self):
        tableview = self.view()
        if tableview:
            for i in range(len(self._models)):
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


class ObjModel(QAbstractTableModel):
    def __init__(self, model, headers, parent=None):
        super().__init__(parent=parent)
        self.model = model
        self.headers = headers

    def initView(self, tableView):
        pass


class ListModel(QAbstractTableModel):
    def __init__(self, models, headers, parent=None):
        super().__init__(parent=parent)
        self.models = models
        self.headers = headers

    def initView(self, tableView):
        pass
