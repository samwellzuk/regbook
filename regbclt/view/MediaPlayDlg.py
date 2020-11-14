# -*- coding: utf-8 -*-

"""
Module implementing ChangePwdDlg.
"""
import logging
import time
import datetime
from enum import Enum
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer, QObject
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPalette, QColor

import vlc
from comm.utility import except_check

from .ui_MediaPlayDlg import Ui_MediaPlayDlg


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
        self.open_video(vfile)

    def open_video(self, vf):
        self.setWindowTitle(f'{vf.filename} - Vlc Media Player')
        media = self.mediaplayer.set_mrl(r'C:\Users\atten\Desktop\Photo\103APPLE\IMG_3606.MOV')
        media.release()
        self.mediaplayer.play()

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
        if val > 0:
            if val > 100:
                val = 100
            self.volumeLabel.setText(f'{val}')

            self.voiceButton.blockSignals(True)
            self.voiceButton.setChecked(False)
            self.voiceButton.blockSignals(False)

            self.volumeSlider.setEnabled(True)
            self.volumeSlider.blockSignals(True)
            self.volumeSlider.setValue(val)
            self.volumeSlider.blockSignals(False)
        else:
            self.voiceButton.blockSignals(True)
            self.voiceButton.setChecked(True)
            self.voiceButton.blockSignals(False)

            self.volumeSlider.setEnabled(False)

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

    def done(self, a0: int) -> None:
        super(MediaPlayDlg, self).done(a0)
        if self.mediaplayer.is_playing():
            self.mediaplayer.stop()
            while self.mediaplayer.is_playing():
                time.sleep(0.1)
        self.evtracker.unregister(self.mediaplayer)
        self.mediaplayer.release()

    @pyqtSlot()
    @except_check
    def on_playButton_clicked(self):
        self.mediaplayer.play()

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
        self.mediaplayer.set_position(position/1000.0)

    @pyqtSlot(int)
    @except_check
    def on_volumeSlider_valueChanged(self, position):
        self.mediaplayer.audio_set_volume(position)
