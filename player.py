import mpv
import conf
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ControlButton(QPushButton):
    def __init__(self, *args, **kwargs):
        _defclk = lambda: None
        self.click_handler = kwargs.pop('clicked', _defclk)
        super().__init__(*args, **kwargs)
        self.clicked.connect(self._click)
        self.setFixedSize(64, 64)

    def click_handler(self, btn):
        raise NotImplementedError

    def _click(self, i):
        self.click_handler(self)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Return:
            self.click()
        elif event.key() == Qt.Key_Down:
            self.parent().down_navigate()


class Player(object):
    url = None
    is_playing = False
    is_paused = False
    win_id = None
    _playlist = []
    current_index = 0
    control = None

    def __init__(self, winid, control):
        self.win_id = winid
        self.control = control
        self.set_controls()

    def setup_player(self):
        self._player = mpv.MPV(
            wid=self.win_id,
            ytdl=True,
            vo=conf.MPV_VO,
            log_handler=print,
            #watch_later_directory='~/.config/mpv/watch_later'
        )

    def set_controls(self):
        self.control.setWidget(QWidget())
        self.control.widget().setLayout(QVBoxLayout())
        self.control.widget().layout().setContentsMargins(0, 0, 0, 0)
        self.control.widget().layout().setSpacing(0)
        self.control.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.control.setFeatures(self.control.NoDockWidgetFeatures)

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

        self.control.widget().layout().addWidget(self.buttons)

        self.playlist_ctrl = QListWidget(flow=QListView.LeftToRight)
        self.playlist_ctrl.setViewMode(QListView.IconMode)
        self.playlist_ctrl.setWrapping(False)
        self.playlist_ctrl.setWordWrap(True)
        self.playlist_ctrl.setIconSize(QSize(240, 320))

        self.buttons.down_navigate = lambda: self.playlist_ctrl.setFocus()

        self.control.widget().layout().addWidget(self.playlist_ctrl)
        self.control.hide()

    def stop(self):
        self._player.quit_watch_later(0)
        self._player.terminate()
        self.is_playing = False

    def pause(self):
        self._player.pause()
        self.is_paused = True

    def play(self):
        try:
            self.url = self.playlist[self.current_index][0]
        except KeyError:
            return False
        else:
            self.is_playing and self.stop()
            self.setup_player()
            self._player.play(self.url)
            self.select_current()
            self.is_playing = True
            return True

    def select_current(self):
        self.playlist_ctrl.item(self.current_index).setSelected(True)

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
