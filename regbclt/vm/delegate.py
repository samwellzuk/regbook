# -*-coding: utf-8 -*-
# Created by samwell
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit, QMessageBox

from comm.utility import _get_parent_wnd

Qt_ItemDataRole_Field = Qt.UserRole + 1
Qt_ItemDataRole_FieldData = Qt.UserRole + 2


class CustomDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(CustomDelegate, self).__init__(parent)

    @pyqtSlot()
    def commitAndCloseEditor(self):
        editor = self.sender()
        if isinstance(editor, QLineEdit):
            self.commitData.emit(editor, CustomDelegate.EditNextItem)
            self.closeEditor.emit(editor)

    def createEditor(self, parent, option, index):
        try:
            fobj = index.data(Qt_ItemDataRole_Field)
            if fobj:
                obj, val = index.data(Qt_ItemDataRole_FieldData)
                editor = fobj.inputobj.create_editor(parent, obj, val)
                if isinstance(editor, QLineEdit):
                    editor.returnPressed.connect(self.commitAndCloseEditor)
                return editor
        except Exception as e:
            QMessageBox.warning(_get_parent_wnd(), 'Error', str(e))
        return super(CustomDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        try:
            fobj = index.data(Qt_ItemDataRole_Field)
            if fobj:
                val = index.data(Qt.EditRole)
                if val is not None:
                    fobj.inputobj.set_editor_data(editor, fobj.ftype, val)
                return
        except Exception as e:
            QMessageBox.warning(_get_parent_wnd(), 'Error', str(e))
        return super(CustomDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        try:
            fobj = index.data(Qt_ItemDataRole_Field)
            if fobj:
                val = fobj.inputobj.get_editor_data(editor, fobj.ftype)
                return model.setData(index, val, Qt.EditRole)
        except Exception as e:
            QMessageBox.warning(_get_parent_wnd(), 'Error', str(e))
        return super(CustomDelegate, self).setModelData(self, editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
