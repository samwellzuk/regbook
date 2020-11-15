# -*- coding: utf-8 -*-

"""
Module implementing ChangePwdDlg.
"""
import time
import datetime
import ctypes
import copy

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QCloseEvent, QPainter, QColor, QPen

import vlc
from comm.utility import except_check
from data.mplayer import EventTracker, MeidaPlayerState, media_open_cb, media_read_cb, media_seek_cb, media_close_cb, \
    cache_object, cache_remove

from .ui_MediaPlayDlg import Ui_MediaPlayDlg


class MediaPlayDlg(QDialog, Ui_MediaPlayDlg):
    """
    Class documentation goes here.
    """

    def __init__(self, vfile, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(MediaPlayDlg, self).__init__(parent)
        self.setupUi(self)
        self.vf = copy.copy(vfile)  # make a new id by copy
        p1 = ctypes.py_object(self.vf)
        p2 = ctypes.pointer(p1)
        p3 = ctypes.cast(p2, ctypes.c_void_p)
        cache_object(id(self.vf), p1, p2, p3)
        self.vf_pointer = p3

        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.mediaplayer.set_hwnd(self.videoWidget.winId())

        self.evtracker = EventTracker(parent=self)
        self.evtracker.register(self.mediaplayer)

        self.evtracker.MediaPlayerStateChanged.connect(self.state_change)
        self.evtracker.MediaPlayerSeekableChanged.connect(self.seekable_change)
        self.evtracker.MediaPlayerPausableChanged.connect(self.pausable_change)
        self.evtracker.MediaPlayerLengthChanged.connect(self.total_time_change)
        self.evtracker.MediaPlayerTimeChanged.connect(self.current_time_change)
        self.evtracker.MediaPlayerAudioVolume.connect(self.volume_change)
        self.evtracker.MediaPlayerPositionChanged.connect(self.position_change)
        self.evtracker.MediaPlayerMuted.connect(self.muted_change)
        self.evtracker.MediaPlayerUnmuted.connect(self.unmuted_change)

        self.meida_pausable = True
        self.setWindowTitle(f'{vfile.filename} - Vlc Media Player')
        self.open_video()

    def __del__(self):
        cache_remove(id(self.vf))

    def open_video(self):
        media = self.instance.media_new_callbacks(
            media_open_cb, media_read_cb, media_seek_cb, media_close_cb,
            self.vf_pointer
        )
        self.mediaplayer.set_media(media)
        media.release()
        self.mediaplayer.play()

    def _do_clear(self):
        if self.mediaplayer:
            if self.mediaplayer.is_playing():
                self.mediaplayer.stop()
                while self.mediaplayer.is_playing():
                    time.sleep(0.1)
            self.evtracker.unregister(self.mediaplayer)
            self.mediaplayer.release()
            self.evtracker = None
            self.mediaplayer = None

    def done(self, a0: int) -> None:
        super(MediaPlayDlg, self).done(a0)
        self._do_clear()

    def closeEvent(self, a0: QCloseEvent) -> None:
        super(MediaPlayDlg, self).closeEvent(a0)
        self._do_clear()

    @pyqtSlot(MeidaPlayerState)
    @except_check
    def state_change(self, state):
        if state == MeidaPlayerState.Opening:
            self.playButton.setEnabled(True)
            self.pauseButton.setEnabled(False)
            self.stopButton.setEnabled(False)
        elif state == MeidaPlayerState.Playing:
            self.playButton.setEnabled(False)
            self.pauseButton.setEnabled(self.meida_pausable)
            self.stopButton.setEnabled(True)
        elif state == MeidaPlayerState.Paused:
            self.playButton.setEnabled(True)
            self.pauseButton.setEnabled(False)
            self.stopButton.setEnabled(True)
        elif state == MeidaPlayerState.Stopped:
            self.playButton.setEnabled(True)
            self.pauseButton.setEnabled(False)
            self.stopButton.setEnabled(False)

    @pyqtSlot(int)
    @except_check
    def seekable_change(self, seekable):
        self.positionSlider.setEnabled((seekable == 1))

    @pyqtSlot(int)
    @except_check
    def pausable_change(self, pausable):
        self.meida_pausable = pausable == 1
        self.pauseButton.setEnabled(self.meida_pausable)

    def _get_time(self, microseconds):
        hour = microseconds // (60 * 60 * 1000)
        val = microseconds % (60 * 60 * 1000)
        minute = val // (60 * 1000)
        val = val % (60 * 1000)
        second = val // 1000
        microsecond = val % 1000
        return datetime.time(hour=hour, minute=minute, second=second, microsecond=microsecond)

    @pyqtSlot(int)
    @except_check
    def total_time_change(self, microseconds):
        total = self._get_time(microseconds)
        self.totaltimeLabel.setText(total.strftime('%H:%M:%S'))

    @pyqtSlot(int)
    @except_check
    def current_time_change(self, microseconds):
        cur = self._get_time(microseconds)
        self.curtimeLabel.setText(cur.strftime('%H:%M:%S'))

    @pyqtSlot()
    @except_check
    def muted_change(self):
        self.voiceButton.blockSignals(True)
        self.voiceButton.setChecked(True)
        self.voiceButton.blockSignals(False)
        self.volumeSlider.setEnabled(False)

    @pyqtSlot()
    @except_check
    def unmuted_change(self):
        self.voiceButton.blockSignals(True)
        self.voiceButton.setChecked(False)
        self.voiceButton.blockSignals(False)
        self.volumeSlider.setEnabled(True)

    @pyqtSlot(float)
    @except_check
    def volume_change(self, volume):
        val = int(volume * 100)
        if val > 0:  # when finished , volume set to -1.0
            if val > 100:
                val = 100
            self.volumeLabel.setText(f'{val}')
            self.volumeSlider.blockSignals(True)
            self.volumeSlider.setValue(val)
            self.volumeSlider.blockSignals(False)

    @pyqtSlot(float)
    @except_check
    def position_change(self, pos):
        val = int(pos * 1000)
        if val > 0:
            self.positionSlider.blockSignals(True)
            self.positionSlider.setValue(val if val <= 1000 else 1000)
            self.positionSlider.blockSignals(False)
        else:
            self.positionSlider.setEnabled(False)

    @pyqtSlot()
    @except_check
    def on_playButton_clicked(self):
        if self.mediaplayer.will_play():
            self.mediaplayer.play()
        else:
            self.open_video()

    @pyqtSlot()
    @except_check
    def on_pauseButton_clicked(self):
        self.mediaplayer.pause()

    @pyqtSlot()
    @except_check
    def on_stopButton_clicked(self):
        self.mediaplayer.stop()

    @pyqtSlot(bool)
    @except_check
    def on_voiceButton_toggled(self, checked):
        self.mediaplayer.audio_set_mute(checked)

    @pyqtSlot(int)
    @except_check
    def on_positionSlider_valueChanged(self, position):
        self.mediaplayer.set_position(position / 1000.0)

    @pyqtSlot(int)
    @except_check
    def on_volumeSlider_valueChanged(self, position):
        self.mediaplayer.audio_set_volume(position)
