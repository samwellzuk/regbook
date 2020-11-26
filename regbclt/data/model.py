# -*-coding: utf-8 -*-
# Created by samwell
import os
from typing import Dict, Any, Optional, List, NoReturn, Tuple
from dataclasses import make_dataclass, asdict
from datetime import datetime
from abc import ABC, abstractmethod
from importlib import import_module

from PyQt5.QtWidgets import QCheckBox, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTimeEdit, QDateEdit, \
    QDateTimeEdit, QWidget
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QRegExpValidator, QRegularExpressionValidator
from PyQt5.QtCore import Qt, QRegExp, QRegularExpression, QDateTime

from bson import ObjectId
import yaml

from settings import member_yml, conf_dir

avatar_ratio = 1.4
avatar_margin = 0.05
avatar_width_max = 750
avatar_highet_max = 1050

head_margin = 0.05
head_width_max = 128
head_highet_max = 128
head_width = head_width_max + 2
head_high = head_highet_max + 2

_inputs: Dict = {}
_outputs: Dict = {}
_classes: Dict = {}
_classdefs: Dict = {}
_obj: Dict = {}
_xmlfiles: Dict = {}


class Member:
    _id: ObjectId
    _ts: datetime
    photo: bytes
    photofmt: str
    avatar: bytes
    thumbnail: bytes

    def __init__(self, _id=None, _ts=None, photo=None, photofmt=None, avatar=None, thumbnail=None, **kwargs):
        self._id = _id
        self._ts = _ts
        self.photo = photo
        self.photofmt = photofmt
        self.avatar = avatar
        self.thumbnail = thumbnail
        for k in _obj:
            if isinstance(_obj[k], list):
                v = _obj[k][0]
                clsdef = _classdefs[v]
                content = []
                if k in kwargs:
                    for parms in kwargs[k]:
                        content.append(clsdef(**parms))  # readonly field can't pass to class
                setattr(self, k, content)
            elif isinstance(_obj[k], str):
                v = _obj[k]
                clsdef = _classdefs[v]
                if k in kwargs:
                    parms = kwargs[k]
                    setattr(self, k, clsdef(**parms))
                else:
                    setattr(self, k, clsdef())
            else:  # type is Field
                fobj = _obj[k]
                if not fobj.is_readonly():
                    if k in kwargs:
                        setattr(self, k, kwargs[k])
                    else:
                        setattr(self, k, fobj.fdefault)

    def to_db_dict(self) -> Dict:
        di = {
            '_id': self._id,
            '_ts': self._ts,
            'photo': self.photo,
            'photofmt': self.photofmt,
            'avatar': self.avatar,
            'thumbnail': self.thumbnail,
        }
        for k in _obj:
            if isinstance(_obj[k], list):
                obs = []
                for o in getattr(self, k):
                    obs.append(asdict(o))
                di[k] = obs
            elif isinstance(_obj[k], str):
                o = getattr(self, k)
                di[k] = asdict(o)
            else:  # type is Field
                fobj = _obj[k]
                if not fobj.is_readonly():
                    di[k] = getattr(self, k)
        return di

    def to_display_dict(self) -> Dict:
        """
        return dict for display , use output to produce every field,  include readonly field
        :return:
        """

        def _get_cls(cls, obj):
            odi = {}
            for kf in cls:
                fobj = cls[kf]
                val = None if fobj.is_readonly() else getattr(obj, kf)
                odi[kf] = fobj.outputobj.to_str(obj, val)
                if odi[kf] is None:
                    odi[kf] = ''
            return odi

        di = {}
        for k in _obj:
            if isinstance(_obj[k], list):
                cls = _classes[_obj[k][0]]
                objlist = getattr(self, k)
                odis = []
                for obj in objlist:
                    odis.append(_get_cls(cls, obj))
                di[k] = odis
            elif isinstance(_obj[k], str):
                cls = _classes[_obj[k]]
                obj = getattr(self, k)
                di[k] = _get_cls(cls, obj)
            else:  # type if Field
                fobj = _obj[k]
                obj = self
                val = None if fobj.is_readonly() else getattr(self, k)
                di[k] = fobj.outputobj.to_str(obj, val)
                if di[k] is None:
                    di[k] = ''
        return di


