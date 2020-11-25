# -*- coding: utf-8 -*-

"""
Module implementing RestPwdDlg.
"""
import os
from pathlib import Path

from PyQt5.QtCore import pyqtSlot, QByteArray, QStandardPaths
from PyQt5.QtWidgets import QDialog, QFileDialog, QWidget, QVBoxLayout, QTableView, QAbstractItemView
from PyQt5.QtGui import QPixmap, QImage

from comm.utility import except_check
from data.model import get_write_top_fields, get_write_group_top_fields, get_write_group_list_fields

from .ui_MemberDlg import Ui_MemberDlg
from .PhotoEditorDlg import PhotoEditorDlg


class MemberDlg(QDialog, Ui_MemberDlg):
    """
    Class documentation goes here.
    """

    def __init__(self, member, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MemberDlg, self).__init__(parent)
        self.setupUi(self)

        self.infotabs = {}
        self.infovls = {}
        self.infotabviews = {}
        self.listtabs = {}
        self.listvls = {}
        self.listtabviews = {}

        self.member = member

        topfields = get_write_top_fields()
        grouptop = get_write_group_top_fields()
        grouplist = get_write_group_list_fields()

    def add_info_tab(self, name):
        index = len(self.infotabs)
        tab = QWidget()
        tab.setObjectName(f"info_tab{index}")
        verticalLayout = QVBoxLayout(tab)
        verticalLayout.setObjectName(f"info_verticalLayout{index}")
        tableView = QTableView(tab)
        tableView.setEditTriggers(QAbstractItemView.AllEditTriggers)
        tableView.setObjectName(f"info_tableView{index}")
        verticalLayout.addWidget(tableView)
        self.infoTab.addTab(tab, name)
        self.infotabs[name] = tab
        self.infovls[name] = verticalLayout
        self.infotabviews[name] = tableView
        return tableView

    def add_list_tab(self, name):
        index = len(self.listtabs)
        tab = QWidget()
        tab.setObjectName(f"list_tab{index}")
        verticalLayout = QVBoxLayout(tab)
        verticalLayout.setObjectName(f"list_verticalLayout{index}")
        tableView = QTableView(tab)
        tableView.setEditTriggers(QAbstractItemView.AllEditTriggers)
        tableView.setObjectName(f"list_tableView{index}")
        verticalLayout.addWidget(tableView)
        self.listTab.addTab(tab, name)
        self.listtabs[name] = tab
        self.listvls[name] = verticalLayout
        self.listtabviews[name] = tableView
        return tableView

    @pyqtSlot()
    @except_check
    def on_addButton_clicked(self):
        pass

    @pyqtSlot()
    @except_check
    def on_delButton_clicked(self):
        pass

    @pyqtSlot()
    @except_check
    def on_downloadButton_clicked(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            QStandardPaths.writableLocation(QStandardPaths.PicturesLocation),
            f"Image Files(*{self.member.photofmt})"
        )
        fp = Path(filename).with_suffix(self.member.photofmt)
        with open(str(fp), 'wb') as of:
            of.write(self.member.photo)

    @pyqtSlot()
    @except_check
    def on_uploadButton_clicked(self):
        dirs = QStandardPaths.standardLocations(QStandardPaths.PicturesLocation)
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            dirs[0] if dirs else '.',
            "Image Files(*.bmp *.gif *.jpg *.jpeg *.png *.pbm *.pgm *.ppm *.xbm *.xpm)"
        )
        fp = Path(filename)
        if fp.is_file():
            photofmt = fp.suffix.lower()
            with open(filename, 'rb') as bf:
                photobin = bf.read()
            img = QImage(filename)
            dlg = PhotoEditorDlg(img, parent=self)
            if dlg.exec() == PhotoEditorDlg.Accepted:
                self.member.photo = photobin
                self.member.photofmt = photofmt
                self.member.avatar = dlg.avatar
                self.member.thumbnail = dlg.thumbnail
                b = QByteArray(dlg.avatar)
                bmp = QPixmap()
                bmp.loadFromData(b)
                self.avatarLabel.setPixmap(bmp)
                self.downloadButton.setEnabled(True)

    @pyqtSlot()
    @except_check
    def accept(self):
        super(MemberDlg, self).accept()
