# -*-coding: utf-8 -*-
# Created by samwell
from typing import Tuple, Optional
import pathlib
import os

import win32api
import win32con
import pywintypes

from PyQt5.QtGui import QImageReader

from .iconextract import extract

_type_cached = {}

_qt_support_formats = ['.' + s.data().decode() for s in QImageReader.supportedImageFormats()]


def _parse_iconval(iconval: str, bestwidth: Optional[int] = None) -> Optional[bytes]:
    parts = iconval.replace('"', '').split(',')
    file = parts[0]
    if not file.startswith('@'):
        filepath = pathlib.Path(os.path.expandvars(file))
        if filepath.is_file():
            suffix = filepath.suffix.lower()
            if suffix in ['.exe', '.dll']:
                index = int(parts[1]) if len(parts) > 1 else 0
                print('Loading exe ', str(filepath), index)
                if filepath.stat().st_size > 5 * 1024 * 1024:
                    return None
                return extract(str(filepath), index, bestwidth)
            elif suffix in _qt_support_formats:
                print('Loading pic ', str(filepath))
                with filepath.open('rb') as of:
                    return of.read()
    return None


def _get_icon(postfix: str, iconval: Optional[str], best_width: Optional[int] = None) -> Optional[bytes]:
    global _type_cached
    if postfix in _type_cached:
        return _type_cached[postfix]
    img = None
    try:
        if iconval:
            img = _parse_iconval(iconval, best_width)
    except Exception as e:
        print(e)
    _type_cached[postfix] = img
    return img


def query_file_type(postfix: str, best_width: Optional[int] = None) -> Tuple[str, Optional[bytes]]:
    if not postfix or not postfix.startswith('.'):
        raise RuntimeError('Error postfix format!')
    postfix = postfix.lower()

    perceivetype = 'unknown'
    iconval = None
    try:
        appid = win32api.RegQueryValue(win32con.HKEY_CLASSES_ROOT, postfix)
        hk = win32api.RegOpenKeyEx(win32con.HKEY_CLASSES_ROOT, postfix)
        try:
            val, _ = win32api.RegQueryValueEx(hk, 'PerceivedType')
            perceivetype = val.lower()
        except pywintypes.error as e:
            pass
        win32api.RegCloseKey(hk)
        try:
            iconval = win32api.RegQueryValue(win32con.HKEY_CLASSES_ROOT, f'{postfix}\\DefaultIcon')
        except pywintypes.error as e:
            try:
                iconval = win32api.RegQueryValue(win32con.HKEY_CLASSES_ROOT, f'{appid}\\DefaultIcon')
            except pywintypes.error as e:
                pass
    except Exception as e:
        pass

    return perceivetype, _get_icon(postfix, iconval, best_width)


def _test():
    query_file_type('.db')
    query_file_type('.dbproj ')

def _test1():
    postfixs = []
    hk = win32api.RegOpenKeyEx(win32con.HKEY_CLASSES_ROOT, None)
    try:
        err = 0
        index = 0
        while True:
            sk = win32api.RegEnumKey(hk, index)
            if sk.startswith('.'):
                postfixs.append(sk.lower())
            else:
                err += 1
            index += 1
            if err > 100:
                break
    except pywintypes.error:
        pass
    finally:
        win32api.RegCloseKey(hk)

    print(len(postfixs))

    for p in postfixs:
        ty, img = query_file_type(p)
        print(p, ty, img is not None)
