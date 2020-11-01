# -*- coding: utf-8 -*-

"""
Module implementing MemberManageView.
"""

from PyQt5.QtCore import pyqtSlot, QModelIndex
from PyQt5.QtWidgets import QWidget

from comm.asynctask import coroutine, AsyncTask
from comm.utility import except_check
from data.members import MemberService
from vm.members import MembersModel

from .ui_MemberManageView import Ui_MemberManageView
from .ProgressDlg import ProgressDlg

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

        self._selectmodel = self.baseView.selectionModel()
        self._selectmodel.currentRowChanged.connect(self.on_table_change)

        self.svc = MemberService()
        self.progressdlg = ProgressDlg(parent=self)
        self.svc.progressUpdated.connect(self._update_progress)
        self.svc.progressTxtChanged.connect(self._update_label)

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

    def activeView(self):
        pass

    @pyqtSlot()
    @except_check
    def on_findButton_clicked(self):
        pass

    @pyqtSlot()
    @except_check
    def on_refreshButton_clicked(self):
        pass

    @pyqtSlot()
    @except_check
    def on_addButton_clicked(self):
        pass

    @pyqtSlot()
    @except_check
    def on_exportButton_clicked(self):
        pass

    @pyqtSlot()
    @except_check
    def on_modifyButton_clicked(self):
        pass

    @pyqtSlot()
    @except_check
    def on_videoButton_clicked(self):
        pass

    @pyqtSlot()
    @except_check
    def on_delButton_clicked(self):
        pass

    @pyqtSlot()
    @except_check
    def on_printButton_clicked(self):
        pass

    @pyqtSlot()
    @except_check
    def on_preButton_clicked(self):
        pass

    @pyqtSlot()
    @except_check
    def on_nextButton_clicked(self):
        pass

    @pyqtSlot(str)
    @except_check
    def on_keywordEdit_textEdited(self, p0):
        if p0.strip():
            self.findButton.setEnabled(True)
        else:
            self.findButton.setEnabled(False)

    @pyqtSlot()
    @except_check
    def on_pagenumEdit_editingFinished(self):
        pagenum = self.pagenumEdit.text().strip()
        # 输入无效, 空白, 强制设置默认值
        if not pagenum:
            pagenum = _default_pagenum
            self.pagenumEdit.setText(pagenum)

