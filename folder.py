import os
import urllib
import requests
import json
import conf
from multiprocessing import Pool
from decorators import click_protection
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


def cache_image(img_url):
    img_dir = os.path.join('cache', '1tv')
    img_file = os.path.join(img_dir, os.path.basename(img_url))

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    if not os.path.exists(img_file):
        try:
            urllib.request.urlretrieve(img_url, img_file)
        except Exception:
            return 'img/1tv_default.png'
    return img_file


class FolderView(QWidget):
    rendered = False
    playlist = []
    path = []
    _resp = {}
    MIMETYPES = (
        ('video', ('ogv', 'mpg', 'mpeg', 'avi', 'mkv', 'm4v', 'flv',
                   'webm', 'wmv', 'ts', 'vob', 'mov', 'mp4')),
        ('audio', ('ogg', 'oga', 'flac', 'mp3', 'mp2', 'mpc', 'wma',
                   'aac', 'ac3', 'aiff', 'ape', 'm4a', 'wav', 'wv',)),
        ('img', ('png', 'jpeg', 'jpg', 'gif', 'tif', 'tiff', 'bmp'))
    )


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.files = QListWidget()
        self.files.setIconSize(QSize(64, 64))
        self.setStyleSheet('''
            QListWidget, QLabel {
                font-size: 50px;
                margin: 30px 50px;
            }
            QLabel {
                margin-bottom: 5px;
            }
            QListWidget:item:focus:selected {
                background-color: rgb(100,100,100);
            }
            QListWidget:focus {
                background-color: rgb(80,80,80);
            }
        ''')
        self.files.itemActivated.connect(self.activate_item)
        self.files.keyPressEvent = click_protection(self.files.keyPressEvent, s=self.files)

        self.path_info = QLabel('/{}'.format('/'.join(self.path)))
        self.layout().addWidget(self.path_info)
        self.layout().addWidget(self.files)

    def render(self):
        print('RENDER')
        self.show_files_list()
        self.rendered = True
        self.files.setFocus()

    def get_url(self, filename=None):
        _path = self.path + [filename or '']
        quoted_path = list(map(urllib.parse.quote, _path))
        return 'http://{server}/{path}'.format(
            server=conf.MEDIA_SERVER,
            path='/'.join(quoted_path)
        )

    def show_files_list(self):
        while self.files.count() > 0:
            c = self.files.takeItem(0)
            self.files.removeItemWidget(c)

        self.playlist = []

        r = requests.get(self.get_url())
        self._resp = r.json()

        #pool = Pool(processes=16)
        #images = pool.map(cache_image, [i.get('image') for i in r.get('projects', [])])
        #pool.terminate()

        if self.path:
            self.add_item({'name': 'Назад', 'type': 'up'})

        for _file in self._resp:
            self.add_item(_file)

        self.files.show()
        self.files.setCurrentRow(self.path and 1 or 0)

    def get_mime(self, _file):
        if _file['type'] == 'up':
            return 'up'
        elif _file['type'] == 'directory':
            return 'directory'

        mt = filter(lambda m: _file['name'].split('.')[-1].lower() in m[1], self.MIMETYPES)
        return (list(mt) or [['other']])[0][0]

    def get_icon(self, mime):
        return 'img/nav/{}.png'.format(mime)

    def add_item(self, _file):
        self.path_info.setText('/{}'.format('/'.join(self.path)))

        mime_type = self.get_mime(_file)
        icon = self.get_icon(mime_type)
        url = self.get_url(_file['name'])

        item = QListWidgetItem(QIcon(icon), _file['name'])
        item.file_type = _file['type']
        item.name = _file['name']
        item.url = url

        if mime_type in map(lambda m: m[0], self.MIMETYPES):
            self.playlist.append((url, _file['name'], icon))
            item.index = len(self.playlist) - 1
        self.files.addItem(item)

    def activate_item(self, item):
        if item.file_type == 'up':
            self.path.pop(-1)
        elif item.file_type == 'directory':
            self.path.append(item.name)
        elif item.file_type == 'file' and hasattr(item, 'index'):
            return self.play(item)

        self.show_files_list()

    def play(self, item):
        print('PLAY')
        self.window().player.playlist = self.playlist
        self.window().player.current_index = item.index
        self.window().player.play()
        self.window().setFocus()

    @click_protection
    def keyPressEvent(self, event):
        print('folder', event.key())
        if event.key() == Qt.Key_Escape:
            self.window().categories.show()
            self.window().categories.widget().setFocus()
        else:
            super().keyPressEvent(event)

    def setFocus(self):
        super().setFocus()
        self.files.setFocus()
