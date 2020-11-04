# -*- coding: utf-8 -*-

"""
Module implementing RestPwdDlg.
"""
import os
from pathlib import Path

from PyQt5.QtCore import pyqtSlot, QByteArray, QStandardPaths
from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.QtGui import QPixmap, QImage

from comm.utility import except_check
from settings import config, cities_dict

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
        self.sexBox.addItems(config['sex'])
        self.educationBox.addItems(config['education'])
        self.occupationBox.addItems(config['occupation'])
        self.nationBox.addItems(config['nation'])

        self.provinceBox.addItems([k for k in cities_dict])
        self.member = member

        self.nameEdit.setText(member.name)
        self.cnameEdit.setText(member.cname)
        self.sexBox.setCurrentText(member.sex)
        if member.birthday:
            self.birthdayDt.setDateTime(member.birthday)
        self.nationBox.setCurrentText(member.nation)
        self.provinceBox.setCurrentText(member.province)
        self.cityBox.setCurrentText(member.city)
        self.streetEdit.setText(member.street)
        self.homephEdit.setText(member.homephone)
        self.workphEdit.setText(member.workphone)
        self.cellphEdit.setText(member.cellphone)
        self.educationBox.setCurrentText(member.education)
        self.occupationBox.setCurrentText(member.occupation)
        self.fatherEdit.setText(member.father)
        self.motherEdit.setText(member.mother)
        self.savedEdit.setText(member.saved)
        self.ledbyEdit.setText(member.ledby)
        self.ministerEdit.setText(member.minister)
        self.baptizerEdit.setText(member.baptizer)
        if member.baptismday:
            self.baptismdayDt.setDateTime(member.baptismday)
        self.venueEdit.setText(member.venue)
        if member.avatar:
            b = QByteArray(member.avatar)
            bmp = QPixmap()
            bmp.loadFromData(b)
            self.avatarLabel.setPixmap(bmp)
        self.downloadButton.setEnabled(True if member.photo else False)

    @pyqtSlot(str)
    @except_check
    def on_provinceBox_currentTextChanged(self, province):
        self.cityBox.clear()
        if province in cities_dict:
            self.cityBox.addItems(cities_dict[province])

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
        self.member.name = self.nameEdit.text()
        self.member.cname = self.cnameEdit.text()
        self.member.sex = self.sexBox.currentText()
        self.member.birthday = self.birthdayDt.dateTime().toPyDateTime()
        self.member.nation = self.nationBox.currentText()
        self.member.province = self.provinceBox.currentText()
        self.member.city = self.cityBox.currentText()
        self.member.street = self.streetEdit.text()
        self.member.homephone = self.homephEdit.text()
        self.member.workphone = self.workphEdit.text()
        self.member.cellphone = self.cellphEdit.text()
        self.member.education = self.educationBox.currentText()
        self.member.occupation = self.occupationBox.currentText()
        self.member.father = self.fatherEdit.text()
        self.member.mother = self.motherEdit.text()
        self.member.saved = self.savedEdit.text()
        self.member.ledby = self.ledbyEdit.text()
        self.member.minister = self.ministerEdit.text()
        self.member.baptizer = self.baptizerEdit.text()
        self.member.baptismday = self.baptismdayDt.dateTime().toPyDateTime()
        self.member.venue = self.venueEdit.text()
        super(MemberDlg, self).accept()
