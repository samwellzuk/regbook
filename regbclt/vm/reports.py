# -*- coding: utf-8 -*-
import os
from abc import ABC, abstractmethod
from PyQt5.QtCore import QObject, pyqtSignal

from pyexcelerate import Workbook, Style, Color, Alignment, Font
from pyexcelerate.Range import Range
import win32api

from comm.utility import except_check
from data.model import get_flat_top_fields, get_group_list_fields


class BaseModel(ABC):
    @abstractmethod
    def row_count(self):
        raise NotImplementedError('row_count')

    @abstractmethod
    def column_count(self):
        raise NotImplementedError('column_count')

    def table_title_count(self):
        return 0

    def merge_cell(self):
        """
        :return: row, col, rowcount, colcount
        """
        return []

    @abstractmethod
    def cell_value(self, row, column):
        raise NotImplementedError('cell_value')

    @abstractmethod
    def cell_style(self, row, column):
        """
        return blod,horizontal,vertical
        blod : True False
        horizontal : 'left', 'center', 'right'
        vertical : 'top', 'center', 'bottom'
        """
        raise NotImplementedError('cell_style')

    @abstractmethod
    def column_width(self, column):
        raise NotImplementedError('column_width')


class TopModel(BaseModel):

    def __init__(self, models, headers):
        self.models = models
        self.headers = headers

    def row_count(self):
        return len(self.models) + 1

    def column_count(self):
        return len(self.headers) + 1

    def cell_value(self, row, column):
        if column == 0:
            if row == 0:
                return 'ID'
            return row
        k1, k2, _ = self.headers[column - 1]
        if row == 0:
            return f'{k1}.{k2}' if k2 else k1
        else:
            m = self.models[row - 1]
            return m[k1][k2] if k2 else m[k1]

    def cell_style(self, row, column):
        if row == 0:
            return True, 'center', 'center'
        elif column == 0:
            return False, 'left', 'center'
        else:
            _, _, fobj = self.headers[column - 1]
            return fobj.blod, fobj.horizontal, fobj.vertical

    def column_width(self, column):
        if column == 0:
            return 5
        _, _, fobj = self.headers[column - 1]
        return fobj.width // 10


class ListModel(BaseModel):

    def __init__(self, models, field, headers):
        self.headers = headers
        self.models = []
        self.indexs = []
        self.merges = []
        for i, m in enumerate(models):
            mlist = m[field]
            if count := len(mlist):
                id = i + 1
                start = len(self.indexs) + 1
                for fm in mlist:
                    self.indexs.append(id)
                    self.models.append(fm)
                self.merges.append((start, count))

    def row_count(self):
        return len(self.models) + 1

    def column_count(self):
        return len(self.headers) + 1

    def merge_cell(self):
        for start, count in self.merges:
            yield start, 0, count, 1

    def cell_value(self, row, column):
        if column == 0:
            if row == 0:
                return 'ID'
            return self.indexs[row - 1]
        k, _ = self.headers[column - 1]
        if row == 0:
            return k
        else:
            m = self.models[row - 1]
            return m[k]

    def cell_style(self, row, column):
        if row == 0:
            return True, 'center', 'center'
        elif column == 0:
            return False, 'left', 'center'
        else:
            _, fobj = self.headers[column - 1]
            return fobj.blod, fobj.horizontal, fobj.vertical

    def column_width(self, column):
        if column == 0:
            return 5
        _, fobj = self.headers[column - 1]
        return fobj.width // 10


class MemberReport(QObject):
    progressUpdated = pyqtSignal(int)
    progressTxtChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MemberReport, self).__init__(parent=parent)

    def _export_page(self, ws, model, cur, rate):
        # -------------------------------
        # 写内容
        self.progressUpdated.emit(cur)
        rowcount = model.row_count()
        colcount = model.column_count()
        for row in range(rowcount):
            for col in range(colcount):
                ws[row + 1][col + 1].value = model.cell_value(row, col)
        # -------------------------------
        # 设置列宽
        self.progressUpdated.emit(cur + int(rate * 20 / 100))
        for col in range(colcount):
            if width := model.column_width(col):
                ws.set_col_style(col + 1, Style(size=width))

        # -------------------------------
        # 设置边框
        self.progressUpdated.emit(cur + int(rate * 40 / 100))
        title_count = model.table_title_count()
        r = ws.range(Range.coordinate_to_string((1 + title_count, 1)),
                     Range.coordinate_to_string((ws.num_rows, ws.num_columns)))
        r.style.borders.top.color = Color(0, 0, 0)
        r.style.borders.bottom.color = Color(0, 0, 0)
        r.style.borders.left.color = Color(0, 0, 0)
        r.style.borders.right.color = Color(0, 0, 0)

        # -------------------------------
        # 设置风格
        self.progressUpdated.emit(cur + int(rate * 60 / 100))
        for row in range(rowcount):
            for col in range(colcount):
                bold, horizontal, vertical = model.cell_style(row, col)
                if bold:
                    ws[row + 1][col + 1].style.font.bold = True
                ws[row + 1][col + 1].style.alignment.vertical = vertical
                ws[row + 1][col + 1].style.alignment.horizontal = horizontal

        # -------------------------------
        # 合并头单元格
        self.progressUpdated.emit(cur + int(rate * 80 / 100))
        for row, col, rowcount, colcount in model.merge_cell():
            r = ws.range(Range.coordinate_to_string((row + 1, col + 1)),
                         Range.coordinate_to_string((row + rowcount, col + colcount)))
            r.merge()
        self.progressUpdated.emit(cur + rate)

    def exportModel(self, file, members):
        self.progressTxtChanged.emit('Exporting members ...')
        self.progressUpdated.emit(0)
        # ----------------------------
        datas = []
        for m in members:
            datas.append(m.to_display_dict())

        pages = [('Member', TopModel(datas, get_flat_top_fields()))]
        groupdi = get_group_list_fields()
        for k in groupdi:
            field, cls = k
            fieldlist = groupdi[k]
            pages.append((cls, ListModel(datas, field, fieldlist)))
        self.progressUpdated.emit(10)
        # ----------------------------
        wb = Workbook()
        cur = 10
        rate = 80 // len(pages)
        for name, model in pages:
            ws = wb.new_sheet(name)
            self._export_page(ws, model, cur, rate)
            cur += rate
        self.progressUpdated.emit(90)
        # ----------------------------
        wb.save(file)
        filedir = os.path.dirname(file)
        win32api.ShellExecute(None, 'open', file, None, filedir, 5)
        self.progressUpdated.emit(100)
