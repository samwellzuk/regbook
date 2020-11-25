# -*- coding: utf-8 -*-
import copy
from PyQt5.QtCore import QAbstractListModel, QModelIndex, QVariant, Qt, QSize, QRect
from PyQt5.QtGui import QPixmap, QPainter

from comm.utility import except_check
from comm.fileicon import query_file_icon
from settings import best_thumbnail_width


# _role_dict = {
#     0: 'DisplayRole',
#     1: 'DecorationRole',
#     2: 'EditRole',
#     3: 'ToolTipRole',
#     4: 'StatusTipRole',
#     5: 'WhatsThisRole',
#     13: 'SizeHintRole',
#     6: 'FontRole',
#     7: 'TextAlignmentRole',
#     8: 'BackgroundRole',
#     9: 'ForegroundRole',
#     10: 'CheckStateRole',
#     14: 'InitialSortOrderRole',
#     11: 'AccessibleTextRole',
#     12: 'AccessibleDescriptionRole',
#     256: 'UserRole',
# }


class VirFileModel(QAbstractListModel):

    def __init__(self):
        super(VirFileModel, self).__init__()
        self._models = []
        self._pixmaps = []

    def _get_pixmap(self, m):
        if m.thumbnail:
            pixmap = QPixmap()
            pixmap.loadFromData(m.thumbnail)
            return pixmap
        if suffix := m.file_suffix():
            if imgbytes := query_file_icon(suffix):
                pixmap = QPixmap()
                pixmap.loadFromData(imgbytes)
                return pixmap
        return QPixmap(":/images/default.ico")

    def _get_best_pixmap(self, pixmap):
        # pixmap need scale
        if pixmap.height() > best_thumbnail_width or pixmap.width() > best_thumbnail_width:
            pixmap = pixmap.scaled(best_thumbnail_width, best_thumbnail_width,
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # align pixmap to bottom
        if pixmap.height() < best_thumbnail_width:
            dstimg = QPixmap(best_thumbnail_width, best_thumbnail_width)
            dstimg.fill(Qt.transparent)
            painter = QPainter()
            if painter.begin(dstimg):
                x = int((best_thumbnail_width - pixmap.width()) / 2)
                y = int(best_thumbnail_width - pixmap.height())
                dstrect = QRect(x, y, pixmap.width(), pixmap.height())
                srcrect = QRect(0, 0, pixmap.width(), pixmap.height())
                painter.drawPixmap(dstrect, pixmap, srcrect)
                painter.end()
                pixmap = dstimg
        return pixmap

    @except_check
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return int(section + 1)
            else:
                return int(section + 1)
        return super(VirFileModel, self).headerData(section, orientation, role)

    @except_check
    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._models)

    @except_check
    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return super(VirFileModel, self).flags(index)

    @except_check
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            row = index.row()
            m = self._models[row]
            if role == Qt.SizeHintRole:
                # 10 margin, 60 for 3 line text
                return QSize(best_thumbnail_width + 10, best_thumbnail_width + 10 + 60)
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            elif role == Qt.DisplayRole:
                return m.filename
            elif role == Qt.DecorationRole:
                return self._pixmaps[row]
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
        img = self._get_best_pixmap(self._get_pixmap(m))
        self.beginInsertRows(QModelIndex(), pos, pos)
        self._models.insert(pos, m)
        self._pixmaps.insert(pos, img)
        self.endInsertRows()

    def get_model(self, row):
        return self._models[row]

    def update_model(self, row, m):
        self._pixmaps[row] = self._get_best_pixmap(self._get_pixmap(m))
        self._models[row] = m
        left = self.index(row, 0)
        rigth = self.index(row, 1)
        self.dataChanged.emit(left, rigth)

    def remove_model(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._models[row]
        del self._pixmaps[row]
        self.endRemoveRows()

    def reset_models(self, mlist=None):
        self.beginResetModel()
        self._models = [] if mlist is None else mlist
        self._pixmaps = [self._get_best_pixmap(self._get_pixmap(m)) for m in mlist]
        self.endResetModel()
