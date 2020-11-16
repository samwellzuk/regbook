# -*- coding: utf-8 -*-

from .commreport import CommonReport
from .members import _member_header


class PersonReport(CommonReport):

    def __init__(self, models, max_display, parent=None):
        super(PersonReport, self).__init__(models, max_display, parent=parent)
        self.model_header = _member_header

    def _row_count(self, maxlen):
        row = 1 + len(self.models)
        return row

    def _column_count(self):
        return len(self.model_header)

    def _merge_cell(self):
        return []

    def _cell_value(self, row, column):
        currow = row
        if currow == 0:
            return self.model_header[column][0]
        else:
            currow -= 1
            person = self.models[currow]
            key = self.model_header[column][0]
            val = getattr(person, key)
            if (column == 3 or column == 19) and val:
                return val.strftime('%b %d %Y')
            else:
                return val

    def _cell_style(self, row, column):
        return False, 'right', 'center'

    def _column_width(self, column):
        return self.model_header[column][1] // 10
