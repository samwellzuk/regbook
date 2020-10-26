# -*-coding: utf-8 -*-
# Created by samwell
import os
import sys
import codecs
import yaml

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

if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

root_dir = os.path.normpath(os.getcwd())

cities_dict = {}
if os.path.isfile(os.path.join(root_dir, "cities.yml")):
    with codecs.open(os.path.join(root_dir, "cities.yml"), mode='r', encoding="utf-8") as f:
        cities_dict = yaml.load(f, Loader=yaml.FullLoader)
config = {}
if os.path.isfile(os.path.join(root_dir, "settings.yml")):
    with codecs.open(os.path.join(root_dir, "settings.yml"), mode='r', encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

if __name__ == '__main__':
    print(cities_dict['NCR'])
    print(config['nations'])
