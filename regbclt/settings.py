# -*-coding: utf-8 -*-
# Created by samwell

import os
import yaml
import codecs
import appdirs

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = appdirs.user_data_dir("regbook")

config = {}
if os.path.isfile(os.path.join(data_dir, "settings.yml")):
    with codecs.open(os.path.join(data_dir, "settings.yml"), mode='rb', encoding="utf-8") as f:
        config.update(yaml.load(f))







