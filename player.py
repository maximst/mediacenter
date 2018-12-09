import time

import mpv
import conf
from decorators import click_protection
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ControlButton(QPushButton):
    def __init__(self, *args, **kwargs):
        _defclk = lambda: None
        self.click_handler = kwargs.pop('clicked', _defclk)
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setStyleSheet('''
            ControlButton:hover, ControlButton:focus {
                background: rgb(128,128,128);
            }
            ControlButton:pressed, ControlButton:focus:pressed {
                background: rgb(100,100,100);
            }
        ''')
        self.clicked.connect(self._click)
        self.setFixedSize(64, 64)

    def click_handler(self, btn):
        raise NotImplementedError

    def _click(self, i):
        self.click_handler(self)

    @click_protection
    def keyPressEvent(self, event):
        self.window().last_control_time = time.time()
        if event.key() == Qt.Key_Return:
            self.click()
        elif event.key() == Qt.Key_Down:
            self.parent().down_navigate()
        elif event.key() == Qt.Key_Up:
            return
        elif event.key() == Qt.Key_Left:
            self.parent().left_navigate(self)
        elif event.key() == Qt.Key_Right:
            self.parent().right_navigate(self)
        else:
            super().keyPressEvent(event)


class Playlist(QListWidget):
    def __init__(self, *args, **kwargs):
        self.playlist_up = kwargs.pop('playlist_up', self.playlist_up)
        self.activate_item = kwargs.pop('activate_item', self.playlist_up)
        self.update_playlist = kwargs.pop('update_playlist', self.playlist_up)
        self.close_player = kwargs.pop('close_player', self.playlist_up)
        kwargs['flow'] = QListView.LeftToRight

        super().__init__(*args, **kwargs)

        self.setViewMode(QListView.IconMode)
        self.setWrapping(False)
        self.setWordWrap(True)
        self.setIconSize(QSize(240, 320))
        self.setFixedHeight(300)
        self.itemActivated.connect(self.activate_item)

        self.setStyleSheet("""
            Playlist {
                margin: 0 50px 20px 30px;
            }
            Playlist:item:selected {
                background-color: rgb(70,70,70);
                color: #fff;
            }
            Playlist:item:focus:selected {
                background-color: rgb(150,150,150);
                color: #fff;
            }
        """)

    def playlist_up(self):
        raise NotImplementedError

    @click_protection
    def keyPressEvent(self, event):
        self.window().last_control_time = time.time()
        if event.key() == Qt.Key_Up:
            self.playlist_up()
        elif event.key() == Qt.Key_Down:
            return
        elif event.key() == Qt.Key_Left and self.currentRow() < 1:
            return
        elif event.key() == Qt.Key_Right and self.currentRow() == self.count() - 1:
            self.update_playlist()
        else:
            super().keyPressEvent(event)


