# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\ProgressStepDlg.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ProgressStepDlg(object):
    def setupUi(self, ProgressStepDlg):
        ProgressStepDlg.setObjectName("ProgressStepDlg")
        ProgressStepDlg.setWindowModality(QtCore.Qt.ApplicationModal)
        ProgressStepDlg.resize(600, 300)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ProgressStepDlg)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.progressTxt = QtWidgets.QLabel(ProgressStepDlg)
        self.progressTxt.setObjectName("progressTxt")
        self.verticalLayout_2.addWidget(self.progressTxt)
        self.progressBar = QtWidgets.QProgressBar(ProgressStepDlg)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout_2.addWidget(self.progressBar)
        self.progressSetpTxt = QtWidgets.QLabel(ProgressStepDlg)
        self.progressSetpTxt.setObjectName("progressSetpTxt")
        self.verticalLayout_2.addWidget(self.progressSetpTxt)
        self.progressStepBar = QtWidgets.QProgressBar(ProgressStepDlg)
        self.progressStepBar.setObjectName("progressStepBar")
        self.verticalLayout_2.addWidget(self.progressStepBar)
        self.groupBox = QtWidgets.QGroupBox(ProgressStepDlg)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.errinfoEdit = QtWidgets.QPlainTextEdit(self.groupBox)
        self.errinfoEdit.setReadOnly(True)
        self.errinfoEdit.setObjectName("errinfoEdit")
        self.verticalLayout.addWidget(self.errinfoEdit)
        self.verticalLayout_2.addWidget(self.groupBox)

        self.retranslateUi(ProgressStepDlg)
        QtCore.QMetaObject.connectSlotsByName(ProgressStepDlg)

    def retranslateUi(self, ProgressStepDlg):
        _translate = QtCore.QCoreApplication.translate
        ProgressStepDlg.setWindowTitle(_translate("ProgressStepDlg", "Please Waiting ..."))
        self.progressTxt.setText(_translate("ProgressStepDlg", "Processing..."))
        self.progressSetpTxt.setText(_translate("ProgressStepDlg", "Processing..."))
        self.groupBox.setTitle(_translate("ProgressStepDlg", "Error information"))
