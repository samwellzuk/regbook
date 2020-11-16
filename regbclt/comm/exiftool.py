# -*-coding: utf-8 -*-
# Created by samwell
from typing import List, Tuple, Optional
import os
import subprocess
import tempfile
from settings import temp_dir, exiftool_exe


def _filiter_exif(sinfo: str) -> Tuple[str, bool]:
    sinfo = sinfo.replace('Date/Time', '')
    ignores = [
        'ExifTool Version Number',
        'File Name',
        'Directory',
        'Warning',
        'Error',
        '<!--',
    ]
    reports = []
    has_thumbnail = False
    for sline in sinfo.split('\n'):
        if sline.find('Thumbnail Image') != -1:
            has_thumbnail = True
            continue
        for ig in ignores:
            if sline.find(ig) != -1:
                break
        else:
            reports.append(sline)
    return ''.join(reports), has_thumbnail


def _run_exif(cmds, fout):
    with tempfile.TemporaryFile(dir=temp_dir) as ferr:
        result = subprocess.run(cmds, stdout=fout, stderr=ferr, timeout=100,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode != 0:
            ferr.seek(0)
            serr = ferr.read().decode(encoding='UTF8', errors='ignore')
            raise RuntimeError(f'Exif return code: {result.returncode}\nOutput: {serr}')


def extract_exif(fname: str) -> Tuple[str, Optional[bytes]]:
    if not os.path.isfile(fname):
        raise RuntimeError(f'File dont exist: {fname}')

    img = None
    with tempfile.TemporaryFile(dir=temp_dir) as freport, tempfile.TemporaryFile(dir=temp_dir) as ferr:
        result = subprocess.run([exiftool_exe, '-h', '-charset', 'UTF8', fname],
                                stdout=freport, stderr=ferr, timeout=100,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        freport.seek(0)
        sinfo = freport.read().decode(encoding='UTF8', errors='ignore')
        sreport, has_thumbnail = _filiter_exif(sinfo)
        if not sreport and result.returncode != 0:
            ferr.seek(0)
            serr = ferr.read().decode(encoding='UTF8', errors='ignore')
            raise RuntimeError(f'Exif report return: {result.returncode}\nOutput: {serr}')
    # if has_thumbnail:
    #     ferr.seek(0)
    #     with tempfile.TemporaryFile(dir=temp_dir) as fthumbnail:
    #         result = subprocess.run([exiftool_exe, '-b', '-ThumbnailImage', fname],
    #                                 stdout=fthumbnail, stderr=ferr, timeout=100,
    #                                 creationflags=subprocess.CREATE_NO_WINDOW)
    #         fthumbnail.seek(0)
    #         img = fthumbnail.read()
    #         if not sreport and result.returncode != 0:
    #             ferr.seek(0)
    #             serr = ferr.read().decode(encoding='UTF8', errors='ignore')
    #             raise RuntimeError(f'Exif thumbnail return: {result.returncode}\nOutput: {serr}')
    return sreport, img
