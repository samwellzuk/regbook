# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\UserManageView.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_UserManageView(object):
    def setupUi(self, UserManageView):
        UserManageView.setObjectName("UserManageView")
        UserManageView.resize(913, 421)
        self.verticalLayout = QtWidgets.QVBoxLayout(UserManageView)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.line = QtWidgets.QFrame(UserManageView)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_2.addWidget(self.line)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.addButton = QtWidgets.QPushButton(UserManageView)
        self.addButton.setObjectName("addButton")
        self.horizontalLayout_2.addWidget(self.addButton)
        self.delButton = QtWidgets.QPushButton(UserManageView)
        self.delButton.setObjectName("delButton")
        self.horizontalLayout_2.addWidget(self.delButton)
        self.resetButton = QtWidgets.QPushButton(UserManageView)
        self.resetButton.setObjectName("resetButton")
        self.horizontalLayout_2.addWidget(self.resetButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.usersView = QtWidgets.QTableView(UserManageView)
        self.usersView.setAlternatingRowColors(True)
        self.usersView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.usersView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.usersView.setObjectName("usersView")
        self.verticalLayout.addWidget(self.usersView)

        self.retranslateUi(UserManageView)
        QtCore.QMetaObject.connectSlotsByName(UserManageView)

    def retranslateUi(self, UserManageView):
        _translate = QtCore.QCoreApplication.translate
        UserManageView.setWindowTitle(_translate("UserManageView", "User Manage"))
        self.addButton.setText(_translate("UserManageView", "Add(&A)"))
        self.delButton.setText(_translate("UserManageView", "Delete(&D)"))
        self.resetButton.setText(_translate("UserManageView", "Reset Password(&R)"))
