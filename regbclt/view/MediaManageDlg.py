# -*- coding: utf-8 -*-

"""
Module implementing MediaManageDlg.
"""
from PyQt5.QtCore import pyqtSlot, QModelIndex, QItemSelection, QDir
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog

from comm.asynctask import coroutine, AsyncTask
from comm.utility import except_check

from data.vfile import VirFileService
from vm.virfiles import VirFileModel

from settings import vlc_audio_formats, vlc_video_formats

from .ProgressStepDlg import ProgressStepDlg
from .ui_MediaManageDlg import Ui_MediaManagDlg

_preview_max_filesz = 5 * 1024 * 1024


class MediaManageDlg(QDialog, Ui_MediaManagDlg):
    """
    Class documentation goes here.
    """

    def __init__(self, member, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(MediaManageDlg, self).__init__(parent)
        self.setupUi(self)
        self.member = member

        self._vfmodel = VirFileModel()
        self.listView.setModel(self._vfmodel)

        self._selectmodel = self.listView.selectionModel()
        self._selectmodel.currentChanged.connect(self.on_current_change)
        self._selectmodel.selectionChanged.connect(self.on_selection_change)

        self.svc = VirFileService()
        self.progressdlg = ProgressStepDlg(parent=self)
        self.svc.progressUpdated.connect(self.progressdlg.setValue)
        self.svc.progressTxtChanged.connect(self.progressdlg.setLabelText)
        self.svc.progressErrChanged.connect(self.progressdlg.addErrorText)
        self.svc.progressStepUpdated.connect(self.progressdlg.setStepValue)
        self.svc.progressStepTxtChanged.connect(self.progressdlg.setStepLabelText)

        self._refresh_vfs()

    @pyqtSlot(QModelIndex, QModelIndex)
    @except_check
    def on_current_change(self, current, previous):
        print('current: from ', previous.row() if previous.isValid() else -1, ' to ',
              current.row() if current.isValid() else -1, )
        if current.isValid():
            vf = self._vfmodel.get_model(current.row())
            self.exifText.setHtml(vf.exif)
            postfix = vf.filename.split('.')[-1]
            postfix = f'.{postfix.lower()}'
            if postfix in vlc_video_formats or postfix in vlc_audio_formats:
                self.previewButton.setEnabled(True)
            else:
                self.previewButton.setEnabled(vf.length <= _preview_max_filesz)
        else:
            self.previewButton.setEnabled(False)
            self.exifText.clear()

    @pyqtSlot(QItemSelection, QItemSelection)
    @except_check
    def on_selection_change(self, selected, deselected):
        items = selected.indexes()
        print('selection_change: ')
        for i in items:
            print(i.row())
        if items:
            self.downloadButton.setEnabled(True)
            self.deleteButton.setEnabled(True)
        else:
            self.downloadButton.setEnabled(False)
            self.deleteButton.setEnabled(False)

    @coroutine(is_block=True)
    def _refresh_vfs(self):
        self.progressdlg.open()
        try:
            vfiles = yield AsyncTask(self.svc.get_member_files, self.member)
            self._vfmodel.reset_models(vfiles)
            self.previewButton.setEnabled(False)
            self.downloadButton.setEnabled(False)
            self.deleteButton.setEnabled(False)
        finally:
            self.progressdlg.close()
            errtxt = self.progressdlg.getAllError()
            if errtxt:
                QMessageBox.critical(self, 'Error', errtxt)

    @coroutine(is_block=True)
    def _delete_vfs(self, vfiles):
        self.progressdlg.open()
        try:
            yield AsyncTask(self.svc.delete_files, vfiles)
        finally:
            self.progressdlg.close()
            errtxt = self.progressdlg.getAllError()
            if errtxt:
                QMessageBox.critical(self, 'Error', errtxt)

    @coroutine(is_block=True)
    def _upload_files(self, files):
        self.progressdlg.open()
        try:
            vfiles = yield AsyncTask(self.svc.upload_files, self.member, files)
        finally:
            self.progressdlg.close()
            errtxt = self.progressdlg.getAllError()
            if errtxt:
                QMessageBox.critical(self, 'Error', errtxt)
        for vf in vfiles:
            self._vfmodel.add_model(vf, 0)

    @coroutine(is_block=True)
    def _download_files(self, vfiles, targetdir):
        self.progressdlg.open()
        try:
            yield AsyncTask(self.svc.download_files, vfiles, targetdir)
        finally:
            self.progressdlg.close()

    def _get_selected_vfs(self):
        indexes = self._selectmodel.selectedIndexes()
        vfiles = []
        vrows = []
        for index in indexes:
            vf = self._vfmodel.get_model(index.row())
            vfiles.append(vf)
            vrows.append(index.row())
        return vfiles, vrows

    @pyqtSlot()
    @except_check
    def on_refreshButton_clicked(self):
        self._refresh()

    @pyqtSlot()
    @except_check
    def on_uploadButton_clicked(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Upload Files', QDir.homePath(), 'All Files(*.*)')
        if files:
            self._upload_files(files)

    @pyqtSlot()
    @except_check
    def on_downloadButton_clicked(self):
        targetdir, _ = QFileDialog.getExistingDirectory(self, 'Download Files', QDir.homePath(),
                                                        QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if targetdir:
            vfiles, vrows = self._get_selected_vfs()
            if vfiles:
                self._download_files(vfiles, targetdir)

    @pyqtSlot()
    @except_check
    def on_deleteButton_clicked(self):
        vfiles, vrows = self._get_selected_vfs()
        if vfiles:
            r = QMessageBox.question(self, 'Warning', f'Are you sure to delete {len(vfiles)} media files?')
            if r == QMessageBox.Yes:
                self._delete_vfs(vfiles)
                for row in vrows:
                    self._vfmodel.remove_model(row)

    @pyqtSlot()
    @except_check
    def on_previewButton_clicked(self):
        pass
