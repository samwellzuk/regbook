# -*- coding: utf-8 -*-

import logging
from enum import Enum
import ctypes
import threading

from PyQt5.QtCore import pyqtSignal, QObject
import vlc

from .vfile import VirFileService


class MeidaPlayerState(Enum):
    NothingSpecial = 0
    Opening = 1
    # Buffering = 2  #Deprecated
    Playing = 3
    Paused = 4
    Stopped = 5
    EndReached = 6
    EncounteredError = 7
    Forward = 8
    Backward = 9


class EventTracker(QObject):
    MediaPlayerStateChanged = pyqtSignal(MeidaPlayerState)
    MediaPlayerBuffering = pyqtSignal(float)
    MediaPlayerTimeChanged = pyqtSignal(int)  # libvlc_time_t
    MediaPlayerPositionChanged = pyqtSignal(float)
    MediaPlayerSeekableChanged = pyqtSignal(int)
    MediaPlayerPausableChanged = pyqtSignal(int)
    MediaPlayerTitleChanged = pyqtSignal(int)
    MediaPlayerSnapshotTaken = pyqtSignal(str)
    MediaPlayerLengthChanged = pyqtSignal(int)  # libvlc_time_t
    MediaPlayerVout = pyqtSignal(int)
    MediaPlayerScrambledChanged = pyqtSignal(int)
    # MediaPlayerESAdded = pyqtSignal()
    # MediaPlayerESDeleted = pyqtSignal()
    # MediaPlayerESSelected = pyqtSignal()
    MediaPlayerCorked = pyqtSignal()
    MediaPlayerUncorked = pyqtSignal()
    MediaPlayerMuted = pyqtSignal()
    MediaPlayerUnmuted = pyqtSignal()
    MediaPlayerAudioVolume = pyqtSignal(float)
    # MediaPlayerAudioDevice = pyqtSignal(str)
    # MediaPlayerChapterChanged = pyqtSignal(int)

    StateEvents = {
        vlc.EventType.MediaPlayerNothingSpecial: MeidaPlayerState.NothingSpecial,
        vlc.EventType.MediaPlayerOpening: MeidaPlayerState.Opening,
        vlc.EventType.MediaPlayerPlaying: MeidaPlayerState.Playing,
        vlc.EventType.MediaPlayerPaused: MeidaPlayerState.Paused,
        vlc.EventType.MediaPlayerStopped: MeidaPlayerState.Stopped,
        vlc.EventType.MediaPlayerForward: MeidaPlayerState.Forward,
        vlc.EventType.MediaPlayerBackward: MeidaPlayerState.Backward,
        vlc.EventType.MediaPlayerEndReached: MeidaPlayerState.EndReached,
        vlc.EventType.MediaPlayerEncounteredError: MeidaPlayerState.EncounteredError,
    }
    TrackEvents = [
        vlc.EventType.MediaPlayerNothingSpecial,
        vlc.EventType.MediaPlayerOpening,
        vlc.EventType.MediaPlayerPlaying,
        vlc.EventType.MediaPlayerPaused,
        vlc.EventType.MediaPlayerStopped,
        vlc.EventType.MediaPlayerForward,
        vlc.EventType.MediaPlayerBackward,
        vlc.EventType.MediaPlayerEndReached,
        vlc.EventType.MediaPlayerEncounteredError,
        vlc.EventType.MediaPlayerBuffering,
        vlc.EventType.MediaPlayerTimeChanged,
        vlc.EventType.MediaPlayerPositionChanged,
        vlc.EventType.MediaPlayerSeekableChanged,
        vlc.EventType.MediaPlayerPausableChanged,
        vlc.EventType.MediaPlayerTitleChanged,
        vlc.EventType.MediaPlayerSnapshotTaken,
        vlc.EventType.MediaPlayerLengthChanged,
        vlc.EventType.MediaPlayerVout,
        vlc.EventType.MediaPlayerScrambledChanged,
        vlc.EventType.MediaPlayerCorked,
        vlc.EventType.MediaPlayerUncorked,
        vlc.EventType.MediaPlayerMuted,
        vlc.EventType.MediaPlayerUnmuted,
        vlc.EventType.MediaPlayerAudioVolume,
    ]

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def register(self, mediaplayer):
        eventmgr = mediaplayer.event_manager()
        for env in EventTracker.TrackEvents:
            eventmgr.event_attach(env, self.event_callback)

    def unregister(self, mediaplayer):
        eventmgr = mediaplayer.event_manager()
        for env in EventTracker.TrackEvents:
            eventmgr.event_detach(env)

    def event_callback(self, event):
        if event.type in EventTracker.StateEvents:
            state = EventTracker.StateEvents[event.type]
            self.MediaPlayerStateChanged.emit(state)
            logging.debug('MediaPlayerStateChanged: %s', state.name)
        elif event.type == vlc.EventType.MediaPlayerBuffering:
            self.MediaPlayerBuffering.emit(event.u.new_cache)
            logging.debug('MediaPlayerBuffering: %s', event.u.new_cache)
        elif event.type == vlc.EventType.MediaPlayerTimeChanged:
            self.MediaPlayerTimeChanged.emit(event.u.new_time)
            logging.debug('MediaPlayerTimeChanged: %s', event.u.new_time)
        elif event.type == vlc.EventType.MediaPlayerPositionChanged:
            self.MediaPlayerPositionChanged.emit(event.u.new_position)
            logging.debug('MediaPlayerPositionChanged: %s', event.u.new_position)
        elif event.type == vlc.EventType.MediaPlayerSeekableChanged:
            val = event.u.new_seekable & 0xFFFFFFFF
            self.MediaPlayerSeekableChanged.emit(val)
            logging.debug('MediaPlayerSeekableChanged: %s', val)
        elif event.type == vlc.EventType.MediaPlayerPausableChanged:
            val = event.u.new_pausable & 0xFFFFFFFF
            self.MediaPlayerPausableChanged.emit(val)
            logging.debug('MediaPlayerPausableChanged: %s', val)
        elif event.type == vlc.EventType.MediaPlayerTitleChanged:
            self.MediaPlayerTitleChanged.emit(event.u.new_title)
            logging.debug('MediaPlayerTitleChanged: %s', event.u.new_title)
        elif event.type == vlc.EventType.MediaPlayerSnapshotTaken:
            self.MediaPlayerSnapshotTaken.emit(event.u.psz_filename)
            logging.debug('MediaPlayerSnapshotTaken: %s', event.u.psz_filename)
        elif event.type == vlc.EventType.MediaPlayerLengthChanged:
            self.MediaPlayerLengthChanged.emit(event.u.new_length)
            logging.debug('MediaPlayerLengthChanged: %s', event.u.new_length)
        elif event.type == vlc.EventType.MediaPlayerVout:
            self.MediaPlayerVout.emit(event.u.new_count)
            logging.debug('MediaPlayerVout: %s', event.u.new_count)
        elif event.type == vlc.EventType.MediaPlayerScrambledChanged:
            val = event.u.new_scrambled & 0xFFFFFFFF
            self.MediaPlayerScrambledChanged.emit(val)
            logging.debug('MediaPlayerScrambledChanged: %s', val)
        elif event.type == vlc.EventType.MediaPlayerCorked:
            self.MediaPlayerCorked.emit()
            logging.debug('MediaPlayerCorked')
        elif event.type == vlc.EventType.MediaPlayerUncorked:
            self.MediaPlayerUncorked.emit()
            logging.debug('MediaPlayerUncorked')
        elif event.type == vlc.EventType.MediaPlayerMuted:
            self.MediaPlayerMuted.emit()
            logging.debug('MediaPlayerMuted')
        elif event.type == vlc.EventType.MediaPlayerUnmuted:
            self.MediaPlayerUnmuted.emit()
            logging.debug('MediaPlayerUnmuted')
        elif event.type == vlc.EventType.MediaPlayerAudioVolume:
            # vlc python don't define volume, so use new_position
            self.MediaPlayerAudioVolume.emit(event.u.new_position)
            logging.debug('MediaPlayerAudioVolume: %s', event.u.new_position)
        else:
            logging.debug('Unkonw Event: %s', event.type)


