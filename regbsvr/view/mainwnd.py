# -*-coding: utf-8 -*-
# Created by samwell

import socket

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QMessageBox

from svc import SvcStatus
from .ui_mainwnd import Ui_MainWindow
from .utility import except_check


class Ui_MainWindow_Ex(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)


ip_fmt = '<span style="font-size:32pt;font-weight:bold;color:black;">IP&nbsp;&nbsp;:</span><span style="font-size:32pt;font-weight:bold;color:green;">{}</span>'
status_fmt = '<span style="font-size:32pt;font-weight:bold;color:black;">STATUS:</span><span style="font-size:32pt;font-weight:bold;color:{};">{}</span>'


class MainWindow(QDialog):
    def __init__(self, svc):
        QDialog.__init__(self)
        self.svc = svc

        self.ui = Ui_MainWindow_Ex()
        self.ui.setupUi(self)

        self.ui.btn_refresh.clicked.connect(self._btn_refresh)
        self.ui.btn_start.clicked.connect(self._btn_start)
        self.ui.btn_stop.clicked.connect(self._btn_stop)
        self.ui.btn_install.clicked.connect(self._btn_install)
        self.ui.btn_uninstall.clicked.connect(self._btn_uninstall)

    def _refresh(self):
        # set ip
        _, _, iplist = socket.gethostbyname_ex(socket.gethostname())
        sip = ip_fmt.format(', '.join(iplist))
        self.ui.label_ip.setText(sip)
        # set status
        status = self.svc.query()
        if status == SvcStatus.NO_EXIST:
            stxt = status_fmt.format('grey', 'Not Exist')
        elif status == SvcStatus.RUNNING:
            stxt = status_fmt.format('green', 'Running')
        elif status == SvcStatus.STOPPED:
            stxt = status_fmt.format('red', 'Stopped')
        else:  # SvcStatus.PAUSED
            stxt = status_fmt.format('red', 'Paused')
        self.ui.label_status.setText(stxt)
        # set button
        if status == SvcStatus.NO_EXIST:
            self.ui.btn_refresh.setEnabled(True)
            self.ui.btn_start.setEnabled(False)
            self.ui.btn_stop.setEnabled(False)
            self.ui.btn_install.setEnabled(True)
            self.ui.btn_uninstall.setEnabled(False)
        elif status == SvcStatus.RUNNING:
            self.ui.btn_refresh.setEnabled(True)
            self.ui.btn_start.setEnabled(False)
            self.ui.btn_stop.setEnabled(True)
            self.ui.btn_install.setEnabled(False)
            self.ui.btn_uninstall.setEnabled(True)
        elif status == SvcStatus.STOPPED:
            self.ui.btn_refresh.setEnabled(True)
            self.ui.btn_start.setEnabled(True)
            self.ui.btn_stop.setEnabled(False)
            self.ui.btn_install.setEnabled(False)
            self.ui.btn_uninstall.setEnabled(True)
        else:  # SvcStatus.PAUSED
            self.ui.btn_refresh.setEnabled(True)
            self.ui.btn_start.setEnabled(True)
            self.ui.btn_stop.setEnabled(False)
            self.ui.btn_install.setEnabled(False)
            self.ui.btn_uninstall.setEnabled(True)

    @pyqtSlot(bool)
    @except_check
    def _btn_refresh(self, checked):
        self._refresh()

    @pyqtSlot(bool)
    @except_check
    def _btn_start(self, checked):
        self.svc.start()
        self._refresh()

    @pyqtSlot(bool)
    @except_check
    def _btn_stop(self, checked):
        self.svc.stop()
        self._refresh()

    @pyqtSlot(bool)
    @except_check
    def _btn_install(self, checked):
        self.svc.install()
        self._refresh()

    @pyqtSlot(bool)
    @except_check
    def _btn_uninstall(self, checked):
        if QMessageBox.question(self, 'Warning', 'Are you sure to remove service?') == QMessageBox.Yes:
            self.svc.remove()
            self._refresh()

    def showEvent(self, event):
        """
        rewrite closeEvent, so when mainwindows closing, can clear up
        :param event:
        :return: None
        """
        self._btn_refresh(False)

    def closeEvent(self, event):
        """
        rewrite closeEvent, so when mainwindows closing, can clear up
        :param event:
        :return: None
        """
        pass
