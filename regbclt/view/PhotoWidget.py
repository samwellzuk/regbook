# -*-coding: utf-8 -*-
# Created by samwell
from typing import Tuple

from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal, QRectF, QPointF, QRect, QIODevice, QByteArray, QBuffer
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap, QPen, QPainter, QColor, QImage, QTransform, QRegion, \
    QMouseEvent, QPaintEvent, QWheelEvent
from comm.utility import except_check

_head_margin = 0.05
_head_width_max = 128
_head_highet_max = 128
_avatar_ratio = 1.4
_avatar_margin = 0.05
_avatar_width_max = 750
_avatar_highet_max = 1050


class PhotoWidget(QWidget):
    ratioChanged = pyqtSignal(int)

    def __init__(self, img: QImage, parent: QWidget = None):
        super(PhotoWidget, self).__init__(parent=parent)
        self.lastpt = None
        self._init_img(img)

    def save_image(self) -> Tuple[QImage, QImage]:
        passrectpix = self._get_imgrect(self.ratio, self.offsetpt)
        xratio = (self.orgwinport.x() - passrectpix.x()) / passrectpix.width()
        yratio = (self.orgwinport.y() - passrectpix.y()) / passrectpix.height()
        wratio = self.orgwinport.width() / passrectpix.width()
        hratio = self.orgwinport.height() / passrectpix.height()
        wimg = self.orgimg.width()
        himg = self.orgimg.height()

        rectsel = QRectF(wimg * xratio, himg * yratio, wimg * wratio, himg * hratio)
        recthead = self._get_headport(rectsel)
        imgavatar = self.orgimg.copy(rectsel.toRect())
        imghead = self.orgimg.copy(recthead.toRect())
        # avatar 图片超过范围,需要压缩
        wimg = imgavatar.width()
        himg = imgavatar.height()
        if wimg > _avatar_width_max or himg > _avatar_highet_max:
            r = himg / wimg
            if r > 1.4:
                imgavatar = imgavatar.scaledToHeight(_avatar_highet_max, Qt.SmoothTransformation)
            else:
                imgavatar = imgavatar.scaledToWidth(_avatar_width_max, Qt.SmoothTransformation)
        # head
        dstimg = QImage(_head_width_max, _head_highet_max, QImage.Format_ARGB4444_Premultiplied)
        dstimg.fill(Qt.transparent)
        painter = QPainter()
        if painter.begin(dstimg):
            dstrect = QRect(0, 0, _head_width_max, _head_highet_max)
            srcrect = QRect(0, 0, imghead.width(), imghead.height())
            region = QRegion(dstrect, QRegion.Ellipse)
            painter.setClipRegion(region)
            painter.drawImage(dstrect, imghead, srcrect)
            painter.end()
            imghead = dstimg

        avatar_arr = QByteArray()
        avatar_buf = QBuffer(avatar_arr)
        avatar_buf.open(QIODevice.WriteOnly)
        imgavatar.save(avatar_buf, "JPG")
        head_arr = QByteArray()
        head_buf = QBuffer(head_arr)
        head_buf.open(QIODevice.WriteOnly)
        imghead.save(head_buf, "PNG")
        return avatar_arr.data(), head_arr.data()

    def _init_img(self, img):
        self.orgimg = img
        self.orgpix = QPixmap.fromImage(img)
        self.orgwinport = self._get_winport()
        self.ratio = 1.0
        self.offsetpt = QPointF(0, 0)

    def _get_headport(self, vp: QRectF) -> QRectF:
        dx = vp.width() * _head_margin
        dy = vp.height() * _head_margin
        recthd = QRectF(vp.x(), vp.y(), vp.width(), vp.width())
        recthd.adjust(dx, dy, -dx, -dy)
        return recthd

    def _get_viewport(self) -> QRectF:
        winw = self.width() * 1.0
        winh = self.height() * 1.0
        ratio = winh / winw
        if ratio > _avatar_ratio:
            tmpw = winw * (1 - _avatar_margin * 2)
            rectw = tmpw
            recth = tmpw * _avatar_ratio
        else:
            tmph = winh * (1 - _avatar_margin * 2)
            rectw = tmph / _avatar_ratio
            recth = tmph
        rectvp = QRectF((winw - rectw) / 2, (winh - recth) / 2, rectw, recth)
        return rectvp

    def _get_winport(self) -> QRectF:
        imgw = self.orgpix.width() * 1.0
        imgh = self.orgpix.height() * 1.0
        ratio = imgh / imgw
        if ratio > _avatar_ratio:
            rectw = imgw
            recth = imgw * _avatar_ratio
        else:
            rectw = imgh / _avatar_ratio
            recth = imgh
        rectwinp = QRectF(-(rectw / 2), -(recth / 2), rectw, recth)
        return rectwinp

    def _get_imgrect(self, ratio: float, offsetpt: QPointF = None) -> QRectF:
        imgw = self.orgpix.width() * ratio
        imgh = self.orgpix.height() * ratio
        rectimg = QRectF(0, 0, imgw, imgh)
        rectimg.moveCenter(QPointF(0.0, 0.0))
        if offsetpt:
            rectimg.translate(offsetpt)
        return rectimg

    @except_check
    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)

        rectvp = self._get_viewport()
        recthd = self._get_headport(rectvp)
        rectpix = self._get_imgrect(self.ratio, self.offsetpt)

        painter.save()
        painter.setViewport(rectvp.toRect())
        painter.setWindow(self.orgwinport.toRect())
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(rectpix, self.orgpix, QRectF(0, 0, self.orgpix.width(), self.orgpix.height()))
        painter.restore()

        pen = QPen()
        pen.setColor(QColor(255, 0, 0))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawRect(rectvp)
        painter.drawEllipse(recthd)

    def _move_img(self, curpt):
        orgoff = curpt - self.lastpt
        offset = QPointF(orgoff.x() * self.ratio, orgoff.y() * self.ratio)
        newoffset = self.offsetpt + offset
        rectimg = self._get_imgrect(self.ratio, newoffset)
        if rectimg.contains(self.orgwinport):
            self.offsetpt = newoffset
            self.update()

    def _rotate(self, turnright=True):
        tf = QTransform()
        tf.translate(self.orgimg.width() / 2.0, self.orgimg.height() / 2.0)
        if turnright:
            tf.rotate(90)
        else:
            tf.rotate(-90)
        tf.translate(-self.orgimg.height() / 2.0, -self.orgimg.width() / 2.0)
        dstimg = self.orgimg.transformed(tf)
        self._init_img(dstimg)
        self.update()

    @pyqtSlot()
    @except_check
    def rotate_left(self):
        self._rotate(False)

    @pyqtSlot()
    @except_check
    def rotate_right(self):
        self._rotate()

    @pyqtSlot(int)
    @except_check
    def zoom(self, val: int):
        if val > 50 or val < 10:
            return
        newratio = val / 10.0
        rectimg = self._get_imgrect(newratio, self.offsetpt)
        if rectimg.contains(self.orgwinport):
            self.ratio = newratio
            self.update()
            self.ratioChanged.emit(val)

    @except_check
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.LeftButton:
            self.lastpt = event.pos()

    @except_check
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.LeftButton:
            if self.lastpt:
                curpt = event.pos()
                self._move_img(curpt)
                self.lastpt = curpt

    @except_check
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.LeftButton:
            if self.lastpt:
                curpt = event.pos()
                self._move_img(curpt)
                self.lastpt = None

    @except_check
    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.angleDelta().y() > 0:
            self.zoom(int(self.ratio * 10) + 1)
        else:
            self.zoom(int(self.ratio * 10) - 1)