_vfile_svc = VirFileService()
_obj_cache = {}
_obj_lock = threading.Lock()


def cache_object(key: int, *arg):
    with _obj_lock:
        if key in _obj_cache:
            raise RuntimeError(f'cache_object: key duplicate: {key}')
        _obj_cache[key] = arg


def cache_remove(key: int):
    with _obj_lock:
        if key not in _obj_cache:
            raise RuntimeError(f'cache_remove: key not found: {key}')
        del _obj_cache[key]


@vlc.cb.MediaOpenCb
def media_open_cb(opaque, data_pointer, size_pointer):
    try:
        vf = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value
        outf = _vfile_svc.open_file_content(vf)
        p1 = ctypes.py_object(outf)
        p2 = ctypes.pointer(p1)
        p3 = ctypes.cast(p2, ctypes.c_void_p)
        cache_object(id(outf), outf, p1, p2, p3)
        data_pointer.contents.value = p3.value
        size_pointer.contents.value = outf.length
    except Exception as e:
        logging.exception('media_open_cb')
        return -1
    return 0


@vlc.cb.MediaReadCb
def media_read_cb(opaque, buffer, length):
    try:
        outf = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value
        data = outf.read(length)
        sz = len(data)
        ctypes.memmove(buffer, data, sz)
        return sz
    except Exception as e:
        logging.exception('media_read_cb')
        return -1


@vlc.cb.MediaSeekCb
def media_seek_cb(opaque, offset):
    try:
        outf = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value
        outf.seek(offset)
    except Exception as e:
        logging.exception('media_seek_cb')
        return -1
    return 0


@vlc.cb.MediaCloseCb
def media_close_cb(opaque):
    try:
        outf = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value
        outf.close()
        cache_remove(id(outf))
    except Exception as e:
        logging.exception('media_close_cb')
        return
