# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\LoginDlg.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginDlg(object):
    def setupUi(self, LoginDlg):
        LoginDlg.setObjectName("LoginDlg")
        LoginDlg.resize(400, 200)
        LoginDlg.setSizeGripEnabled(False)
        LoginDlg.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(LoginDlg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.titlelabel = QtWidgets.QLabel(LoginDlg)
        self.titlelabel.setObjectName("titlelabel")
        self.verticalLayout.addWidget(self.titlelabel)
        self.line = QtWidgets.QFrame(LoginDlg)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.serverlabel = QtWidgets.QLabel(LoginDlg)
        self.serverlabel.setObjectName("serverlabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.serverlabel)
        self.server = QtWidgets.QLineEdit(LoginDlg)
        self.server.setObjectName("server")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.server)
        self.userlabel = QtWidgets.QLabel(LoginDlg)
        self.userlabel.setObjectName("userlabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.userlabel)
        self.username = QtWidgets.QLineEdit(LoginDlg)
        self.username.setObjectName("username")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.username)
        self.pwdlabel = QtWidgets.QLabel(LoginDlg)
        self.pwdlabel.setObjectName("pwdlabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.pwdlabel)
        self.password = QtWidgets.QLineEdit(LoginDlg)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setObjectName("password")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.password)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(131, 31, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.okButton = QtWidgets.QPushButton(LoginDlg)
        self.okButton.setEnabled(False)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout_3.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(LoginDlg)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_3.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.serverlabel.setBuddy(self.server)
        self.userlabel.setBuddy(self.username)
        self.pwdlabel.setBuddy(self.password)

        self.retranslateUi(LoginDlg)
        self.okButton.clicked.connect(LoginDlg.accept)
        self.cancelButton.clicked.connect(LoginDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(LoginDlg)
        LoginDlg.setTabOrder(self.server, self.username)
        LoginDlg.setTabOrder(self.username, self.password)
        LoginDlg.setTabOrder(self.password, self.okButton)
        LoginDlg.setTabOrder(self.okButton, self.cancelButton)

    def retranslateUi(self, LoginDlg):
        _translate = QtCore.QCoreApplication.translate
        LoginDlg.setWindowTitle(_translate("LoginDlg", "Login"))
        self.titlelabel.setText(_translate("LoginDlg", "User Login"))
        self.serverlabel.setText(_translate("LoginDlg", "Server IP(&S)"))
        self.server.setText(_translate("LoginDlg", "localhost"))
        self.userlabel.setText(_translate("LoginDlg", "User Name(&U)"))
        self.pwdlabel.setText(_translate("LoginDlg", "Password(&P)  "))
        self.okButton.setText(_translate("LoginDlg", "Login(&O)"))
        self.cancelButton.setText(_translate("LoginDlg", "Quit(&Q)"))
import resouce_rc
