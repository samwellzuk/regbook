# -*-coding: utf-8 -*-
# Created by samwell
from typing import List, Optional, NoReturn
import struct
import pefile


class ExtractIcon(object):
    GRPICONDIRENTRY_format = ('GRPICONDIRENTRY',
                              ('B,Width', 'B,Height', 'B,ColorCount', 'B,Reserved',
                               'H,Planes', 'H,BitCount', 'I,BytesInRes', 'H,ID'))
    GRPICONDIR_format = ('GRPICONDIR',
                         ('H,Reserved', 'H,Type', 'H,Count'))
    RES_ICON = 1
    RES_CURSOR = 2

    def __init__(self, filep: str):
        self.pe = pefile.PE(filep)

    def find_dir_bytype(self, restype):
        if restype not in pefile.RESOURCE_TYPE:
            raise RuntimeError('Resource type error!')
        resindex = pefile.RESOURCE_TYPE[restype]
        try:
            rt_base_idx = [entry.id for entry in self.pe.DIRECTORY_ENTRY_RESOURCE.entries].index(resindex)
        except ValueError or AttributeError:
            raise RuntimeError("Can't find resource directory")
        return self.pe.DIRECTORY_ENTRY_RESOURCE.entries[rt_base_idx]

    def get_resource_byid(self, resdir, resindex):
        if resindex < 0:
            try:
                idx = [entry.id for entry in resdir.directory.entries].index(-resindex)
            except ValueError:
                raise RuntimeError("Can't find resource by id")
        else:
            if resindex >= len(resdir.directory.entries):
                raise RuntimeError("Resource Id out of range")
            idx = resindex

        test_res_dir = resdir.directory.entries[idx]
        if test_res_dir.struct.DataIsDirectory:
            # another Directory
            # probably language take the first one
            res_dir = test_res_dir.directory.entries[0]
        else:
            res_dir = test_res_dir

        if res_dir.struct.DataIsDirectory:
            # Ooooooooooiconoo no !! another Directory !!!
            raise RuntimeError('Too many nest directory in resource')
        return res_dir

    def get_icon(self, resindex):
        resdir = self.find_dir_bytype('RT_ICON')
        icon_entry = self.get_resource_byid(resdir, -resindex)

        data_rva = icon_entry.data.struct.OffsetToData
        size = icon_entry.data.struct.Size
        data = self.pe.get_memory_mapped_image()[data_rva:data_rva + size]

        return data

    def get_group_icons(self, resindex):
        resdir = self.find_dir_bytype('RT_GROUP_ICON')

        grp_icon_dir_entry = self.get_resource_byid(resdir, resindex)

        data_rva = grp_icon_dir_entry.data.struct.OffsetToData
        size = grp_icon_dir_entry.data.struct.Size
        data = self.pe.get_memory_mapped_image()[data_rva:data_rva + size]
        file_offset = self.pe.get_offset_from_rva(data_rva)

        grp_icon_dir = pefile.Structure(self.GRPICONDIR_format, file_offset=file_offset)
        grp_icon_dir.__unpack__(data)

        assert grp_icon_dir.Reserved == 0 or grp_icon_dir.Type == self.RES_ICON

        offset = grp_icon_dir.sizeof()

        grp_icons = []
        for idx in range(0, grp_icon_dir.Count):
            grp_icon = pefile.Structure(self.GRPICONDIRENTRY_format, file_offset=file_offset + offset)
            grp_icon.__unpack__(data[offset:])
            offset += grp_icon.sizeof()
            grp_icons.append(grp_icon)
        return grp_icons

    def export_ico(self, grp_icons, index=None):
        """
        export icon form group icons,
        output format is .ico
        """
        if index is not None:
            grp_icons = grp_icons[index:index + 1]

        ico = struct.pack('<HHH', 0, self.RES_ICON, len(grp_icons))
        data_offset = None
        data = []
        info = []
        for grp_icon in grp_icons:
            if data_offset is None:
                data_offset = len(ico) + ((grp_icon.sizeof() + 2) * len(grp_icons))

            nfo = grp_icon.__pack__()[:-2] + struct.pack('<L', data_offset)
            info.append(nfo)

            raw_data = self.get_icon(grp_icon.ID)
            if not raw_data:
                continue

            data.append(raw_data)
            data_offset += len(raw_data)

        icodata = ico + b''.join(info + data)
        return icodata

    def best_icon(self, groups, best_width=None):
        windexs = {}
        for i in range(len(groups)):
            icon = groups[i]
            if icon.Width in windexs:
                windexs[icon.Width][icon.BitCount] = i
            else:
                windexs[icon.Width] = {icon.BitCount: i}
        if best_width and best_width in windexs:
            bitdict = windexs[best_width]
            bitkeys = sorted(bitdict)
            return bitdict[bitkeys[-1]]
        wkeys = sorted(windexs)
        # width big than 255, set to zero
        selk = 0 if 0 in wkeys else wkeys[-1]
        bitdict = windexs[selk]
        bitkeys = sorted(bitdict)
        return bitdict[bitkeys[-1]]


def extract(filepath: str, index: int, bestwidth: int = None) -> bytes:
    extractor = ExtractIcon(filepath)
    groups = extractor.get_group_icons(index)
    bestid = extractor.best_icon(groups, bestwidth)
    data = extractor.export_ico(groups, bestid)
    return data


if __name__ == '__main__':
    import sys
    from PyQt5.QtGui import QPixmap
    from PyQt5.QtWidgets import QApplication, QLabel

    filepath = 'D:\\Qt\\Tools\\QtCreator\\bin\\qtcreator.exe'
    extractor = ExtractIcon(filepath)
    groups = extractor.get_group_icons(3)
    data = extractor.export_ico(groups, extractor.best_icon(groups, 128))

    app = QApplication(sys.argv)
    img = QPixmap()
    if not img.loadFromData(data):
        raise RuntimeError('Error load')
    wnd = QLabel()
    wnd.move(100, 100)
    wnd.setPixmap(img)
    wnd.show()
    app.exec()
