# -*-coding: utf-8 -*-
# Created by samwell
import sys
import time

from PyQt5.QtCore import pyqtSlot, QRect, QCoreApplication, Qt, QObject, pyqtSignal, QRectF
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, \
    QFileDialog
from PyQt5.QtGui import QPixmap, QPen, QBrush, QPainter, QImage, QTransform

from comm.asynctask import coroutine, AsyncTask
from comm.utility import except_check

from data.dbmgr import DBManager

from view.ProgressDlg import ProgressDlg
from view.PhotoWidget import PhotoWidget


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


def main():
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


if __name__ == '__main__':
    from comm.filetype import _test
    _test()
    #main()
