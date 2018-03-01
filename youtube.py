import os
import json
import urllib
import requests
from pprint import pprint

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import conf


class YouTubeView(object):
    current_focus = 0
    results = []
    rendered = False
    rec_api = requests.session()
    rec_next = None
    rec_continuation = None
    rec_row = 0
    rec_col = 0
    rec_data = {
        "context": {
            "client": {
                "clientName": "TVHTML5",
                "clientVersion": "5.20160729",
                "screenWidthPoints": 1920,
                "screenHeightPoints": 1080,
                "screenPixelDensity": 1,
                "theme": "CLASSIC",
                "webpSupport": False,
                "animatedWebpSupport": False,
                "acceptRegion": "RU",
                "acceptLanguage": "ru",
                "tvAppInfo": {
                    "appQuality": "TV_APP_QUALITY_FULL_ANIMATION"
                }
            },
            "request": {},
            "user": {
                "enableSafetyMode": False
            }
        },
        "browseId": "default"
    }

    def __init__(self, parent=None):
        self.parent = parent
        self.search = QLineEdit()
        self.results = QListWidget(flow=QListView.LeftToRight)
        self.results.setViewMode(QListView.IconMode)
        self.results.setWrapping(False)
        self.results.setWordWrap(True)
        self.results.hide()
        self.layout = QFormLayout()
        self.layout.setLabelAlignment(Qt.AlignHorizontal_Mask)
        self.layout.addRow(QLabel("Search"), self.search)
        self.layout.addRow(self.results)

    def render(self):
        print('RENDER')
        self.parent.setLayout(self.layout)
        self.recomendations()
        self.rendered = True

    def show(self):
        self.parent.setLayout(self.layout)

    def setFocus(self):
        self.current_focus = 1
        #w = self.layout.takeAt(self.current_focus).widget()
        #print(self.layout.takeAt(self.current_focus))
       # print(w)
       # w.setFocus()
        #w.setCurrentRow(1)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            self.layout.takeAt(self.current_focus+1).widget().setFocus()
            self.current_focus += 1
#            self.parent.window().categories.show()
#            self.parent.window().categories.categories_list.setFocus()

    def activate_item(self, item):
        if hasattr(item, 'video_id') and item.video_id:
            self.play(item.video_id)
        elif hasattr(item, 'channel_id') and item.channel_id:
            self.render_channel(item.channel_id)

    def play(self, id):
        self.parent.window().player.set_url('https://www.youtube.com/watch?v={}'.format(id))
        print('Play video', id)
        self.parent.window().player.play()

    def render_channel(self, id):
        print('Render channel', id)

    def recomendations(self):
        url = '{}?key={}'.format(conf.YOUTUBE_RECOMENDATIONS_API, conf.YOUTUBE_API_KEY)
        data = self.rec_data.copy()
        if self.rec_next and self.rec_continuation:
            data['context']['clickTracking'] = {"clickTrackingParams": self.rec_next}
            data['continuation'] = self.rec_continuation
        res = self.rec_api.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        res = res.json()

        if self.rec_next and self.rec_continuation:
            content = res['continuationContents']['sectionListContinuation']['contents']
            continuations = res['continuationContents']['sectionListContinuation'].get('continuations', [{}])
        else:
            content = res['contents']['sectionListRenderer']['contents']
            continuations = res['contents']['sectionListRenderer'].get('continuations', [{}])

        for row in content:
            list_widget = QListWidget(flow=QListView.LeftToRight, height=250)
            list_widget.setViewMode(QListView.IconMode)
            list_widget.setWrapping(False)
            list_widget.setWordWrap(True)
            list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            list_widget.setFixedHeight(250)

            section = QVBoxLayout()

            section_title = row['shelfRenderer'].get('title', '')
            if section_title:
                section_title = section_title['runs'][0]['text']

            section.addWidget(QLabel(section_title))
            section.addWidget(list_widget)

            for col in row['shelfRenderer']['content']['horizontalListRenderer']['items']:
                is_channel = False
                it = col.get('gridVideoRenderer')
                if not it:
                    is_channel = True
                    it = col.get('gridChannelRenderer', {})

                thumb = it.get('thumbnail')
                filepath = 'img/youtube_default.png'
                if thumb:
                    thumb = thumb['thumbnails'][0]['url']
                    url = not thumb.startswith('http') and 'https:{}'.format(thumb) or thumb
                    filepath = 'cache/{}'.format(thumb.replace('/', '_'))
                    if not os.path.isfile(filepath):
                        urllib.request.urlretrieve(url, filepath)

                title = it['title']['runs'][0]['text'][:32]
                if len(title) < len(it['title']['runs'][0]['text']):
                    title += '...'

                badges = it.get('badges')
                mode = ''
                if badges:
                    mode = '[{}] '.format(badges[0]['textBadge']['label']['runs'][0]['text'])

                item = QListWidgetItem(QIcon(filepath), '{}{}'.format(mode, title))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
                item.video_id = it.get('videoId')
                item.channel_id = it.get('channelId')
                list_widget.addItem(item)
            list_widget.setIconSize(QSize(90, 120))
            list_widget.itemActivated.connect(self.activate_item)
            self.layout.addRow(section)
        self.rec_next = continuations[0].get('nextContinuationData', {}).get('clickTrackingParams')
        self.rec_continuation = continuations[0].get('nextContinuationData', {}).get('continuation')