class InputBase(ABC):
    @abstractmethod
    def create_editor(self, parent, obj, val):
        raise NotImplementedError('create_editor')

    @abstractmethod
    def set_editor_data(self, editor, data):
        raise NotImplementedError('create_editor')

    @abstractmethod
    def get_editor_data(self, editor, ftype):
        raise NotImplementedError('create_editor')

    def transform(self, val, dsttype):
        if isinstance(val, str):
            if dsttype == str:
                return val
            elif dsttype == int:
                return int(val)
            elif dsttype == float:
                return float(val)
        elif isinstance(val, bool):  # bool > int > object
            if dsttype == bool:
                return val
        elif isinstance(val, int):
            if dsttype == str:
                return str(val)
            elif dsttype == int:
                return val
            elif dsttype == float:
                return float(val)
        elif isinstance(val, float):
            if dsttype == str:
                return str(val)
            elif dsttype == int:
                return int(val)
            elif dsttype == float:
                return val
        elif isinstance(val, datetime):
            if dsttype == datetime:
                return val
        raise TypeError(f'Unsupported type transform: {type(val)}->{dsttype}')


class InputCheckBox(InputBase):
    def __init__(self, title=None):
        self.title = title

    def create_editor(self, parent, obj, val):
        if self.title:
            editor = QCheckBox(self.title, parent=parent)
        else:
            editor = QCheckBox(parent=parent)
        editor.setStyleSheet("QCheckBox{background-color:white;}")
        return editor

    def set_editor_data(self, editor, data):
        val = self.transform(data, bool)
        editor.setCheckState(Qt.Checked if val else Qt.Unchecked)

    def get_editor_data(self, editor, ftype):
        s = editor.checkState()
        val = (s == Qt.Checked)
        return self.transform(val, ftype)


class LineEditinputMask(object):
    def __init__(self, inputMask=None):
        self.inputMask = inputMask

    def init_editor(self, parent, editor):
        if self.inputMask:
            editor.setInputMask(self.inputMask)


class LineEditInt(object):
    def __init__(self, minimum=None, maximum=None):
        self.minimum = minimum
        self.maximum = maximum

    def init_editor(self, parent, editor):
        if self.minimum is not None or self.maximum is not None:
            validator = QIntValidator(parent=parent)
            if self.minimum is not None:
                validator.setBottom(self.minimum)
            if self.maximum is not None:
                validator.setTop(self.maximum)
            editor.setValidator(validator)


class LineEditDouble(object):
    def __init__(self, bottom=None, top=None, decimals=None, notation=None):
        self.bottom = bottom
        self.top = top
        self.decimals = decimals
        self.notation = notation

    def init_editor(self, parent, editor):
        if self.bottom is not None or self.top is not None \
                or self.decimals is not None or self.notation is not None:
            validator = QDoubleValidator(parent=parent)
            if self.bottom is not None:
                validator.setBottom(self.bottom)
            if self.top is not None:
                validator.setTop(self.top)
            if self.decimals is not None:
                validator.setDecimals(self.decimals)
            if self.notation is not None:
                if self.notation == QDoubleValidator.StandardNotation:
                    validator.setNotation(QDoubleValidator.StandardNotation)
                elif self.notation == QDoubleValidator.ScientificNotation:
                    validator.setNotation(QDoubleValidator.ScientificNotation)
            editor.setValidator(validator)


