#!/usr/bin/env python3
import sys
import time
import math

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from decorators import click_protection
from player import Player
from categories import Categories
from youtube import YouTubeView
from tv import TVView
from onetv import OneTvView


class Overlay(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)
        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerEvent)
        self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(0, 0, 0, 100)))
        painter.setPen(QPen(Qt.NoPen))

        for i in range(6):
            if self.counter % 6 == i:
                painter.setBrush(QBrush(QColor(127, 255, 127)))
            elif self.counter % 6 == i+1:
                painter.setBrush(QBrush(QColor(127, 200, 127)))
            elif self.counter % 6 == i+2:
                painter.setBrush(QBrush(QColor(127, 155, 127)))
            else:
                painter.setBrush(QBrush(QColor(127, 127, 127)))
            painter.drawEllipse(
                self.width()/2 + 30 * math.cos(2 * math.pi * i / 6.0) - 10,
                self.height()/2 + 30 * math.sin(2 * math.pi * i / 6.0) - 10,
                20, 20)

        painter.end()

    def showEvent(self, event):
        self.counter = 0
        self.timer.start(120)

    def timerEvent(self):
        self.counter += 1
        self.update()
        if self.counter == 60:
            self.counter = 0

    def hideEvent(self, event):
        #self.killTimer(self.timer)
        self.timer.stop()
        self.counter = 0


class Main(QMainWindow):
    current_view = None
    last_control_time = time.time()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.youtube_class = YouTubeView
        self.youtube = YouTubeView(self)
        self.tv_class = TVView
        self.tv = TVView(self)
        self.onetv = OneTvView(self)
        self.onetv_class = OneTvView

        self.views = ('youtube', 'tv', 'onetv')

        #self.container = MainWidget(self)
        self.container = QScrollArea()
        #self.container.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.container.setWidgetResizable(True)
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgb(50,50,50);
                color: #fff;
                margin: 0;
            }
        """)
        #self.container.setWidget(MainWidget())

        self.setCentralWidget(self.container)
        #self.container.setAttribute(Qt.WA_DontCreateNativeAncestors)
        #self.container.setAttribute(Qt.WA_NativeWindow)

        self.categories = Categories(self.container)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.categories, Qt.Vertical)
        self.categories.setFocus()

        self.play_control = QDockWidget()
#        self.play_control.setLayout(QVBoxLayout())
#        self.play_control.layout().setContentsMargins(0, 0, 0, 0)
#        self.play_control.layout().setSpacing(0)
#        self.play_control.setFixedHeight(50)
#        self.play_control.setAllowedAreas(Qt.BottomDockWidgetArea)
#        self.play_control.setFeatures(self.play_control.NoDockWidgetFeatures)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.play_control)

        self.player = Player(str(int(self.container.winId())), self.play_control)

        #player = mpv.MPV(wid=str(int(self.container.winId())),
        #        vo='vdpau', # You may not need this
        #        log_handler=print)
        #player.play(sys.argv[1])

        self.timer = QTimer()
        self.timer.timeout.connect(self._timer)
        self.timer.start(1000)
        self.overlay = Overlay(self.centralWidget())
        self.overlay.resize(1920, 1080)
        self.overlay.hide()

    def _timer(self):
        if (time.time() - self.last_control_time) > 7 and not self.play_control.isHidden():
            self.play_control.hide()
            self.container.setFocus()

    def _show_view(self, view_name):
        view_class = getattr(self, view_name+'_class')
        view = getattr(self, view_name)
        [getattr(self, v).hide() for v in self.views if v != view_name]
        try:
            self.container.setWidget(view)
        except RuntimeError:
            view = view_class(self)
            setattr(self, view_name, view)

        view.setFocus()
        if not view.rendered:
            view.render()
        view.show()
        self.categories.hide()
        self.current_view = view
        self.current_view_name = view_name
        self.overlay.hide()

    def show_youtube(self):
        self._show_view('youtube')

    def show_tv(self):
        self._show_view('tv')

    def show_onetv(self):
        self._show_view('onetv')

    @click_protection
    def keyPressEvent(self, event):
        self.last_control_time = time.time()
        if event.key() == Qt.Key_Right and self.current_view.rendered:
            self._show_view(self.current_view_name)
        elif event.key() == Qt.Key_Escape and self.player.is_playing:
            if not self.play_control.isHidden():
                self.play_control.hide()
                self.container.setFocus()
            else:
                self.player.stop()
                self.current_view.setFocus()
                #self.setCentralWidget(self.container)
        elif event.key() == Qt.Key_Return and self.player.is_playing and self.play_control.isHidden():
            self.play_control.show()
            self.player.play_btn.setFocus()
        elif self.current_view:
            self.current_view.keyPressEvent(event)
        else:
            super().keyPressEvent(event)


app = QApplication(sys.argv)
#app.setAttribute(Qt.AA_UseStyleSheetPropagationInWidgetStyles, True)
app.setStyleSheet("""
    QWidget, QMainWindow {
        background-color: rgb(50,50,50);
        color: #fff;
        font-size: 22pt;
        margin: 0;
    }
    QWidget:item:focus:selected {
        background-color: rgb(100,100,100);
        color: #fff;
    }
""")

# This is necessary since PyQT stomps over the locale settings needed by libmpv.
# This needs to happen after importing PyQT before creating the first mpv.MPV instance.
import locale
locale.setlocale(locale.LC_NUMERIC, 'C')
win = Main()
win.categories.render()
win.setAttribute(Qt.WA_NoSystemBackground, True)
win.setAttribute(Qt.WA_TranslucentBackground, True)
win.showFullScreen()
sys.exit(app.exec_())
