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
        self.layout = QFormLayout()
        label = QLabel("Search")
        self.layout.addRow(QLabel("Search"), self.search)
        #self.layout.addRow(self.result)

        style = """
            QWidget {
                background-color: rgba(50,50,50, 0.8);
                color: #fff;
            }
        """
        label.setStyleSheet(style)
        #self.result.setStyleSheet(style)
        self.search.setStyleSheet(style)

    def render(self):
        print('RENDER')
        self.recomendations()
        self.parent.setLayout(self.layout)
        self.rendered = True

    def show(self):
        self.parent.setLayout(self.layout)

    def setFocus(self):
        pass
        #self.result.setFocus()

#    def keyPressEvent(self, event):
#        if event.key() == Qt.Key_Left:
#            self.parent.window().categories.show()
#            self.parent.window().categories.categories_list.setFocus()

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
            list_widget = QListWidget(flow=QListView.LeftToRight)
            list_widget.setViewMode(QListView.IconMode)
            list_widget.setWrapping(False)
            for col in row['shelfRenderer']['content']['horizontalListRenderer']['items']:
                it = col.get('gridVideoRenderer', col.get('gridChannelRenderer', {}))
                thumb = it.get('thumbnail', {}).get('thumbnails', [{}])[0].get('url', 'default')
                url = not thumb.startswith('http') and 'https:{}'.format(thumb) or thumb
                filepath = 'cache/{}'.format(thumb.replace('/', '_'))
                if not os.path.isfile(filepath):
                    urllib.request.urlretrieve(url, filepath)
                title = it['title']['runs'][0]['text'][:32]
                if len(title) < len(it['title']['runs'][0]['text']):
                    title += '...'
                item = QListWidgetItem(QIcon(filepath), title)
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignBottom)
                item.setSizeHint(QSize(170, 120))
                list_widget.addItem(item)
            list_widget.setIconSize(QSize(90, 120))
            self.layout.addRow(list_widget)
        self.rec_next = continuations[0].get('nextContinuationData', {}).get('clickTrackingParams')
        self.rec_continuation = continuations[0].get('nextContinuationData', {}).get('continuation')

