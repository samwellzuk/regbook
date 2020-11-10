# -*-coding: utf-8 -*-
# Created by samwell
from typing import Tuple, Optional, NoReturn, List
import pathlib
import os
import dbm

import win32api
import win32con
import pywintypes

import settings
from .iconextract import extract

_icons_db = None


def initialize() -> NoReturn:
    global _icons_db
    if _icons_db is None:
        _icons_db = dbm.open(os.path.join(settings.cache_dir, 'icons'), 'c')


def uninialize() -> NoReturn:
    global _icons_db
    if _icons_db:
        _icons_db.close()
        _icons_db = None


def _parse_iconval(iconval: str, bestwidth: Optional[int] = None) -> Optional[bytes]:
    parts = iconval.replace('"', '').split(',')
    file = parts[0]
    if not file.startswith('@'):
        filepath = pathlib.Path(os.path.expandvars(file))
        if filepath.is_file():
            suffix = filepath.suffix.lower()
            if suffix in ['.exe', '.dll']:
                index = int(parts[1]) if len(parts) > 1 else 0
                return extract(str(filepath), index, bestwidth)
            elif suffix in settings.qt_image_formats:
                with filepath.open('rb') as of:
                    return of.read()
    return None


def _get_icon(postfix: str, best_width: Optional[int] = None) -> Optional[bytes]:
    try:
        appid = win32api.RegQueryValue(win32con.HKEY_CLASSES_ROOT, postfix)
        # hk = win32api.RegOpenKeyEx(win32con.HKEY_CLASSES_ROOT, postfix)
        # try:
        #     val, _ = win32api.RegQueryValueEx(hk, 'PerceivedType')
        #     perceivetype = val.lower()
        # except pywintypes.error as e:
        #     pass
        # win32api.RegCloseKey(hk)
        iconval = None
        try:
            iconval = win32api.RegQueryValue(win32con.HKEY_CLASSES_ROOT, f'{postfix}\\DefaultIcon')
        except pywintypes.error as e:
            try:
                iconval = win32api.RegQueryValue(win32con.HKEY_CLASSES_ROOT, f'{appid}\\DefaultIcon')
            except pywintypes.error as e:
                pass
        if iconval:
            img = _parse_iconval(iconval, best_width)
            return img
    except Exception as e:
        pass
    return None


def query_file_icon(postfix: str) -> Optional[bytes]:
    assert postfix and postfix.startswith('.')
    assert _icons_db != None
    postfix = postfix.lower()
    if postfix in _icons_db:
        img = _icons_db[postfix]
        return img if img else None
    img = _get_icon(postfix)
    _icons_db[postfix] = img if img else ''
    _icons_db.sync()
    return img


def _get_all_type() -> List[str]:
    postfixs = []
    hk = win32api.RegOpenKeyEx(win32con.HKEY_CLASSES_ROOT, None)
    try:
        index = 0
        while True:
            sk = win32api.RegEnumKey(hk, index)
            if sk.startswith('.'):
                postfixs.append(sk.lower())
            index += 1
    except pywintypes.error:
        pass
    finally:
        win32api.RegCloseKey(hk)
    return postfixs


def scan_register() -> NoReturn:
    assert _icons_db == None
    settings.initialize()
    initialize()
    try:
        print('scan register... ')
        postfixs = _get_all_type()

        total = len(postfixs)
        for index, pfix in enumerate(postfixs):
            query_file_icon(pfix)
            print(f'extract {int((index + 1) / total * 100)}%')
    except Exception as e:
        print(e)
    finally:
        uninialize()
