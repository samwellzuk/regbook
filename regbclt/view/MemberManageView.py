# -*- coding: utf-8 -*-

"""
Module implementing MemberManageView.
"""

from PyQt5.QtCore import pyqtSlot, QModelIndex, Qt
from PyQt5.QtWidgets import QWidget, QMessageBox

from copy import copy
from comm.asynctask import coroutine, AsyncTask
from comm.utility import except_check
from data.members import MemberService
from data.model import Member
from vm.members import MembersModel

from .ui_MemberManageView import Ui_MemberManageView
from .ProgressDlg import ProgressDlg
from .MemberDlg import MemberDlg

_default_pagenum = '10'


class MemberManageView(QWidget, Ui_MemberManageView):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MemberManageView, self).__init__(parent)
        self.setupUi(self)

        self.pagenumEdit.setText(_default_pagenum)

        self._membersmodel = MembersModel()
        self.baseView.setModel(self._membersmodel)
        self._membersmodel.initView(self.baseView)

        self._membersmodel.sortChanged.connect(self.on_sortChanged)
        self._selectmodel = self.baseView.selectionModel()
        self._selectmodel.currentRowChanged.connect(self.on_table_change)

        self.svc = MemberService()
        self.progressdlg = ProgressDlg(parent=self)
        self.svc.progressUpdated.connect(self._update_progress)
        self.svc.progressTxtChanged.connect(self._update_label)

        self.total_pages_ = 0
        self.cur_page_ = 0
        self.num_page_ = int(_default_pagenum)

    @pyqtSlot(int)
    @except_check
    def _update_progress(self, progress):
        if self.progressdlg.is_open():
            self.progressdlg.setValue(progress)

    @pyqtSlot(str)
    @except_check
    def _update_label(self, txt):
        if self.progressdlg.is_open():
            self.progressdlg.setLabelText(txt)

    @coroutine(is_block=True)
    def _query_members(self):
        self.progressdlg.open()
        try:
            self._selectmodel.clear()
            kw = self.keywordEdit.text().strip()
            keyword = kw if kw else None
            self.num_page_ = int(self.pagenumEdit.text().strip())
            skip = self.cur_page_ * self.num_page_
            limit = self.num_page_
            sortkey = self._membersmodel.sortkey
            sortorder = self._membersmodel.sortorder

            total, members = yield AsyncTask(self.svc.query_members, skip, limit, keyword, sortkey, sortorder)

            self.total_pages_ = int(total / self.num_page_) + (1 if total % self.num_page_ > 0 else 0)

            self.totalpageLabel.setText(f"共有{total}条记录，分为{self.total_pages_}页，当前第{self.cur_page_ + 1}页")
            self.startButton.setEnabled(self.cur_page_ != 0)
            self.preButton.setEnabled(self.cur_page_ != 0)
            self.nextButton.setEnabled(self.total_pages_ > self.cur_page_ + 1)
            self.endButton.setEnabled(self.total_pages_ > self.cur_page_ + 1)
            self._membersmodel.reset_models(members)
        finally:
            self.progressdlg.close()

    @pyqtSlot(QModelIndex, QModelIndex)
    @except_check
    def on_table_change(self, current, previous):
        if current.isValid():
            self.modifyButton.setEnabled(True)
            self.videoButton.setEnabled(True)
            self.delButton.setEnabled(True)
            self.printButton.setEnabled(True)
        else:
            self.modifyButton.setEnabled(False)
            self.videoButton.setEnabled(False)
            self.delButton.setEnabled(False)
            self.printButton.setEnabled(False)

    @except_check
    def activeView(self):
        self.baseView.sortByColumn(-1, Qt.AscendingOrder)

    @pyqtSlot()
    @except_check
    def on_findButton_clicked(self):
        self.cur_page_ = 0
        self._query_members()

    @pyqtSlot()
    @except_check
    def on_refreshButton_clicked(self):
        self.keywordEdit.setText('')
        self.baseView.sortByColumn(-1, Qt.AscendingOrder)

    @pyqtSlot()
    @except_check
    def on_addButton_clicked(self):
        dlg = MemberDlg(Member(), parent=self)
        if dlg.exec() == MemberDlg.Accepted:
            member = self.svc.add_member(dlg.member)
            self._membersmodel.add_model(member)

    @pyqtSlot()
    @except_check
    def on_modifyButton_clicked(self):
        index = self._selectmodel.currentIndex()
        oldmem = self._membersmodel.get_model(index.row())
        dlg = MemberDlg(copy(oldmem), parent=self)
        if dlg.exec() == MemberDlg.Accepted:
            member = self.svc.update_member(oldmem, dlg.member)
            self._membersmodel.update_model(index.row(), member)

    @pyqtSlot()
    @except_check
    def on_delButton_clicked(self):
        index = self._selectmodel.currentIndex()
        member = self._membersmodel.get_model(index.row())
        r = QMessageBox.question(self, 'Warning', f'Are you sure to delete {member.name} [{member.cname}] ?')
        if r == QMessageBox.Yes:
            self.svc.del_member(member)
            self._membersmodel.remove_model(index.row())

    @pyqtSlot()
    @except_check
    def on_preButton_clicked(self):
        self.cur_page_ -= 1
        self._query_members()

    @pyqtSlot()
    @except_check
    def on_nextButton_clicked(self):
        self.cur_page_ += 1
        self._query_members()

    @pyqtSlot()
    @except_check
    def on_startButton_clicked(self):
        self.cur_page_ = 0
        self._query_members()

    @pyqtSlot()
    @except_check
    def on_endButton_clicked(self):
        self.cur_page_ = self.total_pages_ - 1 if self.total_pages_ > 0 else 0
        self._query_members()

    @pyqtSlot()
    @except_check
    def on_sortChanged(self):
        self.cur_page_ = 0
        self._query_members()

    @pyqtSlot(str)
    @except_check
    def on_keywordEdit_textChanged(self, p0):
        if p0.strip():
            self.findButton.setEnabled(True)
        else:
            self.findButton.setEnabled(False)

    @pyqtSlot()
    @except_check
    def on_keywordEdit_editingFinished(self):
        keyword = self.keywordEdit.text()
        if keyword:
            self.cur_page_ = 0
            self._query_members()

    @pyqtSlot()
    @except_check
    def on_pagenumEdit_editingFinished(self):
        pagenum = self.pagenumEdit.text().strip()
        # 输入无效, 空白, 强制设置默认值
        if not pagenum:
            pagenum = _default_pagenum
            self.pagenumEdit.setText(pagenum)
        self.cur_page_ = 0
        self._query_members()

    @pyqtSlot()
    @except_check
    def on_exportButton_clicked(self):
        pass

    @pyqtSlot()
    @except_check
    def on_videoButton_clicked(self):
        pass

    @pyqtSlot()
    @except_check
    def on_printButton_clicked(self):
        pass
