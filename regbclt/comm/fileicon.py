# -*-coding: utf-8 -*-
# Created by samwell
from typing import Tuple, Optional, NoReturn, List
import pathlib
import os
import dbm
import logging

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


def _parse_iconval(suffix: str, iconval: str, bestwidth: Optional[int] = None) -> Optional[bytes]:
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


def _get_icon(suffix: str, best_width: Optional[int] = None) -> Optional[bytes]:
    iconval = None
    try:
        appid = _get_reg(suffix)
        # perceivetype = _get_reg(suffix,'PerceivedType')
        iconval = _get_reg(f'{suffix}\\DefaultIcon')
        if not iconval and appid:
            iconval = _get_reg(f'{appid}\\DefaultIcon')
            if iconval:
                return _parse_iconval(suffix, iconval, best_width)
    except Exception as e:
        logging.exception('Parse Error[%s] : {%s} ', suffix, iconval)
    return None


def query_file_icon(suffix: str) -> Optional[bytes]:
    assert suffix and suffix.startswith('.')
    assert _icons_db != None
    suffix = suffix.lower()
    if suffix in _icons_db:
        img = _icons_db[suffix]
        return img if img else None
    img = _get_icon(suffix, settings.best_thumbnail_width)
    _icons_db[suffix] = img if img else ''
    _icons_db.sync()
    return img


def _get_all_type() -> List[str]:
    suffixs = []
    hk = win32api.RegOpenKeyEx(win32con.HKEY_CLASSES_ROOT, None)
    try:
        index = 0
        while True:
            sk = win32api.RegEnumKey(hk, index)
            if sk.startswith('.'):
                suffixs.append(sk.lower())
            index += 1
    except pywintypes.error:
        pass
    finally:
        win32api.RegCloseKey(hk)
    return suffixs


def scan_register() -> NoReturn:
    assert _icons_db == None
    settings.initialize()
    initialize()
    try:
        print('scan register... ')
        suffixs = _get_all_type()

        total = len(suffixs)
        for index, pfix in enumerate(suffixs):
            query_file_icon(pfix)
            print(f'extract {int((index + 1) / total * 100)}%')
    except Exception as e:
        logging.exception('scan_register')
    finally:
        uninialize()