class LineEditRegExp(object):
    def __init__(self, pattern=None, cs=None, syntax=None):
        self.pattern = pattern
        self.cs = cs
        self.syntax = syntax

    def init_editor(self, parent, editor):
        if self.pattern is not None or self.cs is not None or self.syntax is not None:
            regexp = QRegExp()
            if self.pattern is not None:
                regexp.setPattern(self.pattern)
            if self.cs is not None:
                if self.cs == 0:
                    regexp.setCaseSensitivity(Qt.CaseInsensitive)
                elif self.cs == 1:
                    regexp.setCaseSensitivity(Qt.CaseSensitive)
            if self.syntax is not None:
                regexp.setPatternSyntax(self.syntax)
            validator = QRegExpValidator(regexp, parent=parent)
            editor.setValidator(validator)


class LineEditRegularExpression(object):
    def __init__(self, pattern=None, options=None):
        self.pattern = pattern
        self.options = options

    def init_editor(self, parent, editor):
        if self.pattern is not None or self.options is not None:
            regexp = QRegularExpression()
            if self.pattern is not None:
                regexp.setPattern(self.pattern)
            if self.options is not None:
                regexp.setPatternOptions(self.options)
            validator = QRegularExpressionValidator(regexp, parent=parent)
            editor.setValidator(validator)


class InputLineEdit(InputBase):
    def __init__(self, validator=None):
        self.validator = None
        if validator:
            cls = validator['class']
            validator.pop('class')
            if cls == 'inputMask':
                self.validator = LineEditinputMask(**validator)
            elif cls == 'QIntValidator':
                self.validator = LineEditInt(**validator)
            elif cls == 'QDoubleValidator':
                self.validator = LineEditDouble(**validator)
            elif cls == 'QRegExpValidator':
                self.validator = LineEditRegExp(**validator)
            elif cls == 'QRegularExpressionValidator':
                self.validator = LineEditRegularExpression(**validator)

    def create_editor(self, parent, obj, val):
        editor = QLineEdit(parent=parent)
        if self.validator:
            self.validator.init_editor(parent, editor)
        return editor

    def set_editor_data(self, editor, data):
        val = self.transform(data, str)
        editor.setText(val)
        return

    def get_editor_data(self, editor, ftype):
        val = editor.text()
        return self.transform(val, ftype)


class ComboBoxItems(object):
    def __init__(self, items):
        self.items = items

    def init_editor(self, editor, obj, val):
        editor.addItems(self.items)


class ComboBoxLambda(object):
    def __init__(self, function, ymlfile=None, modules=None):
        self.srcdi = _xmlfiles[ymlfile] if ymlfile else {}
        self.func = _build_func(function, modules)

    def init_editor(self, editor, obj, val):
        items = self.func(obj, self.srcdi)
        editor.addItems(items)


class InputComboBox(InputBase):
    def __init__(self, editable=None, items=None):
        self.editable = editable
        self.srcobj = None
        if items is not None:
            if isinstance(items, list):
                self.srcobj = ComboBoxItems(items)
            elif items['class'] == 'lambda':
                items.pop('class')
                self.srcobj = ComboBoxLambda(**items)

    def create_editor(self, parent, obj, val):
        editor = QComboBox(parent=parent)
        if self.editable is not None:
            editor.setEditable(self.editable)
        if self.srcobj:
            self.srcobj.init_editor(editor, obj, val)
        return editor

    def set_editor_data(self, editor, data):
        val = self.transform(data, str)
        editor.setCurrentText(val)

    def get_editor_data(self, editor, ftype):
        val = editor.currentText()
        return self.transform(val, ftype)


class InputSpinBox(InputBase):
    def __init__(self, minimum=None, maximum=None, step=None, intbase=None, suffix=None, prefix=None):
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.intbase = intbase
        self.suffix = suffix
        self.prefix = prefix

    def create_editor(self, parent, obj, val):
        editor = QSpinBox(parent=parent)
        if self.minimum is not None:
            editor.setMinimum(self.minimum)
        if self.maximum is not None:
            editor.setMaximum(self.maximum)
        if self.step is not None:
            editor.setSingleStep(self.step)
        if self.intbase is not None:
            editor.setDisplayIntegerBase(self.intbase)
        if self.suffix is not None:
            editor.setSuffix(self.suffix)
        if self.prefix is not None:
            editor.setPrefix(self.prefix)
        return editor

    def set_editor_data(self, editor, data):
        val = self.transform(data, int)
        editor.setValue(val)
        return

    def get_editor_data(self, editor, ftype):
        val = editor.value()
        return self.transform(val, ftype)


