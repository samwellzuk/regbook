# -*- coding: utf-8 -*-

"""
Module implementing MemberManageView.
"""

from PyQt5.QtCore import pyqtSlot, QModelIndex, Qt
from PyQt5.QtWidgets import QWidget, QMessageBox

from copy import copy
from comm.asynctask import coroutine, AsyncTask
from comm.utility import except_check

from data.model import Member
from data.dbmgr import DBManager
from vm.members import MembersModel

from data.members import MemberService
from data.vfile import VirFileService

from .ui_MemberManageView import Ui_MemberManageView
from .ProgressDlg import ProgressDlg
from .MemberDlg import MemberDlg
from .MediaManageDlg import MediaManageDlg

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
        self.svc.progressUpdated.connect(self.progressdlg.setValue)
        self.svc.progressTxtChanged.connect(self.progressdlg.setLabelText)

        self.vif_svc = VirFileService()
        self.vif_svc.progressUpdated.connect(self.progressdlg.setValue)
        self.vif_svc.progressTxtChanged.connect(self.progressdlg.setLabelText)

        self.total_pages_ = 0
        self.cur_page_ = 0
        self.num_page_ = int(_default_pagenum)

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

    @coroutine(is_block=True)
    def _query_photo(self, member):
        if member.thumbnail is not None and member.avatar is None:
            self.progressdlg.open()
            try:
                yield AsyncTask(self.svc.get_member_avatar, member)
            finally:
                self.progressdlg.close()

    @coroutine(is_block=True)
    def _del_member(self, member):
        self.progressdlg.open()
        try:
            vfiles = yield AsyncTask(self.vif_svc.get_member_files, member)
            if vfiles:
                yield AsyncTask(self.vif_svc.delete_files, vfiles)
            yield AsyncTask(self.svc.del_member, member)
        finally:
            self.progressdlg.close()

    @pyqtSlot(QModelIndex, QModelIndex)
    @except_check
    def on_table_change(self, current, previous):
        if current.isValid():
            self.modifyButton.setEnabled(True)
            self.videoButton.setEnabled(True)
            # only allow admin to delete member
            self.delButton.setEnabled(DBManager().cur_user.is_admin())
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

    @pyqtSlot(QModelIndex)
    @except_check
    def on_baseView_doubleClicked(self, clickindex):
        oldmem = self._membersmodel.get_model(clickindex.row())
        self._query_photo(oldmem)
        dlg = MemberDlg(copy(oldmem), parent=self)
        if dlg.exec() == MemberDlg.Accepted:
            member = self.svc.update_member(oldmem, dlg.member)
            self._membersmodel.update_model(clickindex.row(), member)

    @pyqtSlot()
    @except_check
    def on_modifyButton_clicked(self):
        index = self._selectmodel.currentIndex()
        oldmem = self._membersmodel.get_model(index.row())
        self._query_photo(oldmem)
        dlg = MemberDlg(copy(oldmem), parent=self)
        if dlg.exec() == MemberDlg.Accepted:
            member = self.svc.update_member(oldmem, dlg.member)
            self._membersmodel.update_model(index.row(), member)

    @pyqtSlot()
    @except_check
    def on_delButton_clicked(self):
        index = self._selectmodel.currentIndex()
        member = self._membersmodel.get_model(index.row())
        r = QMessageBox.question(
            self,
            'Warning',
            f'Are you sure to delete {member.name} [{member.cname}]?\nAll media files will be delete too!')
        if r == QMessageBox.Yes:
            self._del_member(member)
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
        index = self._selectmodel.currentIndex()
        member = self._membersmodel.get_model(index.row())
        dlg = MediaManageDlg(member, parent=self)
        dlg.exec()

    @pyqtSlot()
    @except_check
    def on_printButton_clicked(self):
        pass
