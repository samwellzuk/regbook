# -*-coding: utf-8 -*-
# Created by samwell
import os
import sys
import logging
import codecs
import yaml

from PyQt5.QtGui import QImageReader
import xml.etree.ElementTree as ET

# if getattr(sys, 'frozen', False):
#     # we are running in a bundle
#     bundle_dir = sys._MEIPASS    C:\Users\atten\AppData\Local\Temp\_MEI1093962
#     sys.argv[0]                  qdir.exe
#     sys.executable               D:\ChruchProjects\regbook\regbsvr\qdir.exe
#     os.getcwd()                  D:\ChruchProjects\regbook\regbsvr
# else:
#     # we are running in a normal Python environment
#     bundle_dir = os.path.dirname(os.path.abspath(
#         __file__))               D:\ChruchProjects\regbook\regbsvr
#     sys.argv[0]                  qdir.py
#     sys.executable               D:\ChruchProjects\regbook\venv\Scripts\python.exe
#     os.getcwd()                  D:\ChruchProjects\regbook\regbsvr

preview_max_filesz = 5 * 1024 * 1024
best_thumbnail_width = 128

_file_exist_list = []

root_dir = os.path.normpath(os.getcwd())
if not os.path.isfile(os.path.join(root_dir, "conf", "member.yml")):
    root_dir = os.path.normpath(os.path.join(os.getcwd(), '..'))

cache_dir = os.path.join(root_dir, 'cache')
if not os.path.isdir(cache_dir):
    os.makedirs(cache_dir, exist_ok=True)

tmpl_dir = os.path.join(root_dir, 'tmpl')
if not os.path.isdir(tmpl_dir):
    os.makedirs(tmpl_dir, exist_ok=True)

temp_dir = os.path.join(root_dir, 'temp')
if not os.path.isdir(temp_dir):
    os.makedirs(temp_dir, exist_ok=True)

conf_dir = os.path.join(root_dir, 'conf')
member_yml = os.path.join(conf_dir, "member.yml")
_file_exist_list.append(member_yml)

qt_image_formats = set(['.' + s.data().decode() for s in QImageReader.supportedImageFormats()])

vlc_dir = os.path.join(root_dir, 'vlc')
vlc_libvlc_dll = os.path.join(vlc_dir, 'libvlc.dll')
vlc_extensions_wxs = os.path.join(vlc_dir, "msi", "extensions.wxs")
_file_exist_list.append(vlc_libvlc_dll)
_file_exist_list.append(vlc_extensions_wxs)
os.environ["PYTHON_VLC_MODULE_PATH"] = vlc_dir
os.environ["PYTHON_VLC_LIB_PATH"] = vlc_libvlc_dll
vlc_video_formats = set()
vlc_audio_formats = set()
if os.path.isfile(vlc_extensions_wxs):
    _root = ET.parse(vlc_extensions_wxs).getroot()
    _ns = {'wix': 'http://schemas.microsoft.com/wix/2006/wi'}
    for e in _root.findall('.//wix:Component[@Id="CompAudioFileAssociation"]/wix:RegistryValue[@Root="HKLM"]', _ns):
        vlc_audio_formats.add(e.get('Name').lower())
    for e in _root.findall('.//wix:Component[@Id="CompVideoFileAssociation"]/wix:RegistryValue[@Root="HKLM"]', _ns):
        vlc_video_formats.add(e.get('Name').lower())

exiftool_exe = os.path.join(root_dir, 'exiftool', 'exiftool.exe')
_file_exist_list.append(exiftool_exe)


def initialize():
    for f in _file_exist_list:
        if not os.path.isfile(f):
            raise RuntimeError(f'File not exist: {f}')
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