class InputDoubleSpinBox(InputBase):
    def __init__(self, minimum=None, maximum=None, step=None, decimals=None, suffix=None, prefix=None):
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.decimals = decimals
        self.suffix = suffix
        self.prefix = prefix

    def create_editor(self, parent, obj, val):
        editor = QDoubleSpinBox(parent=parent)
        if self.minimum is not None:
            editor.setMinimum(self.minimum)
        if self.maximum is not None:
            editor.setMaximum(self.maximum)
        if self.step is not None:
            editor.setSingleStep(self.step)
        if self.decimals is not None:
            editor.setDecimals(self.decimals)
        if self.suffix is not None:
            editor.setSuffix(self.suffix)
        if self.prefix is not None:
            editor.setPrefix(self.prefix)
        return editor

    def set_editor_data(self, editor, data):
        val = self.transform(data, float)
        editor.setValue(val)
        return

    def get_editor_data(self, editor, ftype):
        val = editor.value()
        return self.transform(val, ftype)


class InputTimeEdit(InputBase):
    def __init__(self, displayfmt=None):
        self.displayfmt = displayfmt

    def create_editor(self, parent, obj, val):
        editor = QTimeEdit(parent=parent)
        if self.displayfmt is not None:
            editor.setDisplayFormat(self.displayfmt)
        return editor

    def set_editor_data(self, editor, data):
        val = self.transform(data, datetime)
        editor.setDateTime(QDateTime(val))
        return

    def get_editor_data(self, editor, ftype):
        val = editor.dateTime().toPyDateTime()
        return self.transform(val, ftype)


class InputDateEdit(InputBase):
    def __init__(self, calendar=None, displayfmt=None):
        self.calendar = calendar
        self.displayfmt = displayfmt

    def create_editor(self, parent, obj, val):
        editor = QDateEdit(parent=parent)
        if self.displayfmt is not None:
            editor.setDisplayFormat(self.displayfmt)
        if self.calendar is not None:
            editor.setCalendarPopup(self.calendar)
        return editor

    def set_editor_data(self, editor, data):
        val = self.transform(data, datetime)
        editor.setDateTime(QDateTime(val))
        return

    def get_editor_data(self, editor, ftype):
        val = editor.dateTime().toPyDateTime()
        return self.transform(val, ftype)


class InputDateTimeEdit(InputBase):
    def __init__(self, calendar=None, displayfmt=None):
        self.calendar = calendar
        self.displayfmt = displayfmt

    def create_editor(self, parent, obj, val):
        editor = QDateTimeEdit(parent=parent)
        if self.displayfmt is not None:
            editor.setDisplayFormat(self.displayfmt)
        if self.calendar is not None:
            editor.setCalendarPopup(self.calendar)
        return editor

    def set_editor_data(self, editor, data):
        val = self.transform(data, datetime)
        editor.setDateTime(QDateTime(val))
        return

    def get_editor_data(self, editor, ftype):
        val = editor.dateTime().toPyDateTime()
        return self.transform(val, ftype)


class OutputBase(ABC):
    @abstractmethod
    def to_str(self, obj, val) -> str:
        raise NotImplementedError('to_str')


class OutputFmt(OutputBase):
    def __init__(self, format):
        self.format = format

    def to_str(self, obj, val) -> str:
        return self.format.format(val) if val is not None else None


class OutputFunc(OutputBase):
    def __init__(self, function, modules=None):
        self.func = _build_func(function, modules)

    def to_str(self, obj, val) -> str:
        return self.func(obj, val)


def _build_func(sfunc, modules):
    gdict = {}
    if modules:
        for m in modules:
            gdict[m] = import_module(m)
    return eval(sfunc, gdict)


