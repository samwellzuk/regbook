# -*-coding: utf-8 -*-
# Created by samwell
from typing import List, Tuple, Optional
import os
import subprocess
import tempfile
from settings import tmp_dir, exiftool_exe


def _filiter_exif(sinfo: str) -> Tuple[str, bool]:
    sinfo = sinfo.replace('Date/Time', '')
    ignores = [
        'ExifTool Version Number',
        'File Name',
        'Directory',
        'Warning',
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
    with tempfile.TemporaryFile(dir=tmp_dir) as ferr:
        result = subprocess.run(cmds, stdout=fout, stderr=ferr)
        if result.returncode != 0:
            ferr.seek(0)
            serr = ferr.read().decode(encoding='UTF8', errors='ignore')
            raise RuntimeError(f'Exif return code: {result.returncode}\nOutput: {serr}')


def extract_exif(fname: str) -> Tuple[str, Optional[bytes]]:
    if not os.path.isfile(fname):
        raise RuntimeError(f'File dont exist: {fname}')
    freport, fthumbnail = None, None
    try:
        # get report
        freport = tempfile.TemporaryFile(dir=tmp_dir)
        _run_exif([exiftool_exe, '-h', '-charset', 'UTF8', fname], freport)
        freport.seek(0)
        sinfo = freport.read().decode(encoding='UTF8', errors='ignore')
        sreport, has_thumbnail = _filiter_exif(sinfo)
        if not has_thumbnail:
            return sreport, None
        # get thumbnail
        fthumbnail = tempfile.TemporaryFile(dir=tmp_dir)
        _run_exif([exiftool_exe, '-b', '-ThumbnailImage', fname], fthumbnail)
        fthumbnail.seek(0)
        img = fthumbnail.read()
        return sreport, img if img else None
    finally:
        if fthumbnail:
            fthumbnail.close()
        if freport:
            freport.close()
