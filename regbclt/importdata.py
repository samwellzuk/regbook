# -*- coding: utf-8 -*-
import sys
import os
import csv
from datetime import datetime
from data.members import DBManager
from data.model import Member

import settings
from data import model


def get_data(fname):
    datalist = []
    with open(fname, newline='', encoding='utf-8-sig') as csvfile:
        spamreader = csv.reader(csvfile, dialect='excel')
        keylist = []
        for row in spamreader:
            if keylist:
                di = {}
                for i, k in enumerate(keylist):
                    di[k] = row[i]
                datalist.append(di)
            else:
                keylist = row
    return datalist


def distr(val):
    v = val.strip()
    if v == 'Las Pinas':
        return 'Las Piñas'
    elif v == 'Paranaque':
        return 'Parañaque'
    elif v == 'Sta Rosa':
        return 'Santa Rosa'
    return v


def is_chinese_char(char):
    if char < '\u4E00' or char > '\u9FD5':
        return False
    return True


def cname(val):
    val = val.strip()
    cn = []
    for i in val:
        if is_chinese_char(i):
            cn.append(i)
    return ''.join(cn)


def chilevel(val):
    val = val.strip()
    if val == '1':
        return 'Level 1'
    if val == '2':
        return 'Level 2'
    if val == '3':
        return 'Level 3'
    if val == '4':
        return 'Level 4'
    if val == '5':
        return 'Level 5'
    return None


def transdt(val):
    val = val.strip()
    try:
        return datetime.strptime(val, '%Y/%m/%d')
    except Exception:
        pass
    return None


def chkstr(val):
    val = val.strip()
    if val:
        return val
    return None


def to_list(memlist, di):
    m = Member(**di)
    mdi = m.to_db_dict()
    if m.base.name:
        mdi.pop('_id')
        mdi['_ts'] = datetime.now()
        memlist.append(mdi)
    else:
        print(mdi)


def process(datalist):
    memlist = []
    for di in datalist:
        family = '{bnick}-{snick}'.format(**di)

        male = {
            'base': {
                'name': chkstr(di['bename']),
                'nick': chkstr(di['bnick']),
                'cname': cname(di['bcname']),
                'sex': 'Male',
                'birth': transdt(di['bbirth']),
                'height': None,
                'weight': None
            },
            'rel': {
                'nation': 'Filipino',
                'cnlang': chilevel(di['bchi']),
                'education': None,
                'occupation': None,
                'plateno': None,
                'family': family,
                'role': 'Husband',
                'father': None,
                'mother': None
            },
            'adr': {
                'cellphone': chkstr(di['bcell']),
                'landline': chkstr(di['tel']),
                'region': chkstr(di['region']),
                'district': chkstr(distr(di['distr'])),
                'street': chkstr(di['addr']),
                'wlandline': chkstr(di['b_tel']),
                'wregion': chkstr(di['region']),
                'wdistrict': chkstr(distr(di['b_distr'])),
                'wstreet': chkstr(di['b_addr'])
            },
            'chu': {
                'group': chkstr(di['bgrp']),
                'state': chkstr(di['bstat']),
                'layhand': transdt(di['blayhand']),
                'baptism': transdt(di['bbapt']),
                'minister': None,
                'baptizer': None,
                'venue': None
            },
        }
        female = {
            'base': {
                'name': chkstr(di['sename']),
                'nick': chkstr(di['snick']),
                'cname': cname(di['scname']),
                'sex': 'Famale',
                'birth': transdt(di['sbirth']),
                'height': None,
                'weight': None
            },
            'rel': {
                'nation': 'Filipino',
                'cnlang': chilevel(di['schi']),
                'education': None,
                'occupation': None,
                'plateno': None,
                'family': family,
                'role': 'Wife',
                'father': None,
                'mother': None
            },
            'adr': {
                'cellphone': chkstr(di['scell']),
                'landline': chkstr(di['tel']),
                'region': chkstr(di['region']),
                'district': chkstr(distr(di['distr'])),
                'street': chkstr(di['addr']),
                'wlandline': chkstr(di['s_tel']),
                'wregion': chkstr(di['region']),
                'wdistrict': chkstr(distr(di['s_distr'])),
                'wstreet': chkstr(di['s_addr'])
            },
            'chu': {
                'group': chkstr(di['sgrp']),
                'state': chkstr(di['sstat']),
                'layhand': transdt(di['slayhand']),
                'baptism': transdt(di['sbapt']),
                'minister': None,
                'baptizer': None,
                'venue': None
            },
        }
        to_list(memlist, male)
        to_list(memlist, female)
    return memlist


def main(fname):
    settings.initialize()
    model.initialize()

    datalist = get_data(fname)
    members = process(datalist)
    dbmgr = DBManager()
    while True:
        user = input('Please input user name: ')
        pwd = input('Please input password: ')
        if dbmgr.auth(user, pwd, 'localhost'):
            break
        print('Login error, please retry')
    coll = dbmgr.get_db().get_collection('members')
    result = coll.insert_many(members)
    print('Import db : ', len(result.inserted_ids))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        fname = sys.argv[1]
        if os.path.isfile(fname) and fname.endswith('csv'):
            main(fname)
            sys.exit(0)
    print('Use: importdata xxx.csv')
