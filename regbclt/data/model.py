# -*-coding: utf-8 -*-
# Created by samwell
import os
from dataclasses import dataclass, asdict, field, InitVar
from uuid import UUID
from typing import Optional, List, Any, Dict

from datetime import datetime
from bson import ObjectId

admin_role: str = "dbOwner"
rw_role: str = "readWrite"
change_self_role: str = "changeOwnPasswordCustomDataRole"


@dataclass
class User:
    user: str
    password: Optional[str] = None
    _id: Optional[str] = None
    userId: Optional[UUID] = None
    db: Optional[str] = None
    roles: List[Dict[str, str]] = field(default_factory=list)
    mechanisms: List[str] = field(default_factory=list)
    customData: Any = None

    def is_admin(self) -> bool:
        for r in self.roles:
            if r['role'] == admin_role:
                return True
        return False


@dataclass
class Member:
    name: Optional[str] = None
    cname: Optional[str] = None
    sex: Optional[str] = None
    birthday: Optional[datetime] = None
    nation: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    homephone: Optional[str] = None
    workphone: Optional[str] = None
    cellphone: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    father: Optional[str] = None
    mother: Optional[str] = None
    saved: Optional[str] = None  # datetime?
    ledby: Optional[str] = None  # ?
    minister: Optional[str] = None  # ?
    baptizer: Optional[str] = None  # ?
    baptismday: Optional[datetime] = None
    venue: Optional[str] = None
    photo: Optional[bytes] = None
    photofmt: Optional[str] = None
    avatar: Optional[bytes] = None
    thumbnail: Optional[bytes] = None
    _id: Optional[ObjectId] = None
    _ts: Optional[datetime] = None


@dataclass
class VirFile:
    filename: str
    length: int
    chunkSize: int
    uploadDate: Optional[datetime]
    _id: Optional[ObjectId] = None
    metadata: InitVar[Dict] = None  # init var, to make exif thumbnail
    owner_id: Optional[ObjectId] = field(init=False)
    upload_user: Optional[str] = field(init=False)
    md5: Optional[str] = field(init=False)
    exif: Optional[str] = field(init=False)
    thumbnail: Optional[bytes] = field(init=False)

    def __post_init__(self, metadata):
        self.owner_id = metadata['owner_id'] if 'owner_id' in metadata else None
        self.upload_user = metadata['upload_user'] if 'upload_user' in metadata else None
        self.md5 = metadata['md5'] if 'md5' in metadata else None
        self.exif = metadata['exif'] if 'exif' in metadata else None
        self.thumbnail = metadata['thumbnail'] if 'thumbnail' in metadata else None

    def to_dict(self):
        di = asdict(self)
        di['metadata'] = {}
        keys = ['owner_id', 'upload_user', 'md5', 'exif', 'thumbnail']
        for key in keys:
            if key in di:
                val = di[key]
                di.pop(key)
                di['metadata'][key] = val
        return di

    def file_suffix(self):
        basename = os.path.basename(self.filename)
        parts = basename.split('.')
        if len(parts) < 2 or not parts[0]:  # file name like : .ignored
            return None
        suffix = parts[-1].lower()
        return f'.{suffix}' if suffix else None
