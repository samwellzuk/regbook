# -*- coding: utf-8 -*-
import os
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant, Qt, pyqtSignal

from pyexcelerate import Workbook, Style, Color, Alignment, Font
from pyexcelerate.Range import Range
import win32api

from comm.utility import except_check

_col_indexs = [
    'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O',
    'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y',
    'Z', 'AA', 'AB', 'AC', 'AD',
    'AE', 'AF', 'AG', 'AH', 'AI',
    'AJ', 'AK', 'AL', 'AM', 'AN',
]


class CommonReport(QAbstractTableModel):
    progressUpdated = pyqtSignal(int)
    progressTxtChanged = pyqtSignal(str)

    def __init__(self, models, max_display, parent=None):
        super(CommonReport, self).__init__(parent=parent)
        self.col_indexs = _col_indexs
        self.models = models
        self.max_display = max_display

    def _row_count(self, maxlen):
        return maxlen

    def _column_count(self):
        return 0

    def _table_title_count(self):
        return 0

    def _merge_cell(self):
        """
        :return: row, col, rowcount, colcount
        """
        pass

    def _cell_value(self, row, column):
        pass

    def _cell_style(self, row, column):
        """
        return blod,horizontal,vertical
        blod : True False
        horizontal : 'left', 'center', 'right'
        vertical : 'top', 'center', 'bottom'
        """
        pass

    def _column_width(self, column):
        return 0

    @except_check
    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        maxlen = self.max_display if len(self.models) > self.max_display else len(self.models)
        return self._row_count(maxlen)

    @except_check
    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return self._column_count()

    @except_check
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.col_indexs[section]
        else:
            return int(section + 1)

    @except_check
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        column = index.column()
        row = index.row()
        if role == Qt.TextAlignmentRole:
            _, horizontal, vertical = self._cell_style(row, column)
            flag = 0
            if horizontal == 'left':
                flag |= Qt.AlignLeft
            elif horizontal == 'center':
                flag |= Qt.AlignHCenter
            elif horizontal == 'right':
                flag |= Qt.AlignRight
            if vertical == 'top':
                flag |= Qt.AlignTop
            elif vertical == 'center':
                flag |= Qt.AlignVCenter
            elif vertical == 'bottom':
                flag |= Qt.AlignBottom
            return flag
        elif role == Qt.DisplayRole:
            value = self._cell_value(row, column)
            if value != None:
                return value
        return QVariant()

    def initView(self, tableView):
        count = self.columnCount()
        for col in range(count):
            width = self._column_width(col)
            if width != None:
                tableView.setColumnWidth(col, width * 8)

        for row, col, rowcount, colcount in self._merge_cell():
            tableView.setSpan(row, col, rowcount, colcount)

        tableView.setWordWrap(True)

    def exportModel(self, file, tablename):
        self.progressTxtChanged.emit('Exporting members ...')
        self.progressUpdated.emit(0)

        wb = Workbook()
        ws = wb.new_sheet(tablename)

        # -------------------------------
        # 写内容
        self.progressUpdated.emit(10)
        rowcount = self._row_count(len(self.models))
        colcount = self._column_count()
        for row in range(rowcount):
            for col in range(colcount):
                index = self.createIndex(row, col)
                ws[row + 1][col + 1].value = self._cell_value(row, col)
        # -------------------------------
        # 设置列宽
        self.progressUpdated.emit(40)
        for col in range(colcount):
            width = self._column_width(col)
            if width != None:
                ws.set_col_style(col + 1, Style(size=width))

        # -------------------------------
        # 设置边框
        self.progressUpdated.emit(50)
        title_count = self._table_title_count()
        r = ws.range(Range.coordinate_to_string((1 + title_count, 1)),
                     Range.coordinate_to_string((ws.num_rows, ws.num_columns)))
        r.style.borders.top.color = Color(0, 0, 0)
        r.style.borders.bottom.color = Color(0, 0, 0)
        r.style.borders.left.color = Color(0, 0, 0)
        r.style.borders.right.color = Color(0, 0, 0)

        # -------------------------------
        # 设置风格
        self.progressUpdated.emit(60)
        for row in range(rowcount):
            for col in range(colcount):
                bold, horizontal, vertical = self._cell_style(row, col)
                if bold:
                    ws[row + 1][col + 1].style.font.bold = True
                ws[row + 1][col + 1].style.alignment.vertical = vertical
                ws[row + 1][col + 1].style.alignment.horizontal = horizontal

        # -------------------------------
        # 合并头单元格
        self.progressUpdated.emit(70)
        for row, col, rowcount, colcount in self._merge_cell():
            r = ws.range(Range.coordinate_to_string((row + 1, col + 1)),
                         Range.coordinate_to_string((row + rowcount, col + colcount)))
            r.merge()
        self.progressUpdated.emit(80)
        wb.save(file)
        self.progressUpdated.emit(90)
        filedir = os.path.dirname(file)
        win32api.ShellExecute(None, 'open', file, None, filedir, 5)
        self.progressUpdated.emit(100)
