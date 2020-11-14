# -*-coding: utf-8 -*-
# Created by samwell
import os
import time
from tempfile import mkstemp
from threading import Condition
from settings import best_thumbnail_width, tmp_dir
import vlc

_snapshot_type = 'png'
_snapshot_position = 0.1


class event_sync(object):
    def __init__(self):
        self.cv = Condition()
        self.is_finish = False

    def call_back(self, ev):
        with self.cv:
            if ev.type == vlc.EventType.MediaPlayerPositionChanged:
                if ev.u.new_position > _snapshot_position * 0.9:  # 90 % margin
                    self.is_finish = True
                    self.cv.notify()
            elif ev.type == vlc.EventType.MediaPlayerSnapshotTaken:
                self.is_finish = True
                self.cv.notify()

    def event_wait(self):
        with self.cv:
            while not self.is_finish:
                self.cv.wait()


class VlcExtractor(object):
    def __init__(self):
        args = [
            '--intf=dummy',  # no interface
            '--vout=dummy',  # we don't want video (output)
            '--no-audio',  # we don't want audio (decoding)
            '--no-video-title-show',  # nor the filename displayed
            '--no-snapshot-preview',  # no blending in dummy vout
            '--no-sub-autodetect-file',  # we don't want subtitles
            '--no-disable-screensaver',  # we don't want interfaces
            '--no-interact',  # 启用时，界面将会在每次需要用户输入时显示一个对话框。
            '--no-stats',  # no stats
            f'--snapshot-format={_snapshot_type}',
            # '--verbose=1',  # 详尽程度等级 (0=仅错误和标准消息、1=警告、2=调试)。
        ]
        self.instance = vlc.Instance(*args)

    def __del__(self):
        self.instance.release()

    def _set_position(self, mplayer):
        osync = event_sync()
        eventmgr = mplayer.event_manager()
        eventmgr.event_attach(vlc.EventType.MediaPlayerPositionChanged, osync.call_back)
        mplayer.set_position(_snapshot_position)
        osync.event_wait()
        eventmgr.event_detach(vlc.EventType.MediaPlayerPositionChanged)

    def _take_snapshot(self, mplayer, fpath, width, height):
        osync = event_sync()
        eventmgr = mplayer.event_manager()
        eventmgr.event_attach(vlc.EventType.MediaPlayerSnapshotTaken, osync.call_back)
        r = mplayer.video_take_snapshot(0, fpath, width, height)
        if r == 0:
            osync.event_wait()
        eventmgr.event_detach(vlc.EventType.MediaPlayerSnapshotTaken)
        return r == 0

    def take_snapshot(self, filepath: str) -> bytes:
        tmpf, tmpfname = mkstemp(suffix=f'.{_snapshot_type}', dir=tmp_dir)
        os.close(tmpf)
        media = None
        mplayer = None
        img = None
        try:
            media = self.instance.media_new_path(filepath)
            if media is None:
                raise RuntimeError(f'Vlc: Open failed: {filepath}')
            mplayer = media.player_new_from_media()
            if mplayer is None:
                raise RuntimeError(f"Vlc: can't get media player: {filepath}")
            mplayer.play()
            self._set_position(mplayer)
            width, height = mplayer.video_get_size()
            if width > height:
                bestw = best_thumbnail_width
                besth = 0
            else:
                bestw = 0
                besth = best_thumbnail_width
            if self._take_snapshot(mplayer, tmpfname, bestw, besth):
                with open(tmpfname, 'rb') as of:
                    img = of.read()
            mplayer.stop()
        finally:
            if mplayer:
                mplayer.release()
            if media:
                media.release()
            if tmpfname:
                os.remove(tmpfname)
        return img
