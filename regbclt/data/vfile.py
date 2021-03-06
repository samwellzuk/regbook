# -*- coding: utf-8 -*-
# Created by samwell
import os
from typing import List, NoReturn, Optional, Dict
from dataclasses import dataclass, asdict, field, InitVar
from hashlib import md5
from datetime import datetime
from bson import ObjectId

from PyQt5.QtCore import QObject, pyqtSignal, QIODevice, QByteArray, QBuffer, Qt
from PyQt5.QtGui import QImage

import gridfs
import pymongo

from .model import Member
from .dbmgr import DBManager
from comm.exiftool import extract_exif
from comm.fileicon import query_file_icon
from comm.vlctool import VlcExtractor

from settings import qt_image_formats, best_thumbnail_width, vlc_video_formats


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


class VirFileService(QObject):
    progressUpdated = pyqtSignal(int)
    progressTxtChanged = pyqtSignal(str)
    progressStepUpdated = pyqtSignal(int)
    progressStepTxtChanged = pyqtSignal(str)
    progressErrChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def upload_files(self, member: Member, fpathlist: List[str]) -> List[VirFile]:
        assert len(fpathlist) != 0
        vfiles = []
        # 1 checking existence of files
        progress = 0
        step_total = 10
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Step[1]: Checking existence of files...')
        self.progressStepUpdated.emit(0)
        for i, fp in enumerate(fpathlist):
            self.progressStepTxtChanged.emit(f'{fp}')
            try:
                if not os.path.isfile(fp):
                    self.progressErrChanged.emit(f'file not exist: {fp}')
                else:
                    vf = VirFile(filename=fp, length=0, chunkSize=0, uploadDate=None, metadata=dict())
                    vfiles.append(vf)
            except Exception as e:
                self.progressErrChanged.emit(f'Step[1]({fp}): {e}')
            self.progressStepUpdated.emit(int(100 * (i + 1) / len(fpathlist)))
            self.progressUpdated.emit(progress + int(step_total * (i + 1) / len(fpathlist)))
        # 2 getting exif information, including thumbnail if it's available
        progress += step_total
        step_total = 10
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Step[2]: Getting exif information of files...')
        self.progressStepUpdated.emit(0)
        vftmps = vfiles
        vfiles = []
        for i, vf in enumerate(vftmps):
            self.progressStepTxtChanged.emit(f'{vf.filename}')
            try:
                exif, img = extract_exif(vf.filename)
                vf.exif = exif
                vf.thumbnail = img
                vfiles.append(vf)
            except Exception as e:
                self.progressErrChanged.emit(f'Step[2]({vf.filename}): {e}')
            self.progressStepUpdated.emit(int(100 * (i + 1) / len(vftmps)))
            self.progressUpdated.emit(progress + int(step_total * (i + 1) / len(vftmps)))
        # 3 getting thumbnail of image which is supported by Qt
        progress += step_total
        step_total = 10
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Step[3]: Getting thumbnail of image...')
        self.progressStepUpdated.emit(0)
        vftmps = vfiles
        vfiles = []
        for i, vf in enumerate(vftmps):
            self.progressStepTxtChanged.emit(f'{vf.filename}')
            if vf.thumbnail is None and vf.file_suffix() in qt_image_formats:
                try:
                    img = QImage(vf.filename)
                    resimg = img.scaled(best_thumbnail_width, best_thumbnail_width,
                                        Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    resarr = QByteArray()
                    resbuf = QBuffer(resarr)
                    resbuf.open(QIODevice.WriteOnly)
                    resimg.save(resbuf, "PNG")  # thumbnail save to png for keeping transparent color
                    vf.thumbnail = resarr.data()
                except Exception as e:
                    self.progressErrChanged.emit(f'Step[3]({vf.filename}): {e}')
            vfiles.append(vf)
            self.progressStepUpdated.emit(int(100 * (i + 1) / len(vftmps)))
            self.progressUpdated.emit(progress + int(step_total * (i + 1) / len(vftmps)))
        # 4 getting thumbnail of video which is supported by vlc
        progress += step_total
        step_total = 10
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Step[4]: Getting thumbnail of video...')
        self.progressStepUpdated.emit(0)
        has_video = False
        for vf in vfiles:
            if vf.file_suffix() in vlc_video_formats:
                has_video = True
                break
        if has_video:
            vlcex = VlcExtractor()
            vftmps = vfiles
            vfiles = []
            for i, vf in enumerate(vftmps):
                self.progressStepTxtChanged.emit(f'{vf.filename}')
                if vf.file_suffix() in vlc_video_formats:
                    try:
                        img = vlcex.take_snapshot(vf.filename.replace('/', '\\'))
                        vf.thumbnail = img
                    except Exception as e:
                        self.progressErrChanged.emit(f'Step[4]({vf.filename}): {e}')
                vfiles.append(vf)
                self.progressStepUpdated.emit(int(100 * (i + 1) / len(vftmps)))
                self.progressUpdated.emit(progress + int(step_total * (i + 1) / len(vftmps)))
        # 5 uploading files to mongodb, get VirFile
        progress += step_total
        step_total = 50
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Step[5]: Uploading files...')
        vftmps = vfiles
        vfiles = []
        dbmgr = DBManager()
        dbfs = gridfs.GridFS(dbmgr.get_db(), disable_md5=True)
        for i, vf in enumerate(vftmps):
            self.progressStepTxtChanged.emit(f'{vf.filename}')
            self.progressStepUpdated.emit(0)
            dstf = None
            try:
                metadata = {
                    'owner_id': member._id,
                    'upload_user': dbmgr.cur_user.user,
                    'exif': vf.exif,
                    'thumbnail': vf.thumbnail
                }
                dstf = dbfs.new_file(filename=os.path.basename(vf.filename), metadata=metadata)
                totalsz = os.stat(vf.filename).st_size
                chunksz = dstf.chunk_size
                curpos = 0
                m = md5()
                with open(vf.filename, 'rb') as srcf:
                    while data := srcf.read(chunksz):
                        dstf.write(data)
                        m.update(data)
                        curpos += len(data)
                        self.progressStepUpdated.emit(int(100 * curpos / totalsz))
                # before close, save md5
                dstf.metadata['md5'] = m.hexdigest()
                dstf.close()
                # save information
                vf._id = dstf._id
                vf.filename = dstf.filename
                vf.length = dstf.length
                vf.chunkSize = dstf.chunk_size
                vf.uploadDate = dstf.upload_date
                vf.md5 = dstf.metadata['md5']
                vf.owner_id = dstf.metadata['owner_id']
                vf.upload_user = dstf.metadata['upload_user']
                vfiles.append(vf)
            except Exception as e:
                if dstf:
                    dstf.abort()
                self.progressErrChanged.emit(f'Step[5]({vf.filename}): {e}')
            self.progressStepUpdated.emit(100)
            self.progressUpdated.emit(progress + int(step_total * (i + 1) / len(vftmps)))
        # 6 getting icon by file extension
        progress += step_total
        step_total = 10
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Step[6]: Getting icon by file extension...')
        self.progressStepUpdated.emit(0)
        for i, vf in enumerate(vfiles):
            self.progressStepTxtChanged.emit(f'{vf.filename}')
            try:
                if not vf.thumbnail:
                    if suffix := vf.file_suffix():
                        query_file_icon(suffix)
            except Exception as e:
                self.progressErrChanged.emit(f'Step[6]({vf.filename}): {e}')
            self.progressStepUpdated.emit(int(100 * (i + 1) / len(vfiles)))
            self.progressUpdated.emit(progress + int(step_total * (i + 1) / len(vfiles)))
        # finished
        progress += step_total
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Finished')
        return vfiles

    def download_files(self, vfiles: List[VirFile], targetdir: str) -> NoReturn:
        assert len(vfiles) != 0
        # 1 checking existence of files
        progress = 0
        step_total = 100
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Downloading files...')
        dbfs = gridfs.GridFS(DBManager().get_db(), disable_md5=True)
        for i, vf in enumerate(vfiles):
            self.progressStepTxtChanged.emit(f'{vf.filename}')
            self.progressStepUpdated.emit(0)
            try:
                fp = os.path.join(targetdir, vf.filename)
                fpindex = 0
                while os.path.exists(fp):
                    fparts = vf.filename.split('.')
                    fparts.insert(-1, f'{fpindex}')
                    fp = os.path.join(targetdir, '.'.join(fparts))
                srcf = dbfs.get(vf._id)
                totalsz = srcf.length
                chunksz = srcf.chunk_size
                curpos = 0
                with open(fp, 'wb') as dstf:
                    while data := srcf.read(chunksz):
                        dstf.write(data)
                        curpos += len(data)
                        self.progressStepUpdated.emit(int(100 * curpos / totalsz))
            except Exception as e:
                self.progressErrChanged.emit(f'{vf.filename}: {e}')
            self.progressStepUpdated.emit(100)
            self.progressUpdated.emit(progress + int(step_total * (i + 1) / len(vfiles)))
        progress += step_total
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Finished')
        return

    def delete_files(self, vfiles: List[VirFile]) -> NoReturn:
        assert len(vfiles) != 0
        progress = 0
        step_total = 100
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Deleting files...')
        dbfs = gridfs.GridFS(DBManager().get_db(), disable_md5=True)
        for i, vf in enumerate(vfiles):
            self.progressStepTxtChanged.emit(f'{vf.filename}')
            self.progressStepUpdated.emit(0)
            try:
                dbfs.delete(vf._id)
            except Exception as e:
                self.progressErrChanged.emit(f'{vf.filename}: {e}')
            self.progressStepUpdated.emit(100)
            self.progressUpdated.emit(progress + int(step_total * (i + 1) / len(vfiles)))
        progress += step_total
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Finished')
        return

    def get_member_files(self, member: Member) -> List[VirFile]:
        vfiles = []
        # 1 checking existence of files
        progress = 0
        step_total = 50
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Step[1]: Querying files...')
        self.progressStepUpdated.emit(0)
        try:
            coll = DBManager().get_db().get_collection('fs.files')
            total = coll.count_documents({"metadata.owner_id": member._id})
            index = 0
            for outf in coll.find({"metadata.owner_id": member._id}, sort=[('uploadDate', pymongo.DESCENDING)]):
                vf = VirFile(**outf)
                vfiles.append(vf)
                self.progressStepUpdated.emit(int(100 * (index + 1) / total))
                self.progressUpdated.emit(progress + int(step_total * (index + 1) / total))
                index += 1
        except Exception as e:
            self.progressErrChanged.emit(f'Step[1] Query: {e}')
        # 2 getting icon by file extension
        progress += step_total
        step_total = 50
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Step[2]: Getting icon by file extension...')
        self.progressStepUpdated.emit(0)
        for i, vf in enumerate(vfiles):
            self.progressStepTxtChanged.emit(f'{vf.filename}')
            try:
                if not vf.thumbnail:
                    if suffix := vf.file_suffix():
                        query_file_icon(suffix)
            except Exception as e:
                self.progressErrChanged.emit(f'Step[2]({vf.filename}): {e}')
            self.progressStepUpdated.emit(int(100 * (i + 1) / len(vfiles)))
            self.progressUpdated.emit(progress + int(step_total * (i + 1) / len(vfiles)))
        # finished
        progress += step_total
        self.progressUpdated.emit(progress)
        self.progressTxtChanged.emit('Finished')
        return vfiles

    def open_file_content(self, vf: VirFile) -> gridfs.GridOut:
        dbfs = gridfs.GridFS(DBManager().get_db(), disable_md5=True)
        outf = dbfs.get(vf._id)
        return outf

    def update_file_thumbnail(self, vfile: VirFile, thumbnail: bytes) -> VirFile:
        self.progressUpdated.emit(0)
        self.progressTxtChanged.emit('Updating file thumbnail...')
        coll = DBManager().get_db().get_collection('fs.files')
        result = coll.update_one({'_id': vfile._id}, {'$set': {'metadata.thumbnail': thumbnail}})
        if result.modified_count != 1:
            raise RuntimeError(f'Update Error: modified_count {result.modified_count}')
        vfile.thumbnail = thumbnail
        self.progressUpdated.emit(100)
        self.progressTxtChanged.emit('Finished')
        return vfile
