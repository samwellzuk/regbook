# -*-coding: utf-8 -*-
# Created by samwell

from bson import ObjectId
from datetime import datetime

import settings
from data import model

d = {
    '_id': ObjectId(),
    '_ts': datetime.now(),
    'photo': b'test photo',
    'photofmt': 'txt',
    'avatar': b'test avatar',
    'thumbnail': b'test thumbnail',
    'base': {
        'name': 'test',
        'nick': 'test',
        'cname': 'test',
        'sex': 'male',
        'birth': datetime.now(),
        'height': 1.35,
        'weight': 80.5
    },
    'rel': {
        'nation': 'Chinese',
        'cnlang': '5',
        'education': 'Elementary',
        'occupation': 'Student',
        'plateno': 'B00123',
        'family': 'Test',
        'role': 'Husbond',
        'father': 'someone',
        'mother': None
    },
    'adr': {
        'cellphone': '987654321',
        'landline': '987654321',
        'region': None,
        'district': None,
        'street': None,
        'wlandline': None,
        'wregion': None,
        'wdistrict': None,
        'wstreet': None
    },
    'chu': {
        'group': '1',
        'state': 'G',
        'layhand': datetime.now(),
        'baptism': datetime.now(),
        'minister': 'someone',
        'baptizer': 'someone',
        'venue': 'anywhere'
    },
    'meet': [
        {'name': '2017'},
        {'name': '2018'},
        {'name': '2019'},
        {'name': '2020'},
    ]
}

d1 = {
    '_id': ObjectId(),
    '_ts': datetime.now(),
    'photo': b'test photo',
    'photofmt': 'txt',
    'avatar': b'test avatar',
    'thumbnail': b'test thumbnail',
    'base': {
        'name': 'test',
        'nick': 'test',
        'cname': 'test',
        'sex': 'male',
        'birth': datetime.now(),
        'height': 1.35,
        'weight': 80.5
    },
    'rel': {
        'nation': 'Chinese',
        'cnlang': '5',
        'education': 'Elementary',
        'occupation': 'Student',
        'plateno': 'B00123',
        'family': 'Test',
        'role': 'Husbond',
        'father': 'someone',
        'mother': None
    },
    'adr': {
        'cellphone': '987654321',
        'landline': '987654321',
        'region': None,
        'district': None,
        'street': None,
        'wlandline': None,
        'wregion': None,
        'wdistrict': None,
        'wstreet': None
    },
    'chu': {
        'group': '1',
        'state': 'G',
        'layhand': datetime.now(),
        'baptism': datetime.now(),
        'minister': 'someone',
        'baptizer': 'someone',
        'venue': 'anywhere'
    },
    'meet': [
        {'name': '2017'},
        {'name': '2018'},
        {'name': '2019'},
        {'name': '2020'},
    ]
}


def main():
    settings.initialize()
    model.initialize()
    m = model.Member(**d)
    di = m.to_db_dict()
    print(di == d)
    m1 = model.Member(**d1)
    di1 = m1.to_display_dict()
    print(di1 == d1)



if __name__ == "__main__":
    main()
