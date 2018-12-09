import os
import json
import urllib
import requests
from decorators import click_protection
from multiprocessing import Pool
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


class OneTvView(QWidget):
    rendered = False
    playlist = []

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.projects = QListWidget()
        self.projects.setIconSize(QSize(300, 300))
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
        self.projects.itemActivated.connect(self.show_project_details)
        self.projects.keyPressEvent = click_protection(self.projects.keyPressEvent, s=self.projects)
        self.layout().addWidget(self.projects)

    def render(self):
        print('RENDER')
        self.show_projects_list()
        self.rendered = True

    def show_projects_list(self, init=True):
        while self.layout().count() > 1:
            c = self.layout().takeAt(1)
            c.widget().deleteLater()

        if not init:
            self.projects.show()
            self.projects.setFocus()
            return None

        r = requests.get('http://json-api.1internet.tv/1tv-json-api/projects/list?rubrics=yes')
        r = r.json()

        pool = Pool(processes=16)
        images = pool.map(cache_image, [i.get('image') for i in r.get('projects', [])])
        pool.terminate()

        for i, project in enumerate(r.get('projects', [])):
            item = QListWidgetItem(QIcon(images[i]), project['name'])
            item.rubrics = project.get('rubrics', [])
            item.rubrics.sort(key=lambda x: x['position'])
            item.project_id = project['id']
            self.projects.addItem(item)
        self.projects.show()
        self.projects.item(0).setSelected(True)
        self.projects.setFocus()

    def show_project_details(self, item):
        self.project = QListWidget()
        self.project.setIconSize(QSize(320, 320))
        self.project.itemActivated.connect(self.play)
        self.project.setWordWrap(True)
        self.project.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.project.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.project.keyPressEvent = click_protection(self.project.keyPressEvent, s=self.project)
        self.playlist = []

        self.update_project_details(item)

        self.layout().addWidget(self.project)
        self.projects.hide()
        self.project.item(0).setSelected(True)
        self.project.setFocus()

    def update_project_details(self, item):
        index = hasattr(item, 'index') and item.index+1 or 0
        r = requests.get(
            'http://json-api.1internet.tv/1tv-json-api/projects/video',
            params={
                'id': item.project_id,
                'offset': index,
                'limit': 7,
                'rubric': item.rubrics[0]['rub_id']
            }
        )
        r = r.json()

        pool = Pool(processes=7)
        images = pool.map(cache_image, [i.get('video_image') for i in r.get('videos', [])])
        pool.terminate()

        next_items = []
        for i, video in enumerate(r.get('videos', [])):
            tl = video['video_name'].split()
            for c in range(len(tl)):
                if len(' '.join(tl[:c+1])) > 55:
                    tl.insert(c, '\n')
                    break
            title = ' '.join(tl)
            _item = QListWidgetItem(QIcon(images[i]), title)
            url = [v['src'] for v in video['source'] if v['src'].endswith('m3u8')][0]
            _item.url = url
            _item.index = i+index
            _item.rubrics = item.rubrics
            _item.project_id = item.project_id
            self.project.addItem(_item)
            self.playlist.append([url, video['video_name'], images[i]])
            next_items.append([url, video['video_name'], images[i]])

        def next_playlist():
            return self.update_project_details(_item)

        if next_items:
            self.window().player.new_playlist_items = next_playlist
        else:
            self.window().player.new_playlist_items = lambda: []

        return next_items

    def play(self, item):
        print('PLAY')
        self.window().player.playlist = self.playlist
        self.window().player.current_index = item.index
        self.window().player.play()
        self.window().setFocus()

    @click_protection
    def keyPressEvent(self, event):
        print('onetv', event.key())
        if event.key() == Qt.Key_Escape and self.layout().count() > 1:
            self.show_projects_list(init=False)
        elif event.key() == Qt.Key_Escape:
            self.window().categories.show()
            self.window().categories.widget().setFocus()
        elif (event.key() == Qt.Key_Down and self.projects.isHidden()
              and self.project.currentRow() == self.project.count() - 1):
            self.update_project_details(self.project.item(self.project.currentRow()))
        else:
            super().keyPressEvent(event)

    def setFocus(self):
        super().setFocus()
        if self.projects.isHidden():
            self.project.setFocus()
        else:
            self.projects.setFocus()
