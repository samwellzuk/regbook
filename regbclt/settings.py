# -*-coding: utf-8 -*-
# Created by samwell
import os

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


root_dir = os.path.normpath(os.getcwd())