class Player(object):
    url = None
    is_playing = False
    is_paused = False
    win_id = None
    _playlist = []
    current_index = 0
    control = None
    _player = None

    def __init__(self, winid, control):
        self.win_id = winid
        self.control = control
        self.set_controls()
        self.timer = QTimer()
        self.timer.timeout.connect(self._timer)
        self.timer.start(1000)

    def setup_player(self):
        params = {
            'wid': self.win_id,
            'ytdl': True,
            'ytdl_format': "bestvideo[height<=1080][vcodec!=vp9]+bestaudio/best[height<=1080]",
            'vo': conf.MPV_VO,
            'hwdec_codecs': 'all',
            'video_zoom': -0.05,
            'log_handler': print
        }
        if hasattr(conf, 'MPV_HWDEC'):
            params['hwdec'] = conf.MPV_HWDEC

        self._player = mpv.MPV(**params)

    def set_controls(self):
        self.control.setWidget(QWidget())
        self.control.widget().setLayout(QVBoxLayout())
        self.control.widget().layout().setContentsMargins(20, 0, 20, 20)
        self.control.widget().layout().setSpacing(0)
        self.control.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.control.setFeatures(self.control.NoDockWidgetFeatures)

        self.progress = QSlider(Qt.Horizontal)
        self.progress.is_locked = False
        self.progress.setMinimum(0)
        self.progress.sliderMoved.connect(self.seek)
        self.progress.sliderPressed.connect(self.lock_slider)
        self.progress.sliderReleased.connect(self.seek)
        self.control.widget().layout().addWidget(self.progress)

        self.buttons = QWidget()
        self.buttons.layout = QHBoxLayout()
        self.buttons.layout.setContentsMargins(0, 0, 0, 0)
        self.buttons.layout.setSpacing(0)
        self.buttons.setLayout(self.buttons.layout)

        self.prev_btn = ControlButton('<<', clicked=self.prev_play)

        self.play_btn = ControlButton(clicked=self.play_pause)
        self.play_btn.setIcon(self.buttons.style().standardIcon(QStyle.SP_MediaPlay))

        self.next_btn = ControlButton('>>', clicked=self.next_play)

        self.buttons.layout.addWidget(self.prev_btn)
        self.buttons.layout.addWidget(self.play_btn)
        self.buttons.layout.addWidget(self.next_btn)
        self.buttons.keyPressEvent = click_protection(self.buttons.keyPressEvent, s=self.buttons)

        self.control.widget().layout().addWidget(self.buttons)

        self.playlist_ctrl = Playlist(playlist_up=self.playlist_up,
                                      activate_item=self.play_current_item,
                                      update_playlist=self.update_playlist)

        self.buttons.down_navigate = lambda: self.playlist_ctrl.setFocus()
        self.buttons.left_navigate = lambda b: self.buttons_nav('left', b)
        self.buttons.right_navigate = lambda b: self.buttons_nav('right', b)

        self.control.widget().layout().addWidget(self.playlist_ctrl)

        self.control.hide()

    def set_icon_size(self, h, w):
        self.playlist_ctrl.setIconSize(QSize(h, w))

    def playlist_up(self):
        self.play_btn.setFocus()

    def get_current(self):
        return self.current_index

    def play_current_item(self, item):
        self.current_index = self.playlist_ctrl.indexFromItem(item).row()
        self.play()
        self.playlist_ctrl.setFocus()

    def buttons_nav(self, direction, btn):
        index = self.buttons.layout.indexOf(btn)
        if direction == 'left' and index:
            self.buttons.layout.itemAt(index-1).widget().setFocus()
        elif direction == 'right' and index < self.buttons.layout.count():
            item = self.buttons.layout.itemAt(index+1)
            item and item.widget().setFocus()

    def stop(self):
        self.is_playing = False
        #self._player.quit_watch_later(0)
        self._player.quit()
        self._player.terminate()
        self.setup_player()
        self.hide_loader(None)

    def pause(self):
        self._player.pause = True
        self.is_paused = True

    def play(self):
        if self.is_playing and self.is_paused:
            self._player.pause = False
            self.is_paused = False
            return True

        try:
            self.url = self.playlist[self.current_index][0]
            if callable(self.url):
                self.url = self.url()
        except IndexError:
            return False
        else:
            self.is_playing and self.stop() or self.setup_player()
            self._player.play(self.url)
            self.select_current()
            self.is_playing = True
            self.control.window().overlay.show()
            self._player.event_callback('end_file')(self.next_play_event)
            self._player.event_callback('file_loaded')(self.hide_loader)
            return True

    def hide_loader(self, event):
        self.control.window().overlay.hide()

    def select_current(self, index=None):
        self.playlist_ctrl.item(index or self.current_index).setSelected(True)
        self.playlist_ctrl.setCurrentRow(index or self.current_index)

    @property
    def playlist(self):
        return self._playlist

    @playlist.setter
    def playlist(self, value):
        self.current_index = 0
        self._playlist = value

        while self.playlist_ctrl.count():
            self.playlist_ctrl.takeItem(0)

        for row in value:
            self.playlist_ctrl.addItem(QListWidgetItem(QIcon(row[2]), row[1]))

    def new_playlist_items(self):
        return []

    def update_playlist(self):
        index = len(self.playlist) - 1
        new_items = self.new_playlist_items()
        self.playlist += new_items
        self.select_current(index)
        return

    def next_play_event(self, event):
        if self.is_playing:
            self.next_play(None)

    def next_play(self, btn):
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.play()

    def prev_play(self, btn):
        if self.current_index:
            self.current_index -= 1
            self.play()

    def play_pause(self, btn):
        if self.is_paused:
            self.play()
        else:
            self.pause()

    def seek(self):
        self.progress.is_locked = True
        pos = self.progress.value()
        self._player.time_pos = pos
        self.progress.is_locked = False

    def lock_slider(self):
        self.progress.is_locked = True

    def _timer(self):
        if self._player and not self.progress.is_locked:
            self.progress.setMaximum(int(self._player.duration or 0))
            self.progress.setValue(int(self._player.time_pos or 0))
