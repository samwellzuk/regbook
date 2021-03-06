# -*- coding: utf-8 -*-

"""
Module implementing MediaManageDlg.
"""
import os
from enum import Enum
from PyQt5.QtCore import pyqtSlot, QModelIndex, QItemSelection, QDir, QIODevice, QByteArray, QBuffer
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap, QTransform
import win32api

from comm.asynctask import coroutine, AsyncTask
from comm.utility import except_check

from data.vfile import VirFileService
from vm.virfiles import VirFileModel

from settings import vlc_audio_formats, vlc_video_formats, preview_max_filesz, temp_dir

from .MediaPlayDlg import MediaPlayDlg
from .ProgressStepDlg import ProgressStepDlg
from .ui_MediaManageDlg import Ui_MediaManagDlg


class PreviewType(Enum):
    NoPreview = 0
    VlcPreview = 1
    OpenPreview = 2


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

        self._preview_dlglist = []

        self._vfmodel = VirFileModel()
        self.listView.setModel(self._vfmodel)

        self._selectmodel = self.listView.selectionModel()
        self._selectmodel.currentChanged.connect(self.on_current_change)
        self._selectmodel.selectionChanged.connect(self.on_selection_change)

        self.svc = VirFileService(parent=self)
        self.progressdlg = ProgressStepDlg(parent=self)
        self.svc.progressUpdated.connect(self.progressdlg.setValue)
        self.svc.progressTxtChanged.connect(self.progressdlg.setLabelText)
        self.svc.progressErrChanged.connect(self.progressdlg.addErrorText)
        self.svc.progressStepUpdated.connect(self.progressdlg.setStepValue)
        self.svc.progressStepTxtChanged.connect(self.progressdlg.setStepLabelText)
        self._refresh_vfs()

    def _get_preview_type(self, vf):
        suffix = vf.file_suffix()
        if suffix in vlc_video_formats or suffix in vlc_audio_formats:
            return PreviewType.VlcPreview
        elif vf.length <= preview_max_filesz:
            return PreviewType.OpenPreview
        return PreviewType.NoPreview

    def _check_state(self):
        items = self._selectmodel.selectedIndexes()
        if len(items) == 0:
            self.downloadButton.setEnabled(False)
            self.deleteButton.setEnabled(False)
            self.previewButton.setEnabled(False)
            self.exifText.clear()
            self.rorateLeft.setEnabled(False)
            self.rorateRight.setEnabled(False)
        elif len(items) == 1:
            self.downloadButton.setEnabled(True)
            self.deleteButton.setEnabled(True)
            vf = self._vfmodel.get_model(items[0].row())
            self.previewButton.setEnabled(True)
            self.exifText.setHtml(vf.exif)
            if vf.thumbnail:
                self.rorateLeft.setEnabled(True)
                self.rorateRight.setEnabled(True)
            else:
                self.rorateLeft.setEnabled(False)
                self.rorateRight.setEnabled(False)
        else:
            self.downloadButton.setEnabled(True)
            self.deleteButton.setEnabled(True)
            self.previewButton.setEnabled(False)
            self.exifText.clear()
            self.rorateLeft.setEnabled(False)
            self.rorateRight.setEnabled(False)

    @pyqtSlot(QModelIndex, QModelIndex)
    @except_check
    def on_current_change(self, current, previous):
        self._check_state()

    @pyqtSlot(QItemSelection, QItemSelection)
    @except_check
    def on_selection_change(self, selected, deselected):
        self._check_state()

    @coroutine(is_block=True)
    def _refresh_vfs(self):
        self.progressdlg.open()
        try:
            vfiles = yield AsyncTask(self.svc.get_member_files, self.member)
            self._vfmodel.reset_models(vfiles)
            self._selectmodel.clear()
            self._check_state()
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

    @coroutine(is_block=True)
    def _uppdate_thumbnail(self, index, vfile, thumbnail):
        self.progressdlg.open()
        try:
            newvf = yield AsyncTask(self.svc.update_file_thumbnail, vfile, thumbnail)
        finally:
            self.progressdlg.close()
        self._vfmodel.update_model(index, newvf)

    def _get_selected_vfs(self):
        indexes = self._selectmodel.selectedIndexes()
        vfiles = []
        vrows = []
        for index in indexes:
            vf = self._vfmodel.get_model(index.row())
            vfiles.append(vf)
            vrows.append(index.row())
        return vfiles, vrows

    def _rotate(self, img, turnright=True):
        pixmap = QPixmap()
        pixmap.loadFromData(img)
        tf = QTransform()
        tf.translate(pixmap.width() / 2.0, pixmap.height() / 2.0)
        if turnright:
            tf.rotate(90)
        else:
            tf.rotate(-90)
        tf.translate(-pixmap.height() / 2.0, -pixmap.width() / 2.0)
        dstimg = pixmap.transformed(tf)
        resarr = QByteArray()
        resbuf = QBuffer(resarr)
        resbuf.open(QIODevice.WriteOnly)
        dstimg.save(resbuf, "PNG")  # thumbnail save to png for keeping transparent color
        return resarr.data()

    def _on_rorate(self, turnright):
        vfiles, vrows = self._get_selected_vfs()
        index = vrows[0]
        vf = vfiles[0]
        thunbnail = self._rotate(vf.thumbnail, turnright=turnright)
        self._uppdate_thumbnail(index, vf, thunbnail)

    @pyqtSlot()
    @except_check
    def on_refreshButton_clicked(self):
        self._refresh_vfs()

    @pyqtSlot()
    @except_check
    def on_uploadButton_clicked(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Upload Files', QDir.homePath(), 'All Files(*.*)')
        if files:
            self._upload_files(files)

    @pyqtSlot()
    @except_check
    def on_downloadButton_clicked(self):
        targetdir = QFileDialog.getExistingDirectory(self, 'Download Files', QDir.homePath(),
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
                for row in sorted(vrows, reverse=True):
                    self._vfmodel.remove_model(row)

    @pyqtSlot()
    @except_check
    def on_rorateLeft_clicked(self):
        self._on_rorate(False)

    @pyqtSlot()
    @except_check
    def on_rorateRight_clicked(self):
        self._on_rorate(True)

    def _do_preview(self, vf):
        pty = self._get_preview_type(vf)
        if pty == PreviewType.VlcPreview:
            dlg = MediaPlayDlg(vf, parent=self)
            dlg.show()
            self._preview_dlglist.append(dlg)
        elif pty == PreviewType.OpenPreview:
            dpath = os.path.join(temp_dir, str(vf._id))
            os.makedirs(dpath, exist_ok=True)
            fpath = os.path.join(dpath, vf.filename)
            if not os.path.isfile(fpath):
                self._download_files([vf], dpath)
            win32api.ShellExecute(self.winId(), 'open', fpath, None, dpath, 5)
        else:
            QMessageBox.information(self, 'Preview',
                                    "Can't preview file which size more than 5M,\nPlease just download it.")

    def done(self, a0: int) -> None:
        super(MediaManageDlg, self).done(a0)
        for dlg in self._preview_dlglist:
            if not dlg.isHidden():
                dlg.close()
        self._preview_dlglist.clear()

    @pyqtSlot()
    @except_check
    def on_previewButton_clicked(self):
        vfiles, vrows = self._get_selected_vfs()
        self._do_preview(vfiles[0])

    @pyqtSlot(QModelIndex)
    @except_check
    def on_listView_doubleClicked(self, clickindex):
        vfiles, vrows = self._get_selected_vfs()
        if len(vfiles) == 1:
            self._do_preview(vfiles[0])