class Field(object):
    ftype: type
    fdefault: Any
    title: str
    width: int
    horizontal: str
    vertical: str
    blod: bool
    isreadonly: bool
    inputobj: Optional[InputBase]
    outputobj: OutputBase

    def __init__(self, name, type, output, default=None, title=None, width=None, horizontal=None, vertical=None,
                 blod=None, input=None):
        if type == 'bool':
            self.ftype = bool
        elif type == 'str':
            self.ftype = str
        elif type == 'int':
            self.ftype = int
        elif type == 'float':
            self.ftype = float
        elif type == 'datetime':
            self.ftype = datetime
        self.fdefault = default
        self.title = title if title else name
        self.width = width if width else 80
        self.horizontal = horizontal if horizontal else 'left'
        self.vertical = vertical if vertical else 'center'
        self.blod = blod if blod else False
        if input:
            self.inputobj = _inputs[input]
            self.isreadonly = False
        else:
            self.inputobj = None
            self.isreadonly = True
        self.outputobj = _outputs[output]

    def is_readonly(self) -> bool:
        return self.isreadonly


def _check_key(di, name, ks):
    for k in di:
        if k not in ks.keys():
            raise RuntimeError(f'{name}: unexpected key[{k}]')
        if di[k] and ks[k] and not isinstance(di[k], ks[k]):
            raise RuntimeError(f'{name}: key[{k}] type error')


def _init_field(name, field):
    _check_key(field, name,
               {'type': str, 'default': None, 'title': str, 'width': int,
                'horizontal': str, 'vertical': str, 'blod': bool, 'input': str, 'output': str})
    if 'horizontal' in field and field['horizontal'] not in ('left', 'center', 'right'):
        raise RuntimeError(f"field[{name}]: horizontal is {field['horizontal']}, expected left/center/right.")
    if 'vertical' in field and field['vertical'] not in ('top', 'center', 'bottom'):
        raise RuntimeError(f"field[{name}]: vertical is {field['vertical']}, expected top/center/bottom.")
    if 'type' not in field:
        raise RuntimeError(f'field[{name}]: missing key [type]')
    if field['type'] == 'str':
        if 'default' in field:
            v = field['default']
            if v is not None and not isinstance(v, str):
                raise RuntimeError(f'field[{name}]: default is {type(v)}, expected str.')
    elif field['type'] == 'bool':
        if 'default' in field:
            v = field['default']
            if v is not None and not isinstance(v, bool):
                raise RuntimeError(f'field[{name}]: default is {type(v)}, expected bool.')
    elif field['type'] == 'int':
        if 'default' in field:
            v = field['default']
            if v is not None and not isinstance(v, int):
                raise RuntimeError(f'field[{name}]: default is {type(v)}, expected int.')
    elif field['type'] == 'float':
        if 'default' in field:
            v = field['default']
            if v is not None and not isinstance(v, float):
                raise RuntimeError(f'field[{name}]: default is {type(v)}, expected float.')
    elif field['type'] == 'datetime':
        if 'default' in field:
            v = field['default']
            if v is not None and not isinstance(v, datetime):
                raise RuntimeError(f'field[{name}]: default is {type(v)}, expected datetime.')
    else:
        raise RuntimeError(f"field[{name}]: unsupported type[{field['type']}]")
    if 'input' in field:
        iput = field['input']
        # iput can be None
        if iput and iput not in _inputs:
            raise RuntimeError(f'classes: missing input[{iput}]')
    if 'output' not in field or field['output'] is None:
        raise RuntimeError(f'field[{name}]: missing output')
    oput = field['output']
    if oput not in _outputs:
        raise RuntimeError(f'field[{name}]: missing output[{oput}]')

    return Field(name, **field)


