# -*-coding: utf-8 -*-
# Created by samwell
from dataclasses import dataclass, asdict, field
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
    avatar: Optional[bytes] = None
    thumbnail: Optional[bytes] = None
    _id: Optional[ObjectId] = None
    _ts: Optional[datetime] = None

    def to_short_dict(self):
        result = asdict(self)
        result.pop('_id')
        result.pop('_ts')
        return result
