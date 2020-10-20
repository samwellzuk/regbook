# -*-coding: utf-8 -*-
# Created by samwell
import os
import time
from functools import partial

from PyQt5.QtCore import Qt, QUrl, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QTabBar, QMessageBox, QProgressDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent

from tts import tts_languages, trans_tts
from di.cambridge import CambridgeUK, CambridgeUS
from model import DictWord
from settings import data_dir

from .ui_mainwindow import Ui_MainWindow
from .asynctask import coroutine, AsyncTask
from .utility import except_check


class Ui_MainWindow_Ex(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        # chrome init
        self.qwebView = QWebEngineView(self.groupBox_4)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qwebView.sizePolicy().hasHeightForWidth())
        self.qwebView.setSizePolicy(sizePolicy)
        self.qwebView.setObjectName("qwebView")
        self.verticalLayout_8.addWidget(self.qwebView)
        # tabbar init
        self.tabBar = QTabBar(self.groupBox_6)
        self.tabBar.setObjectName("tabBar")
        self.verticalLayout_5.insertWidget(1, self.tabBar)


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.curDictWord = None
        self.curWord = None
        self.curDictWordChange = False
        self.curDictWordLock = False

        self.ui = Ui_MainWindow_Ex()
        self.ui.setupUi(self)

        # hide progress bar
        self.ui.groupBox_5.setVisible(False)
        self.ui.groupBox_7.setVisible(False)

        # ---------------------------------
        # init dictionary
        self.dictionaries = [CambridgeUS(), CambridgeUK()]
        for obj in self.dictionaries:
            self.ui.dictBox.addItem(obj.displayname)
        self.ui.dictBox.currentIndexChanged.connect(self._dictionary_change)

        # connection
        self.ui.qwebView.loadStarted.connect(self._load_started)
        self.ui.qwebView.loadProgress.connect(self._load_progress)
        self.ui.qwebView.loadFinished.connect(self._load_finished)

        self.ui.refresh.clicked.connect(self._refresh_webview)
        self.ui.dictMktts.clicked.connect(self._refresh_mktts)
        # select dict
        self.ui.dictBox.setCurrentIndex(0)
        self._dictionary_change(0)

        # ---------------------------------
        # media play
        self.titlePlayer = QMediaPlayer(self)
        self.titlePlayer.stateChanged.connect(self._titleStateChanged)
        self.ui.titlePlay.clicked.connect(self._titlePlay)
        self.ui.titleStop.clicked.connect(self._titleStop)
        self.ui.titleMktts.clicked.connect(self._titleMktts)
        self.ui.titleEdit.textChanged.connect(self._titleTextChanged)

        self.contentPlayer = QMediaPlayer(self)
        self.contentPlayer.stateChanged.connect(self._contentStateChanged)
        self.ui.contentPlay.clicked.connect(self._contentPlay)
        self.ui.contentStop.clicked.connect(self._contentStop)
        self.ui.contentMktts.clicked.connect(self._contentMktts)
        self.ui.contentEdit.textChanged.connect(self._contentTextChanged)

        self.ui.tabBar.currentChanged.connect(self._tarbarChanged)
        self.update_dictword(None)

    def save_dictword_change(self):
        if self.curDictWordChange and self.curDictWord:
            self.curDictWord.save()

    def stop_voice_play(self):
        if self.titlePlayer.state() == QMediaPlayer.PlayingState:
            self.titlePlayer.stop()
            self.titlePlayer.setPlaylist(None)
        if self.contentPlayer.state() == QMediaPlayer.PlayingState:
            self.contentPlayer.stop()
            self.contentPlayer.setPlaylist(None)

    def update_dictword(self, dictwordobj):
        # if busy to mktts , don't update to cur dictword
        if self.curDictWordLock:
            return

        self.save_dictword_change()

        self.stop_voice_play()
        self.curDictWord = None
        self.curWord = None
        for i in range(self.ui.tabBar.count() - 1, -1, -1):
            self.ui.tabBar.removeTab(i)

        if dictwordobj is None:
            self.ui.queryword.setText('')
            self.ui.titleEdit.setPlainText('')
            self.ui.contentEdit.setPlainText('')
            self.ui.tabBar.setVisible(False)
            self.ui.titleEdit.setEnabled(False)
            self.ui.titlePlay.setEnabled(False)
            self.ui.titleStop.setEnabled(False)
            self.ui.titleMktts.setEnabled(False)
            self.ui.contentEdit.setEnabled(False)
            self.ui.contentPlay.setEnabled(False)
            self.ui.contentStop.setEnabled(False)
            self.ui.contentMktts.setEnabled(False)
        else:
            if len(dictwordobj.words) > 1:
                for w in dictwordobj.words:
                    self.ui.tabBar.addTab(w.name)
                self.ui.tabBar.setCurrentIndex(0)
                self.ui.tabBar.setVisible(True)
            else:
                self.ui.tabBar.setVisible(False)
            self.curDictWord = dictwordobj
            self.curWord = dictwordobj.words[0]
            self.ui.queryword.setText(self.curDictWord.query_word)
            self.ui.titleEdit.setPlainText(self.curWord.title_text)
            self.ui.contentEdit.setPlainText(self.curWord.content_text)
            self.ui.titleEdit.setEnabled(True)
            self.ui.titleMktts.setEnabled(True)
            self.ui.titlePlay.setEnabled(True)
            self.ui.titleStop.setEnabled(False)
            self.ui.contentEdit.setEnabled(True)
            self.ui.contentMktts.setEnabled(True)
            self.ui.contentPlay.setEnabled(True)
            self.ui.contentStop.setEnabled(False)

    @pyqtSlot(int)
    def _tarbarChanged(self, index):
        if self.curDictWord is None:
            return
        self.stop_voice_play()
        self.curWord = self.curDictWord.words[index]
        self.ui.titleEdit.setPlainText(self.curWord.title_text)
        self.ui.contentEdit.setPlainText(self.curWord.content_text)

        self.ui.titleEdit.setEnabled(True)
        self.ui.titleMktts.setEnabled(True)
        self.ui.titlePlay.setEnabled(True)
        self.ui.titleStop.setEnabled(False)
        self.ui.contentEdit.setEnabled(True)
        self.ui.contentMktts.setEnabled(True)
        self.ui.contentPlay.setEnabled(True)
        self.ui.contentStop.setEnabled(False)

    @pyqtSlot()
    def _titleTextChanged(self):
        if self.curDictWord is None:
            return
        txt = self.ui.titleEdit.toPlainText()
        self.curWord.title_text = txt
        self.curDictWordChange = True

    @pyqtSlot(bool)
    def _titlePlay(self, checked):
        if self.curDictWord is None:
            return
        self.stop_voice_play()
        if self.curWord.title_voices:
            mp3list = [os.path.join(self.curDictWord.data_path, fname) for fname in self.curWord.title_voices]
            playlist = QMediaPlaylist(self)
            for fmp3 in mp3list:
                playlist.addMedia(QUrl.fromLocalFile(fmp3))
            self.titlePlayer.setPlaylist(playlist)
            self.titlePlayer.play()

    @pyqtSlot(bool)
    def _titleStop(self, checked):
        self.stop_voice_play()

    @pyqtSlot(bool)
    def _titleMktts(self, checked):
        if self.curDictWord is None:
            return
        self.stop_voice_play()
        self.mk_voice(True)

    @pyqtSlot()
    def _contentTextChanged(self):
        if self.curDictWord is None:
            return
        txt = self.ui.contentEdit.toPlainText()
        self.curWord.content_text = txt
        self.curDictWordChange = True

    @pyqtSlot(bool)
    def _contentPlay(self, checked):
        if self.curDictWord is None:
            return
        self.stop_voice_play()
        if self.curWord.content_voices:
            mp3list = [os.path.join(self.curDictWord.data_path, fname) for fname in self.curWord.content_voices]
            playlist = QMediaPlaylist(self)
            for fmp3 in mp3list:
                playlist.addMedia(QUrl.fromLocalFile(fmp3))
            self.titlePlayer.setPlaylist(playlist)
            self.titlePlayer.play()

    @pyqtSlot(bool)
    def _contentStop(self, checked):
        self.stop_voice_play()

    @pyqtSlot(bool)
    def _contentMktts(self, checked):
        if self.curDictWord is None:
            return
        self.stop_voice_play()
        self.mk_voice(False)

    @pyqtSlot(QMediaPlayer.State)
    def _titleStateChanged(self, status):
        if status == QMediaPlayer.PlayingState:
            self.ui.titlePlay.setEnabled(False)
            self.ui.titleStop.setEnabled(True)
        else:
            self.ui.titlePlay.setEnabled(True)
            self.ui.titleStop.setEnabled(False)

    @pyqtSlot(QMediaPlayer.State)
    def _contentStateChanged(self, status):
        if status == QMediaPlayer.PlayingState:
            self.ui.contentPlay.setEnabled(False)
            self.ui.contentStop.setEnabled(True)
        else:
            self.ui.contentPlay.setEnabled(True)
            self.ui.contentStop.setEnabled(False)

    @pyqtSlot(int)
    def _dictionary_change(self, index):
        diobj = self.dictionaries[index]
        self.ui.accentBox.clear()

        lang = diobj.language
        default_ttslang = diobj.default_ttslang
        for k, v in tts_languages:
            if k.startswith(lang):
                self.ui.accentBox.addItem(v, k)
        for i in range(self.ui.accentBox.count()):
            k = self.ui.accentBox.itemData(i)
            if k == default_ttslang:
                self.ui.accentBox.setCurrentIndex(i)
                break
        else:
            self.ui.accentBox.setCurrentIndex(0)
        self.ui.qwebView.load(QUrl(diobj.home))

    @pyqtSlot(bool)
    def _refresh_webview(self, checked):
        self.ui.qwebView.reload()

    @pyqtSlot(bool)
    def _refresh_mktts(self, checked):
        url = self.ui.qwebView.page().url()
        index = self.ui.dictBox.currentIndex()
        diobj = self.dictionaries[index]
        qok, qword = diobj.check_url(url)
        if qok:
            tts_lang = self.ui.accentBox.currentData()
            dictwordobj, is_new = self.load_word(diobj, qword, tts_lang)
            if not is_new:
                dictwordobj.words.clear()
            func = partial(self.process, diobj, dictwordobj)
            self.ui.qwebView.page().toHtml(func)

    @pyqtSlot()
    def _load_started(self):
        self.ui.groupBox_7.setVisible(True)
        self.ui.dictBox.setEnabled(False)
        self.ui.accentBox.setEnabled(False)
        self.ui.dictMktts.setEnabled(False)

    @pyqtSlot(int)
    def _load_progress(self, val):
        self.ui.loadingBar.setValue(val)

    @pyqtSlot(bool)
    @except_check
    def _load_finished(self, bok):
        self.ui.groupBox_7.setVisible(False)
        self.ui.dictBox.setEnabled(True)
        self.ui.accentBox.setEnabled(True)
        self.ui.dictMktts.setEnabled(True)
        if bok:
            url = self.ui.qwebView.page().url()
            index = self.ui.dictBox.currentIndex()
            diobj = self.dictionaries[index]
            qok, qword = diobj.check_url(url)
            if qok:
                tts_lang = self.ui.accentBox.currentData()
                dictwordobj, is_new = self.load_word(diobj, qword, tts_lang)
                if is_new:
                    func = partial(self.process, diobj, dictwordobj)
                    self.ui.qwebView.page().toHtml(func)
                else:
                    self.update_dictword(dictwordobj)

    def closeEvent(self, event):
        """
        rewrite closeEvent, so when mainwindows closing, can clear up
        :param event:
        :return: None
        """
        AsyncTask.check_thread()
        self.save_dictword_change()

    def load_word(self, diobj, qword, tts_lang):
        """
        load dictobj, if don't exist then create it
        :param diobj:
        :param qword:
        :return: dictobj, is_new
        """
        data_path = os.path.join(data_dir, 'dictionaries', diobj.name, qword)
        if os.path.exists(data_path) and not os.path.isdir(data_path):
            raise RuntimeError("Loading failed: [%s] is'nt directory" % data_path)
        if os.path.exists(data_path):
            try:
                dictwordobj = DictWord.load(data_path)
                return dictwordobj, False
            except Exception as e:
                QMessageBox.warning(self, 'Warning', 'Loading failed: [%s], %s' % (data_path, str(e)))
        else:
            os.makedirs(data_path, exist_ok=True)
        dictwordobj = DictWord(data_path=data_path, tts_lang=tts_lang, query_word=qword)
        return dictwordobj, True

    @coroutine
    def process(self, diobj, dictwordobj, html):
        self.ui.groupBox_5.setVisible(True)
        try:
            info = '%s, parse html' % dictwordobj.query_word
            self.ui.progressBar.setValue(0)
            self.ui.progressLabel.setText(info)
            bok = yield AsyncTask(diobj.parse_html, dictwordobj, html)
            if not bok:
                dictwordobj.clear()
                info = '%s, parse failed!' % dictwordobj.query_word
                self.ui.progressBar.setValue(100)
                self.ui.progressLabel.setText(info)
                yield AsyncTask(time.sleep, 3)
                self.ui.groupBox_5.setVisible(False)
                return

            info = '%s, translate to voice ...' % dictwordobj.query_word
            self.ui.progressBar.setValue(10)
            self.ui.progressLabel.setText(info)
            total = 0
            for w in dictwordobj.words:
                if not w.title_voices and w.title_text:
                    total += 1
                if not w.content_voices and w.content_text:
                    total += 1
            cur = 0
            for w in dictwordobj.words:
                if not w.title_voices and w.title_text:
                    fname, fpath = dictwordobj.mk_voice_fname()
                    yield AsyncTask(trans_tts, w.title_text, fpath)
                    w.title_voices.append(fname)
                    cur += 1
                    progress = 10 + int(90 * cur / total)
                    self.ui.progressBar.setValue(progress)
                    self.ui.progressLabel.setText(info)
                if not w.content_voices and w.content_text:
                    fname, fpath = dictwordobj.mk_voice_fname()
                    yield AsyncTask(trans_tts, w.content_text, fpath)
                    w.content_voices.append(fname)
                    progress = 10 + int(90 * cur / total)
                    self.ui.progressBar.setValue(progress)
                    self.ui.progressLabel.setText(info)

        except (Exception, GeneratorExit):
            dictwordobj.clear()
            self.ui.groupBox_5.setVisible(False)
            raise

        info = '%s, finished!' % dictwordobj.query_word
        self.ui.progressBar.setValue(100)
        self.ui.progressLabel.setText(info)

        dictwordobj.save()
        self.ui.groupBox_5.setVisible(False)
        self.update_dictword(dictwordobj)
        return

    @coroutine(is_block=True)
    def mk_voice(self, is_title):
        self.curDictWordLock = True

        progressdlg = QProgressDialog('Mktts', parent=self)
        progressdlg.setWindowModality(Qt.WindowModal)
        progressdlg.setAutoClose(False)
        progressdlg.setAutoReset(False)
        progressdlg.setCancelButton(None)
        progressdlg.show()

        try:
            info = '%s, translate to voice ...' % self.curDictWord.query_word
            progressdlg.setLabelText(info)
            progressdlg.setValue(10)

            fname, fpath = self.curDictWord.mk_voice_fname()
            txt = self.curWord.title_text if is_title else self.curWord.content_text
            yield AsyncTask(trans_tts, txt, fpath)
            if is_title:
                self.curWord.title_voices = [fname]
            else:
                self.curWord.content_voices = [fname]

        except (Exception, GeneratorExit):
            self.curDictWordLock = False
            progressdlg.done(0)
            raise

        info = '%s, finished!' % self.curDictWord.query_word
        progressdlg.setLabelText(info)
        progressdlg.setValue(100)
        self.curDictWordChange = True
        self.curDictWordLock = False
        progressdlg.done(0)
        return