def _init_input(iput):
    if 'class' not in iput:
        raise RuntimeError('input: missing key [class]')
    cls = iput['class']
    iput.pop('class')
    if cls == 'QCheckBox':
        _check_key(iput, cls, {'title': str})
        return InputCheckBox(**iput)
    elif cls == 'QComboBox':
        _check_key(iput, cls, {'editable': bool, 'items': None, })
        if 'items' in iput:
            items = iput['items']
            if isinstance(items, dict):
                _check_key(items, cls, {'class': str, 'ymlfile': str, 'function': str, 'modules': list})
                if 'modules' in items:
                    for mod in items['modules']:
                        if not isinstance(mod, str):
                            raise RuntimeError('input: QComboBox modules must is string list')
                if 'ymlfile' in items:
                    kfname = items['ymlfile']
                    if kfname not in _xmlfiles:
                        with open(os.path.join(conf_dir, kfname), mode='r', encoding="utf-8") as f:
                            _xmlfiles[kfname] = yaml.load(f, Loader=yaml.FullLoader)
            elif isinstance(items, list):
                for it in iput['items']:
                    if not isinstance(it, str):
                        raise RuntimeError('input: QComboBox items must is string list')
            else:
                raise RuntimeError(f'input: QComboBox items unknown type[{type(items)}]')
        return InputComboBox(**iput)
    elif cls == 'QLineEdit':
        _check_key(iput, cls, {'validator': dict})
        if 'validator' in iput:
            validator = iput['validator']
            if 'class' not in validator:
                raise RuntimeError('validator: missing key [class]')
            cls = validator['class']
            if cls == 'inputMask':
                _check_key(validator, cls, {'class': str, 'inputMask': str})
            elif cls == 'QIntValidator':
                _check_key(validator, cls, {'class': str, 'minimum': int, 'maximum': int})
            elif cls == 'QDoubleValidator':
                _check_key(validator, cls,
                           {'class': str, 'bottom': float, 'top': float, 'decimals': int, 'notation': int})
            elif cls == 'QRegExpValidator':
                _check_key(validator, cls, {'class': str, 'pattern': str, 'cs': int, 'syntax': int})
            elif cls == 'QRegularExpressionValidator':
                _check_key(validator, cls, {'class': str, 'pattern': str, 'options': int})
            else:
                raise RuntimeError(f'validator: unknown class [{cls}]')
        return InputLineEdit(**iput)
    elif cls == 'QSpinBox':
        _check_key(iput, cls, {'minimum': int, 'maximum': int, 'step': int, 'intbase': int,
                               'suffix': str, 'prefix': str})
        return InputSpinBox(**iput)
    elif cls == 'QDoubleSpinBox':
        _check_key(iput, cls, {'minimum': float, 'maximum': float, 'step': float, 'decimals': int,
                               'suffix': str, 'prefix': str})
        return InputDoubleSpinBox(**iput)
    elif cls == 'QTimeEdit':
        _check_key(iput, cls, {'displayfmt': str})
        return InputTimeEdit(**iput)
    elif cls == 'QDateEdit':
        _check_key(iput, cls, {'calendar': bool, 'displayfmt': str})
        return InputDateEdit(**iput)
    elif cls == 'QDateTimeEdit':
        _check_key(iput, cls, {'calendar': bool, 'displayfmt': str})
        return InputDateTimeEdit(**iput)
    else:
        raise RuntimeError(f'input: unknown class [{cls}]')


def _init_output(oput):
    if 'class' not in oput:
        raise RuntimeError('output: missing key [class]')
    cls = oput['class']
    oput.pop('class')
    if cls == 'format':
        _check_key(oput, cls, {'format': str})
        return OutputFmt(**oput)
    elif cls == 'lambda':
        _check_key(oput, cls, {'function': str, 'modules': list})
        if 'modules' in oput:
            for mod in oput['modules']:
                if not isinstance(mod, str):
                    raise RuntimeError('output: modules must is string list')
        return OutputFunc(**oput)
    else:
        raise RuntimeError(f'output: unknown class [{cls}]')


def _init_clsdef(cls: str, di: Dict[str, Field]):
    fields = []
    for k in di:
        fobj = di[k]
        if fobj.is_readonly():  # read only field , don't save to db
            continue
        fields.append((k, fobj.ftype, fobj.fdefault))
    return make_dataclass(cls, fields)


