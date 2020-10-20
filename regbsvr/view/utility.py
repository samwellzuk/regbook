#!/usr/bin/python
# -*- coding: utf-8 -*-


from functools import wraps

from PyQt5.QtWidgets import QApplication, QMessageBox


def _get_parent_wnd():
    parent = QApplication.activePopupWidget()
    if not parent:
        parent = QApplication.activePopupWidget()
        if not parent:
            parent = QApplication.activeWindow()
    return parent


def except_check(func):
    @wraps(func)
    def _check(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            QMessageBox.warning(_get_parent_wnd(), 'Error', str(e))
            return None
    return _check


