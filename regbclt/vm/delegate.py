# -*-coding: utf-8 -*-
# Created by samwell
from PyQt5.QtCore import pyqtSlot, Qt, QEvent
from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit, QMessageBox

from comm.utility import _get_parent_wnd

Qt_ItemDataRole_Field = Qt.UserRole + 1
Qt_ItemDataRole_FieldData = Qt.UserRole + 2


class CustomDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(CustomDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        try:
            fobj = index.data(Qt_ItemDataRole_Field)
            if fobj:
                obj, val = index.data(Qt_ItemDataRole_FieldData)
                editor = fobj.inputobj.create_editor(parent, obj, val)
                return editor
        except Exception as e:
            QMessageBox.warning(_get_parent_wnd(), 'Error', str(e))
            return None
        return super(CustomDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        try:
            fobj = index.data(Qt_ItemDataRole_Field)
            if fobj:
                val = index.data(Qt.EditRole)
                if val is not None:
                    fobj.inputobj.set_editor_data(editor, val)
                return
        except Exception as e:
            QMessageBox.warning(_get_parent_wnd(), 'Error', str(e))
            return
        return super(CustomDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        try:
            fobj = index.data(Qt_ItemDataRole_Field)
            if fobj:
                val = fobj.inputobj.get_editor_data(editor, fobj.ftype)
                model.setData(index, val, Qt.EditRole)
                return
        except Exception as e:
            QMessageBox.warning(_get_parent_wnd(), 'Error', str(e))
            return
        return super(CustomDelegate, self).setModelData(editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def eventFilter(self, editor, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Enter or key == Qt.Key_Return:
                self.commitData.emit(editor)
                self.closeEditor.emit(editor, CustomDelegate.EditNextItem)
                return True
        return super(CustomDelegate, self).eventFilter(editor, event)