def initialize() -> NoReturn:
    with open(member_yml, mode='r', encoding="utf-8") as f:
        memberdi = yaml.load(f, Loader=yaml.FullLoader)
    if 'inputs' in memberdi:
        for k in memberdi['inputs']:
            _inputs[k] = _init_input(memberdi['inputs'][k])
    if 'outputs' in memberdi:
        for k in memberdi['outputs']:
            _outputs[k] = _init_output(memberdi['outputs'][k])
    if 'classes' in memberdi:
        for cls in memberdi['classes']:
            di = memberdi['classes'][cls]
            clsdi = {field: _init_field(field, di[field]) for field in di}
            _classes[cls] = clsdi
            _classdefs[cls] = _init_clsdef(cls, clsdi)
    global _obj
    if 'obj' not in memberdi:
        raise RuntimeError(f'obj: missing key obj')
    objdi = {}
    for name in memberdi['obj']:
        val = memberdi['obj'][name]
        if isinstance(val, dict):
            fobj = _init_field(name, val)
            # if not fobj.is_readonly():
            #     raise RuntimeError(f'obj[{name}]: top field must is readonly')
            objdi[name] = fobj
        elif isinstance(val, list):
            if len(val) > 1:
                raise RuntimeError(f'obj[{name}]: has more than 1 element')
            if val[0] not in _classes:
                raise RuntimeError(f'obj[{name}]: missing class[{val[0]}]')
            objdi[name] = val
        elif isinstance(val, str):
            if val not in _classes:
                raise RuntimeError(f'obj[{name}]: missing class[{val}]')
            objdi[name] = val
        else:
            raise RuntimeError(f'obj[{name}]: unknown type')
    _obj = objdi


def get_flat_top_fields() -> List[Tuple[str, Optional[str], Field]]:
    """
    获取只读的平坦型顶层field列表, 应用在显示视图,及报表上
    :return:
    """
    fields = []
    for k in _obj:
        if isinstance(_obj[k], Field):
            fields.append((k, None, _obj[k]))
        elif isinstance(_obj[k], str):
            cls = _obj[k]
            clsdi = _classes[cls]
            for field in clsdi:
                fields.append((k, field, clsdi[field]))
        else:  # ignored list
            pass
    return fields


def get_group_list_fields() -> Dict[Tuple[str, str], List[Tuple[str, Field]]]:
    """
    获取按属性命分组的field列表, 用于显示视图及报表
    :return:
    """
    groupdi = {}
    for k in _obj:
        if isinstance(_obj[k], list):
            cls = _obj[k][0]
            clsdi = _classes[cls]
            fields = []
            for field in clsdi:
                fields.append((field, clsdi[field]))
            groupdi[(k, cls)] = fields
    return groupdi


def get_write_top_fields() -> List[Tuple[str, Field]]:
    fields = []
    for k in _obj:
        if isinstance(_obj[k], Field):
            fobj = _obj[k]
            if not fobj.is_readonly():
                fields.append((k, fobj))
    return fields


def get_write_group_top_fields() -> Dict[Tuple[str, str], List[Tuple[str, Field]]]:
    groupdi = {}
    for k in _obj:
        if isinstance(_obj[k], str):
            cls = _obj[k]
            clsdi = _classes[cls]
            fields = []
            for field in clsdi:
                fobj = clsdi[field]
                if not fobj.is_readonly():
                    fields.append((field, fobj))
            groupdi[(k, cls)] = fields
    return groupdi


def get_write_group_list_fields() -> Dict[Tuple[str, str], List[Tuple[str, Field]]]:
    groupdi = {}
    for k in _obj:
        if isinstance(_obj[k], list):
            cls = _obj[k][0]
            clsdi = _classes[cls]
            fields = []
            for field in clsdi:
                fobj = clsdi[field]
                if not fobj.is_readonly():
                    fields.append((field, fobj))
            groupdi[(k, cls)] = fields
    return groupdi


def get_class_object(cls):
    return _classdefs[cls]
