# -*-coding: utf-8 -*-
# Created by samwell
from PyQt5.QtCore import QRegExp, pyqtSlot, Qt, QEvent
from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit, QComboBox, QStyleOptionButton, QStyle, QApplication
from PyQt5.QtGui import QRegExpValidator

Qt_ItemDataRole_CustomType = Qt.UserRole + 1
Qt_ItemDataRole_CustomTypeData = Qt.UserRole + 2

Qt_CustomType_CombBox = 1
Qt_CustomType_CombBoxEditable = 2
Qt_CustomType_RegEdit = 3
Qt_CustomType_Button = 4


class CustomDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.button_cbs = {}

    def createEditor(self, parent, option, index):
        role_type = index.data(Qt_ItemDataRole_CustomType)
        if role_type == Qt_CustomType_CombBox:
            data = index.data(Qt_ItemDataRole_CustomTypeData)
            combobox = QComboBox(parent)
            combobox.addItems(data)
            return combobox
        if role_type == Qt_CustomType_CombBoxEditable:
            data = index.data(Qt_ItemDataRole_CustomTypeData)
            combobox = QComboBox(parent)
            combobox.addItems(data)
            combobox.setEditable(True)
            return combobox
        elif role_type == Qt_CustomType_RegEdit:
            strreg = index.data(Qt_ItemDataRole_CustomTypeData)
            qregex = QRegExp(strreg)
            editor = QLineEdit(parent)
            editor.setValidator(QRegExpValidator(qregex, self))
            editor.returnPressed.connect(self.commitAndCloseEditor)
            return editor
        else:
            return QStyledItemDelegate.createEditor(self, parent, option,
                                                    index)

    def paint(self, painter, option, index):
        role_type = index.data(Qt_ItemDataRole_CustomType)
        if role_type == Qt_CustomType_Button:
            visible, txt, cb = index.data(Qt_ItemDataRole_CustomTypeData)
            if visible:
                row = index.row()
                column = index.column()
                self.button_cbs[(row, column)] = cb

                button = QStyleOptionButton()
                button.rect = option.rect.adjusted(2, 2, -2, -2)
                button.text = txt
                button.state = QStyle.State_Enabled
                QApplication.style().drawControl(QStyle.CE_PushButton, button, painter)
            return
        else:
            return QStyledItemDelegate.paint(self, painter, option, index)

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease:
            role_type = index.data(Qt_ItemDataRole_CustomType)
            if role_type == Qt_CustomType_Button:
                visible, txt, cb = index.data(Qt_ItemDataRole_CustomTypeData)
                if visible:
                    row = index.row()
                    column = index.column()
                    cb = self.button_cbs[(row, column)]
                    cb()
                    return True
        return QStyledItemDelegate.editorEvent(self, event, model, option, index)

    @pyqtSlot()
    def buttenClicked(self):
        button = self.sender()
        if id(button) in self.button_cbs:
            cb = self.button_cbs[id(button)]
            cb()

    @pyqtSlot()
    def commitAndCloseEditor(self):
        editor = self.sender()
        if isinstance(editor, QLineEdit):
            self.commitData.emit(editor)
            self.closeEditor.emit(editor)

    def setEditorData(self, editor, index):
        role_type = index.data(Qt_ItemDataRole_CustomType)
        if role_type == Qt_CustomType_CombBox:
            text = index.data(Qt.DisplayRole)
            if text:
                i = editor.findText(text)
                if i == -1:
                    i = 0
                editor.setCurrentIndex(i)
            else:
                editor.setCurrentIndex(0)
        elif role_type == Qt_CustomType_CombBoxEditable:
            text = index.data(Qt.DisplayRole)
            if text:
                i = editor.findText(text)
                if i == -1:
                    editor.addItem(text)
                    editor.setCurrentText(text)
                else:
                    editor.setCurrentIndex(i)
            else:
                editor.setCurrentIndex(0)
        elif role_type == Qt_CustomType_RegEdit:
            text = index.data(Qt.DisplayRole)
            editor.setText(text)
        elif role_type == Qt_CustomType_Button:
            pass
        else:
            text = index.data(Qt.DisplayRole)
            editor.setText(text)
            # QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        role_type = index.data(Qt_ItemDataRole_CustomType)
        if role_type == Qt_CustomType_CombBox:
            model.setData(index, editor.currentText())
        elif role_type == Qt_CustomType_CombBoxEditable:
            model.setData(index, editor.currentText())
        elif role_type == Qt_CustomType_RegEdit:
            model.setData(index, editor.text())
        elif role_type == Qt_CustomType_Button:
            pass
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
