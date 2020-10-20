# -*-coding: utf-8 -*-
# Created by samwell
import random
import os.path
import yaml
import shutil


class Word(object):
    def __init__(self, **kwargs):
        self.name = kwargs['name'] if 'name' in kwargs else ''
        self.title_text = kwargs['title_text'] if 'title_text' in kwargs else ''
        self.title_voices = kwargs['title_voices'] if 'title_voices' in kwargs and kwargs['title_voices'] else []
        self.content_text = kwargs['content_text'] if 'content_text' in kwargs else ''
        self.content_voices = kwargs['content_voices'] if 'content_voices' in kwargs and kwargs[
            'content_voices'] else []


class DictWord(object):
    def __init__(self, **kwargs):
        if 'data_path' in kwargs:
            self.data_path = kwargs['data_path']
        else:
            raise RuntimeError('Missing field: data_path')
        if 'dictionary' in kwargs:
            self.dictionary = kwargs['dictionary']
        else:
            raise RuntimeError('Missing field: dictionary')
        if 'tts_lang' in kwargs:
            self.tts_lang = kwargs['tts_lang']
        else:
            raise RuntimeError('Missing field: tts_lang')
        if 'query_word' in kwargs:
            self.query_word = kwargs['query_word']
        else:
            raise RuntimeError('Missing field: query_word')

        self.words = [Word(**wobj) for wobj in kwargs['words']] if 'words' in kwargs and kwargs['words'] else []

    def mk_voice_fname(self):
        while True:
            fname = '%06x.mp3' % random.randrange(16 ** 6)
            fpath = os.path.join(self.data_path, fname)
            if not os.path.exists(fpath):
                return fname, fpath

    def clear(self):
        if os.path.isdir(self.data_path):
            shutil.rmtree(self.data_path, ignore_errors=True)

    def save(self):
        dictobj = {
            'dictionary': self.dictionary,
            'tts_lang': self.tts_lang,
            'query_word': self.query_word,
            'words': [
                {
                    'name': subobj.name,
                    'title_text': subobj.title_text,
                    'title_voices': subobj.title_voices,
                    'content_text': subobj.content_text,
                    'content_voices': subobj.content_voices,
                } for subobj in self.words
            ]
        }
        # clear file which is't be used
        filepath = os.path.join(self.data_path, 'dictword.yml')
        with open(filepath, 'w', encoding='utf8') as fp:
            yaml.dump(dictobj, fp)
        filelist = ['dictword.yml']
        for subobj in self.words:
            filelist.extend(subobj.title_voices)
            filelist.extend(subobj.content_voices)
        fileset = set(filelist)
        for fname in os.listdir(self.data_path):
            if fname in fileset:
                continue
            try:
                fpath = os.path.join(self.data_path, fname)
                os.remove(fpath)
            except:
                pass

    @staticmethod
    def load(data_path):
        filepath = os.path.join(data_path, 'dictword.yml')
        with open(filepath, 'r', encoding='utf8') as fp:
            dictword = yaml.load(fp)
            dictword['data_path'] = data_path
            obj = DictWord(**dictword)
            return obj
