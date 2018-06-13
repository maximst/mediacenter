#!/usr/bin/env python3
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from player import Player
from categories import Categories
from youtube import YouTubeView
from tv import TVView


class Main(QMainWindow):
    current_view = None

    def __init__(self, parent=None):
        super().__init__(parent)

        self.youtube_class = YouTubeView
        self.youtube = YouTubeView(self)
        self.tv_class = TVView
        self.tv = TVView(self)

        self.views = ('youtube', 'tv')

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

    def _show_view(self, view_name):
        view_class = getattr(self, view_name+'_class')
        view = getattr(self, view_name)
        [getattr(self, v).hide() for v in self.views if v != view_name]
        try:
            self.container.setWidget(view)
        except RuntimeError:
            view = view_class(self)
            setattr(self, view_name, view)

        if view.rendered:
            view.show()
        else:
            view.render()
        self.categories.hide()
        view.setFocus()
        self.current_view = view

    def show_youtube(self):
        self._show_view('youtube')

    def show_tv(self):
        self._show_view('tv')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right and self.current_view.rendered:
            self._show_view(self.current_view)
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
