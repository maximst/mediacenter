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
        kwargs['flow'] = QListView.LeftToRight

        super().__init__(*args, **kwargs)

        self.setViewMode(QListView.IconMode)
        self.setWrapping(False)
        self.setWordWrap(True)
        self.setIconSize(QSize(240, 320))

    def playlist_up(self):
        raise NotImplementedError

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.playlist_up()
        elif event.key() == Qt.Key_Down:
            return
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
        self._player = mpv.MPV(
            wid=self.win_id,
            ytdl=True,
            vo=conf.MPV_VO,
            log_handler=print,
            input_ipc_server='/tmp/mpvsocket',
            #watch_later_directory='~/.config/mpv/watch_later'
        )

    def set_controls(self):
        self.control.setWidget(QWidget())
        self.control.widget().setLayout(QVBoxLayout())
        self.control.widget().layout().setContentsMargins(0, 0, 0, 0)
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

        self.control.widget().layout().addWidget(self.buttons)

        self.playlist_ctrl = Playlist(playlist_up=self.playlist_up)

        self.buttons.down_navigate = lambda: self.playlist_ctrl.setFocus()
        self.buttons.left_navigate = lambda b: self.buttons_nav('left', b)
        self.buttons.right_navigate = lambda b: self.buttons_nav('right', b)

        self.control.widget().layout().addWidget(self.playlist_ctrl)

        self.control.hide()

    def playlist_up(self):
        self.play_btn.setFocus()

    def buttons_nav(self, direction, btn):
        index = self.buttons.layout.indexOf(btn)
        if direction == 'left' and index:
            self.buttons.layout.itemAt(index-1).widget().setFocus()
        elif direction == 'right' and index < self.buttons.layout.count():
            self.buttons.layout.itemAt(index+1).widget().setFocus()

    def stop(self):
        self._player.quit_watch_later(0)
        self._player.terminate()
        self.is_playing = False

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

    def seek(self):
        self.progress.is_locked = True
        pos = self.progress.value()
        print(pos)
        print(self._player.duration)
        print(self._player.time_pos)
        self._player.time_pos = pos
        self.progress.is_locked = False

    def lock_slider(self):
        self.progress.is_locked = True

    def _timer(self):
        if self._player and not self.progress.is_locked:
            self.progress.setMaximum(int(self._player.duration or 0))
            self.progress.setValue(int(self._player.time_pos or 0))
