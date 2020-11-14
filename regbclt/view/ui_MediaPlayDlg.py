# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\MediaPlayDlg.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MediaPlayDlg(object):
    def setupUi(self, MediaPlayDlg):
        MediaPlayDlg.setObjectName("MediaPlayDlg")
        MediaPlayDlg.resize(622, 569)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/vlc.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MediaPlayDlg.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(MediaPlayDlg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.videoWidget = QtWidgets.QWidget(MediaPlayDlg)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.videoWidget.sizePolicy().hasHeightForWidth())
        self.videoWidget.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.videoWidget.setPalette(palette)
        self.videoWidget.setAutoFillBackground(True)
        self.videoWidget.setObjectName("videoWidget")
        self.verticalLayout.addWidget(self.videoWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.curtimeLabel = QtWidgets.QLabel(MediaPlayDlg)
        self.curtimeLabel.setObjectName("curtimeLabel")
        self.horizontalLayout.addWidget(self.curtimeLabel)
        self.positionSlider = QtWidgets.QSlider(MediaPlayDlg)
        self.positionSlider.setMinimum(1)
        self.positionSlider.setMaximum(1000)
        self.positionSlider.setTracking(False)
        self.positionSlider.setOrientation(QtCore.Qt.Horizontal)
        self.positionSlider.setObjectName("positionSlider")
        self.horizontalLayout.addWidget(self.positionSlider)
        self.totaltimeLabel = QtWidgets.QLabel(MediaPlayDlg)
        self.totaltimeLabel.setObjectName("totaltimeLabel")
        self.horizontalLayout.addWidget(self.totaltimeLabel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.exitButton = QtWidgets.QPushButton(MediaPlayDlg)
        self.exitButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/power.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.exitButton.setIcon(icon1)
        self.exitButton.setIconSize(QtCore.QSize(48, 48))
        self.exitButton.setFlat(False)
        self.exitButton.setObjectName("exitButton")
        self.horizontalLayout_2.addWidget(self.exitButton)
        self.playButton = QtWidgets.QPushButton(MediaPlayDlg)
        self.playButton.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/images/play.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.playButton.setIcon(icon2)
        self.playButton.setIconSize(QtCore.QSize(48, 48))
        self.playButton.setObjectName("playButton")
        self.horizontalLayout_2.addWidget(self.playButton)
        self.pauseButton = QtWidgets.QPushButton(MediaPlayDlg)
        self.pauseButton.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/images/pause.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pauseButton.setIcon(icon3)
        self.pauseButton.setIconSize(QtCore.QSize(48, 48))
        self.pauseButton.setObjectName("pauseButton")
        self.horizontalLayout_2.addWidget(self.pauseButton)
        self.stopButton = QtWidgets.QPushButton(MediaPlayDlg)
        self.stopButton.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/images/stop.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stopButton.setIcon(icon4)
        self.stopButton.setIconSize(QtCore.QSize(48, 48))
        self.stopButton.setObjectName("stopButton")
        self.horizontalLayout_2.addWidget(self.stopButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.voiceButton = QtWidgets.QPushButton(MediaPlayDlg)
        self.voiceButton.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/images/sound.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon5.addPixmap(QtGui.QPixmap(":/images/mute.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.voiceButton.setIcon(icon5)
        self.voiceButton.setIconSize(QtCore.QSize(48, 48))
        self.voiceButton.setCheckable(True)
        self.voiceButton.setFlat(True)
        self.voiceButton.setObjectName("voiceButton")
        self.horizontalLayout_2.addWidget(self.voiceButton)
        self.volumeSlider = QtWidgets.QSlider(MediaPlayDlg)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.volumeSlider.sizePolicy().hasHeightForWidth())
        self.volumeSlider.setSizePolicy(sizePolicy)
        self.volumeSlider.setMinimumSize(QtCore.QSize(100, 0))
        self.volumeSlider.setMinimum(1)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setProperty("value", 50)
        self.volumeSlider.setTracking(False)
        self.volumeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.volumeSlider.setObjectName("volumeSlider")
        self.horizontalLayout_2.addWidget(self.volumeSlider)
        self.volumeLabel = QtWidgets.QLabel(MediaPlayDlg)
        self.volumeLabel.setMinimumSize(QtCore.QSize(50, 0))
        self.volumeLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.volumeLabel.setObjectName("volumeLabel")
        self.horizontalLayout_2.addWidget(self.volumeLabel)
        self.label = QtWidgets.QLabel(MediaPlayDlg)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(MediaPlayDlg)
        self.exitButton.clicked.connect(MediaPlayDlg.accept)
        QtCore.QMetaObject.connectSlotsByName(MediaPlayDlg)

    def retranslateUi(self, MediaPlayDlg):
        _translate = QtCore.QCoreApplication.translate
        MediaPlayDlg.setWindowTitle(_translate("MediaPlayDlg", "Vlc Media Player"))
        self.curtimeLabel.setToolTip(_translate("MediaPlayDlg", "Current Time"))
        self.curtimeLabel.setText(_translate("MediaPlayDlg", "TextLabel"))
        self.totaltimeLabel.setToolTip(_translate("MediaPlayDlg", "Remain/Total Time"))
        self.totaltimeLabel.setText(_translate("MediaPlayDlg", "TextLabel"))
        self.exitButton.setToolTip(_translate("MediaPlayDlg", "Power Off"))
        self.playButton.setToolTip(_translate("MediaPlayDlg", "Play"))
        self.pauseButton.setToolTip(_translate("MediaPlayDlg", "Pause"))
        self.stopButton.setToolTip(_translate("MediaPlayDlg", "Stop"))
        self.voiceButton.setToolTip(_translate("MediaPlayDlg", "Sound/Mute"))
        self.volumeSlider.setToolTip(_translate("MediaPlayDlg", "Volume"))
        self.volumeLabel.setText(_translate("MediaPlayDlg", "1"))
        self.label.setText(_translate("MediaPlayDlg", "%"))
import resouce_rc
