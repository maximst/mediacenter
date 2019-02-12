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


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.files = QListWidget()
        self.files.setIconSize(QSize(300, 300))
        self.setStyleSheet('''
            QListWidget {
                font-size: 50px;
                margin: 30px 50px;
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
        self.layout().addWidget(self.files)

    def render(self):
        print('RENDER')
        self.show_files_list()
        self.rendered = True

    def show_files_list(self):
        while self.files.count() > 0:
            c = self.files.takeItem(0)
            self.files.removeItemWidget(c)

        quoted_path = list(map(urllib.parse.quote, self.path)) 
        quoted_path.append('?format=json')

        r = requests.get('http://{server}/{path}'.format(server=conf.MEDIA_SERVER,
                                                         path='/'.join(quoted_path)))
        self._resp = r.json()

        #pool = Pool(processes=16)
        #images = pool.map(cache_image, [i.get('image') for i in r.get('projects', [])])
        #pool.terminate()

        if self.path:
            self.add_item({'name': '←Назад', 'type': 'up'})

        for _file in self._resp:
            self.add_item(_file)

        self.files.show()
        self.files.item(self.path and 1 or 0).setSelected(True)
        self.files.setFocus()


    def add_item(self, _file):
        item = QListWidgetItem(_file['name'])
        item.name = _file['name']
        item.file_type = _file['type']
        self.files.addItem(item)

    def activate_item(self, item):
        if item.file_type == 'up':
            self.path.pop(-1)
        elif item.file_type == 'directory':
            self.path.append(item.name)
        elif item.file_type == 'file':
            return self.play(item)

        self.show_files_list()

    def play(self, item):
        print(item.name)
        print(item.file_type)
