# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\test.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(647, 426)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setObjectName("tabWidget")
        name = "Tab 1"

        self.infotabs = []
        self.infovls = []
        self.infotabviews = []

        index = len(self.infotabs)
        tab = QtWidgets.QWidget()
        tab.setObjectName(f"tab{index}")
        verticalLayout = QtWidgets.QVBoxLayout(tab)
        verticalLayout.setObjectName(f"verticalLayout{index}")
        tableView = QtWidgets.QTableView(tab)
        tableView.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        tableView.setObjectName(f"tableView{index}")
        verticalLayout.addWidget(tableView)
        self.infoTab.addTab(tab, name)

        self.infotabs.append(tab)
        self.infovls.append(verticalLayout)
        self.infotabviews.append(tableView)


        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tableView_2 = QtWidgets.QTableView(self.tab_2)
        self.tableView_2.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.tableView_2.setObjectName("tableView_2")
        self.verticalLayout_2.addWidget(self.tableView_2)
        self.tabWidget.addTab(self.tab_2, "Tab 2")

        self.verticalLayout_3.addWidget(self.tabWidget)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Tab 1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "Tab 2"))
