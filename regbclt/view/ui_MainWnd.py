# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\MainWnd.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1266, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/app.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.projTitle = QtWidgets.QLabel(self.centralWidget)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(16)
        self.projTitle.setFont(font)
        self.projTitle.setObjectName("projTitle")
        self.horizontalLayout_3.addWidget(self.projTitle)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_31 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_31.setObjectName("horizontalLayout_31")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_31.addItem(spacerItem1)
        self.userTitle = QtWidgets.QLabel(self.centralWidget)
        self.userTitle.setObjectName("userTitle")
        self.horizontalLayout_31.addWidget(self.userTitle)
        self.changePwd = QtWidgets.QPushButton(self.centralWidget)
        self.changePwd.setObjectName("changePwd")
        self.horizontalLayout_31.addWidget(self.changePwd)
        self.verticalLayout.addLayout(self.horizontalLayout_31)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.memberManage = QtWidgets.QCommandLinkButton(self.centralWidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/home.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.memberManage.setIcon(icon1)
        self.memberManage.setCheckable(True)
        self.memberManage.setChecked(True)
        self.memberManage.setAutoExclusive(True)
        self.memberManage.setObjectName("memberManage")
        self.horizontalLayout.addWidget(self.memberManage)
        self.userManage = QtWidgets.QCommandLinkButton(self.centralWidget)
        self.userManage.setIcon(icon1)
        self.userManage.setCheckable(True)
        self.userManage.setAutoExclusive(True)
        self.userManage.setObjectName("userManage")
        self.horizontalLayout.addWidget(self.userManage)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(self.centralWidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.workspace = QtWidgets.QStackedWidget(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.workspace.sizePolicy().hasHeightForWidth())
        self.workspace.setSizePolicy(sizePolicy)
        self.workspace.setObjectName("workspace")
        self.verticalLayout.addWidget(self.workspace)
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Register Book"))
        self.projTitle.setText(_translate("MainWindow", "Christian Gospel Center"))
        self.userTitle.setText(_translate("MainWindow", "Welcome xxx"))
        self.changePwd.setText(_translate("MainWindow", "Change Password"))
        self.memberManage.setText(_translate("MainWindow", "Member Manage"))
        self.userManage.setText(_translate("MainWindow", "User Manage"))
import resouce_rc