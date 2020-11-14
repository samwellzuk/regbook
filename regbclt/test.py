# -*-coding: utf-8 -*-
# Created by samwell
import sys
import time
import os
import pathlib

from PyQt5.QtCore import pyqtSlot, QRect, QCoreApplication, Qt, QObject, pyqtSignal, QRectF
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, \
    QFileDialog, QLabel
from PyQt5.QtGui import QPixmap, QPen, QBrush, QPainter, QImage, QTransform

from comm.asynctask import coroutine, AsyncTask
from comm.utility import except_check

from data.dbmgr import DBManager

from view.ProgressDlg import ProgressDlg
from view.PhotoWidget import PhotoWidget

from comm.exiftool import extract_exif
from comm.iconextract import extract
from settings import tmp_dir


class UserService(QObject):
    progressUpdated = pyqtSignal(int)

    def get_all_user(self):
        for i in range(10):
            self.progressUpdated.emit(i * 10)
            time.sleep(1)
        self.progressUpdated.emit(100)
        return []


class Ui_LoginDlg(object):
    def setupUi(self, LoginDlg):
        LoginDlg.setObjectName("LoginDlg")
        LoginDlg.setWindowModality(Qt.ApplicationModal)
        LoginDlg.resize(358, 118)
        LoginDlg.setSizeGripEnabled(False)
        LoginDlg.setModal(True)
        self.pushButton = QPushButton(LoginDlg)
        self.pushButton.setGeometry(QRect(30, 50, 93, 28))
        self.pushButton.setObjectName("pushButton")
        self.cancelButton = QPushButton(LoginDlg)
        self.cancelButton.setGeometry(QRect(228, 48, 93, 28))
        self.cancelButton.setObjectName("cancelButton")

        self.retranslateUi(LoginDlg)
        self.cancelButton.clicked.connect(LoginDlg.reject)
        self.pushButton.clicked.connect(LoginDlg.on_test)

    def retranslateUi(self, LoginDlg):
        _translate = QCoreApplication.translate
        LoginDlg.setWindowTitle(_translate("LoginDlg", "Login"))
        self.pushButton.setText(_translate("LoginDlg", "Test"))
        self.cancelButton.setText(_translate("LoginDlg", "Quit"))


class TestDlg(QDialog, Ui_LoginDlg):
    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(QDialog, self).__init__(parent)
        self.setupUi(self)

        self.progressdlg = ProgressDlg(parent=self)
        self.svc = UserService()
        self.svc.progressUpdated.connect(self._update_progress)

    @pyqtSlot(int)
    @except_check
    def _update_progress(self, progress):
        print("update: ", progress)
        if self.progressdlg.is_open():
            self.progressdlg.setValue(progress)

    @pyqtSlot()
    @except_check
    def on_test(self):
        self.test2()

    @coroutine(is_block=True)
    def test(self):
        self.progressdlg.setLabelText(f'Query user information ...')
        self.progressdlg.open()
        try:
            yield AsyncTask(self.svc.get_all_user)
        finally:
            self.progressdlg.close()
            print('is open:', self.progressdlg.is_open())

    def test1(self):
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, parent=self)
        item = QGraphicsPixmapItem(QPixmap(":/images/thumbnail.png"))
        self.scene.addItem(item)
        self.view.show()

    def test2(self):
        scene = QGraphicsScene()
        scene.addRect(QRectF(0, 0, 100, 200), QPen(Qt.black), QBrush(Qt.green))

        pixmap = QPixmap()

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        scene.render(painter)
        painter.end()

        pixmap.save("scene.png", "PNG")


from view.MainWnd import MainWindow


def main1():
    app = QApplication(sys.argv)
    fileName, _ = QFileDialog.getOpenFileName(None, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
    srcimg = QImage(fileName)
    center = srcimg.rect().center()
    tf = QTransform()
    tf.translate(center.x(), center.y())
    tf.rotate(90)
    dstImg = srcimg.transformed(tf)
    dstImg.save('d:\\1.jpg', "JPG")

    # wnd = PhotoWidget(img)
    # wnd.show()
    # return app.exec()


def test():
    filelist = []
    r = os.path.join(os.getcwd(), 'exiftool')
    r = r'C:\Users\atten\Desktop\手机照片'
    for root, dirs, files in os.walk(r):
        for f in files:
            filelist.append(os.path.join(root, f))
    tmppath = pathlib.Path(tmp_dir)
    for f in filelist:
        print('-------------------------')
        print('Getting ', f)
        try:
            sreport, img = extract_exif(f)
            fp = pathlib.Path(f)
            newpath = tmppath.joinpath(fp.name)
            newpath.mkdir()

            ftxt = newpath.joinpath('default.htm')
            fimg = newpath.joinpath('default.jpg')
            with ftxt.open('w', encoding='utf8') as of:
                of.write(sreport)
                print('Ok ', ftxt)
            if img:
                with fimg.open('wb') as of:
                    of.write(img)
                    print('Ok image ', fimg)
        except Exception as e:
            print('Failed : ', e)


def main():
    app = QApplication(sys.argv)
    # dlg = TestDlg()
    # dlg.exec()
    data = extract('C:\Windows\SystemResources\imageres.dll.mun', 2, 128)
    with open('imageres.ico', 'wb') as of:
        of.write(data)
    fileName, _ = QFileDialog.getOpenFileName(None, "Open Image", "", "Image Files (*.png *.jpg *.bmp *.ico)")
    pixmap = QPixmap(fileName)
    label = QLabel()
    label.setPixmap(pixmap)
    label.show()
    return app.exec()

def exico():
    import settings
    from comm import fileicon
    # check file
    settings.initialize()
    fileicon.initialize()
    try:
        data = fileicon.query_file_icon('.xls')
        with open('test.ico','wb') as of:
            of.write(data)
    finally:
        fileicon.uninialize()

def exmv():
    import sys
    import pythoncom
    from comm.vlctool import VlcExtractor
    ex = VlcExtractor()
    img = ex.take_snapshot(r'E:\mv\[66影视www.66ys.cn]哈利波特2之消失的密室DVD国语配音高清收藏版.rmvb')
    if img:
        print('ok')
        with open('test.png','wb') as of:
            of.write(img)
    else:
        print('failed')


if __name__ == '__main__':
    exmv()
