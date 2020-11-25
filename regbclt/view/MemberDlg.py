# -*- coding: utf-8 -*-

"""
Module implementing RestPwdDlg.
"""
import os
from pathlib import Path

from PyQt5.QtCore import pyqtSlot, QByteArray, QStandardPaths, Qt
from PyQt5.QtWidgets import QDialog, QFileDialog, QWidget, QVBoxLayout, QTableView, QAbstractItemView
from PyQt5.QtGui import QPixmap, QImage

from comm.utility import except_check
from data.model import get_write_top_fields, get_write_group_top_fields, get_write_group_list_fields, get_class_object
from vm.delegate import CustomDelegate
from vm.members import ListModel, ObjModel

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

        self.info_tabs = {}
        self.info_vls = {}
        self.info_tabviews = {}
        self.info_vm = {}
        self.list_tabs = {}
        self.list_vls = {}
        self.list_tabviews = {}
        self.list_vm = {}
        self.member = member

        topfields = get_write_top_fields()
        if topfields:
            obj = member
            name = 'Top Field'
            self.init_infovm(name, topfields, obj)
        grouptop = get_write_group_top_fields()
        for k in grouptop:
            field, cls = k
            fields = grouptop[k]
            obj = getattr(member, field)
            self.init_infovm(cls, fields, obj)
        grouplist = get_write_group_list_fields()
        for k in grouplist:
            field, cls = k
            fields = grouplist[k]
            objs = getattr(member, field)
            self.init_listvm(cls, fields, objs)

        if member.avatar:
            b = QByteArray(member.avatar)
            bmp = QPixmap()
            bmp.loadFromData(b)
            self.avatarLabel.setPixmap(bmp)
        self.downloadButton.setEnabled(True if member.photo else False)

    def init_infovm(self, name, fields, obj):
        vm = ObjModel(obj, fields, parent=self)
        view = self.add_info_tab(name)
        view.setItemDelegate(CustomDelegate(self))
        view.setModel(vm)
        vm.initView(view)
        self.info_vm[name] = vm

    def init_listvm(self, name, fields, objs):
        vm = ListModel(objs, fields, parent=self)
        view = self.add_list_tab(name)
        view.setItemDelegate(CustomDelegate(self))
        view.setModel(vm)
        vm.initView(view)
        self.list_vm[name] = vm

    def add_info_tab(self, name):
        index = len(self.info_tabs)
        tab = QWidget()
        tab.setObjectName(f"info_tab{index}")
        verticalLayout = QVBoxLayout(tab)
        verticalLayout.setObjectName(f"info_verticalLayout{index}")
        tableView = QTableView(tab)
        tableView.setEditTriggers(QAbstractItemView.AllEditTriggers)
        tableView.setObjectName(f"info_tableView{index}")
        verticalLayout.addWidget(tableView)
        self.infoTab.addTab(tab, name)
        self.info_tabs[name] = tab
        self.info_vls[name] = verticalLayout
        self.info_tabviews[name] = tableView
        return tableView

    def add_list_tab(self, name):
        index = len(self.list_tabs)
        tab = QWidget()
        tab.setObjectName(f"list_tab{index}")
        verticalLayout = QVBoxLayout(tab)
        verticalLayout.setObjectName(f"list_verticalLayout{index}")
        tableView = QTableView(tab)
        tableView.setEditTriggers(QAbstractItemView.AllEditTriggers)
        tableView.setObjectName(f"list_tableView{index}")
        verticalLayout.addWidget(tableView)
        self.listTab.addTab(tab, name)
        self.list_tabs[name] = tab
        self.list_vls[name] = verticalLayout
        self.list_tabviews[name] = tableView
        return tableView

    @pyqtSlot()
    @except_check
    def on_addButton_clicked(self):
        name = self.listTab.tabText(self.listTab.currentIndex())
        clsdef = get_class_object(name)
        obj = clsdef()
        vm = self.list_vm[name]
        view = self.list_tabviews[name]
        row = vm.count_model()
        vm.add_model(obj, row)
        index = vm.index(row, 0)
        view.setCurrentIndex(index)
        view.edit(index)

    @pyqtSlot()
    @except_check
    def on_delButton_clicked(self):
        name = self.listTab.tabText(self.listTab.currentIndex())
        view = self.list_tabviews[name]
        index = view.currentIndex()
        if index.isValid():
            row = index.row()
            vm = self.list_vm[name]
            vm.remove_model(row)

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

    def keyPressEvent(self, evt):
        key = evt.key()
        if key == Qt.Key_Enter or key == Qt.Key_Return or key == Qt.Key_Escape:
            return
        super(MemberDlg, self).keyPressEvent(evt)
