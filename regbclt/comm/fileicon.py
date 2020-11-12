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


_iconval_cache = {}


def _parse_iconval(postfix: str, iconval: str, bestwidth: Optional[int] = None) -> Optional[bytes]:
    if iconval in _iconval_cache:
        return _iconval_cache[iconval]
    imgbin = None
    try:
        parts = iconval.replace('"', '').split(',')
        file = parts[0]
        if not file.startswith('@'):
            filepath = pathlib.Path(os.path.expandvars(file))
            if filepath.is_file():
                with filepath.open('rb') as of:
                    pehead = of.read(2)
                # check is pe file
                if pehead[0] == 0x4D and pehead[1] == 0x5A:
                    index = int(parts[1]) if len(parts) > 1 else 0
                    imgbin = extract(str(filepath), index, bestwidth)
                else:
                    suffix = filepath.suffix.lower()
                    if suffix in settings.qt_image_formats:
                        with filepath.open('rb') as of:
                            imgbin = of.read()
    finally:
        _iconval_cache[iconval] = imgbin
    return imgbin


def _get_reg(path, valname=''):
    hk = None
    try:
        hk = win32api.RegOpenKeyEx(win32con.HKEY_CLASSES_ROOT, path)
        # t == 1 REG_SZ
        # t == 2 REG_EXPAND_SZ
        val, t = win32api.RegQueryValueEx(hk, valname)
        return val
    except pywintypes.error:
        return None
    finally:
        if hk:
            win32api.RegCloseKey(hk)


def _get_icon(postfix: str, best_width: Optional[int] = None) -> Optional[bytes]:
    iconval = None
    try:
        appid = _get_reg(postfix)
        # perceivetype = _get_reg(postfix,'PerceivedType')
        iconval = _get_reg(f'{postfix}\\DefaultIcon')
        if not iconval and appid:
            iconval = _get_reg(f'{appid}\\DefaultIcon')
            if iconval:
                return _parse_iconval(postfix, iconval, best_width)
    except Exception as e:
        print(f"Parse Error[{postfix}] : {iconval} :", e)
    return None


best_thumbnail_width = 128


def query_file_icon(postfix: str) -> Optional[bytes]:
    assert postfix and postfix.startswith('.')
    assert _icons_db != None
    postfix = postfix.lower()
    if postfix in _icons_db:
        img = _icons_db[postfix]
        return img if img else None
    img = _get_icon(postfix, best_thumbnail_width)
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
