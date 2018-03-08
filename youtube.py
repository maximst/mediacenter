import os
import json
import urllib
import requests
from pprint import pprint

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import conf


class KeyboardButton(QPushButton):
    def __init__(self, value):
        super().__init__(value)
        self.val = value
        self.clicked.connect(self._click)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Down, Qt.Key_Up):
            self.parent().keyPressEvent(event, self)
        elif event.key() == Qt.Key_Return:
            self.click_handler(self)
        else:
            super().keyPressEvent(event)

    def click_handler(self, btn):
        raise NotImplementedError

    def _click(self, i):
        self.click_handler(self)


class Keyboard(QWidget):
    ru_keys = (
        ('А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', '<x'),
        ('И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Clear'),
        ('Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', '123'),
        ('Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я', 'En'),
        ('space', 'Enter'),
    )

    en_keys = (
        ('A', 'B', 'C', 'D', 'E', 'F', 'G', '<x'),
        ('H', 'I', 'J', 'K', 'L', 'M', 'N', 'Clear'),
        ('O', 'P', 'Q', 'R', 'S', 'T', 'U', '123'),
        ('V', 'W', 'X', 'Y', 'Z', '-', "'", 'Ru'),
        ('space', 'Enter'),
    )

    digital_keys = (
        ('1', '2', '3', '&', '#', '(', ')', '<x'),
        ('4', '5', '6', '@', '!', '?', ':', 'Clear'),
        ('7', '8', '9', '0', '.', '_', '"', 'Ru'),
        ('space', 'Enter'),
    )

    def __init__(self, parent=None, input_field=None):
        super().__init__(parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.input_field = input_field

    def keyPressEvent(self, event, button=None):
        row_count = self.layout.rowCount()
        pos = self.layout.getItemPosition(self.layout.indexOf(button))
        if event.key() == Qt.Key_Down and pos[0] < row_count - 1:
            self.layout.itemAtPosition(pos[0]+1, pos[1]).widget().setFocus()
        elif event.key() == Qt.Key_Up and pos[0]:
            self.layout.itemAtPosition(pos[0]-1, pos[1]).widget().setFocus()
        elif event.key() == Qt.Key_Left and not pos[1]:
            self.parent().keyPressEvent(event)

    def show(self, ktype):
        while self.layout.count():
            c = self.layout.takeAt(0)
            c.widget().deleteLater()

        for ri, row in enumerate(getattr(self, '{}_keys'.format(ktype), [])):
            for ci, col in enumerate(row):
                btn = KeyboardButton(col)
                btn.click_handler = self.handle_button
                self.layout.addWidget(btn, ri, ci)

    def handle_button(self, btn):
        if len(btn.val) == 1 or btn.val.lower() == 'space':
            self.input_field.insert(btn.val.lower() == 'space' and ' ' or btn.val)
        elif btn.val.lower() in ('en', 'ru', '123'):
            self.show(btn.val == '123' and 'digital' or btn.val.lower())
        elif btn.val == '<x':
            self.input_field.backspace()
        elif btn.val.lower() == 'clear':
            self.input_field.del_()


class YouTubeView(QWidget):
    current_focus = 0
    results = []
    rendered = False
    recs = []
    rec_api = requests.session()
    rec_next = None
    rec_continuation = None
    rec_end = False
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
        super().__init__(parent)
        #self.parent = parent
        self.search = QLineEdit()
        self.search.keyPressEvent = self.search_activated

        self.results = QListWidget(flow=QListView.LeftToRight)
        self.results.setViewMode(QListView.IconMode)
        self.results.setWrapping(False)
        self.results.setWordWrap(True)

        self.layout = QVBoxLayout()
        #self.layout.setLabelAlignment(Qt.AlignHorizontal_Mask)

        self.search_layout = QHBoxLayout()
        self.search_layout.addWidget(QLabel('Search'))
        self.search_layout.addWidget(self.search)
        self.layout.addLayout(self.search_layout)

        self.keyboard_layout = QHBoxLayout()
        self.keyboard = Keyboard(input_field = self.search)
        self.keyboard_layout.addWidget(QListWidget())
        self.keyboard_layout.addWidget(self.keyboard)

        self.results_layout = QVBoxLayout()
        self.results_layout.addWidget(QLabel('Results'))
        self.results_layout.addWidget(self.results)

    def render(self):
        print('RENDER')
        self.setLayout(self.layout)
        self.recomendations()
        self.rendered = True

    #def show(self):
    #    self.setLayout(self.layout)

    def setFocus(self):
        super().setFocus()
        self.current_focus = 1
        w = self.layout.itemAt(self.current_focus).itemAt(1).widget()
        w.setFocus()
        self.window().container.ensureWidgetVisible(w, 0, 0)
        _si = lambda: True
        not getattr(w, 'selectedItems', _si)() and w.item(0) and w.item(0).setSelected(True)
        #print(self.layout.takeAt(self.current_focus))
       # print(w)
       # w.setFocus()
        #w.setCurrentRow(1)

    def keyPressEvent(self, event):
        print(event.key())
        w = None
        _si = lambda: True
        if event.key() == Qt.Key_Down:
            if self.current_focus >= self.layout.count() - 1 and not self.rec_end:
                self.recomendations()
            w = self.layout.itemAt(self.current_focus+1).itemAt(1).widget()
            w.setFocus()

            if isinstance(w, Keyboard):
                w.layout.itemAt(0).widget().setFocus()

            not getattr(w, 'selectedItems', _si)() and w.item(0) and w.item(0).setSelected(True)
            self.current_focus += 1
        elif event.key() == Qt.Key_Up:
            w = self.layout.itemAt(self.current_focus-1).itemAt(1).widget()
            w.setFocus()
            not getattr(w, 'selectedItems', _si)() and w.item(0) and w.item(0).setSelected(True)
            self.current_focus -= 1
        elif event.key() == Qt.Key_Left:
            self.window().categories.show()
            self.window().categories.categories_list.setFocus()
        self.window().container.ensureWidgetVisible(w, 0, 0)

    def activate_item(self, item):
        if hasattr(item, 'video_id') and item.video_id:
            self.play(item.video_id)
        elif hasattr(item, 'channel_id') and item.channel_id:
            self.render_channel(item.channel_id)

    def play(self, id):
        self.window().player.set_url('https://www.youtube.com/watch?v={}'.format(id))
        print('Play video', id)
        self.window().player.play()
        self.window().setFocus()

    def render_channel(self, id):
        print('Render channel', id)

    def recomendations(self):
        url = '{}?key={}'.format(conf.YOUTUBE_RECOMENDATIONS_API, conf.YOUTUBE_API_KEY)
        data = self.rec_data.copy()
        if self.rec_next and self.rec_continuation:
            data['context']['clickTracking'] = {"clickTrackingParams": self.rec_next}
            data['continuation'] = self.rec_continuation
            data.pop('browseId', None)
        res = self.rec_api.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        res = res.json()

        if self.rec_next and self.rec_continuation:
            content = res['continuationContents']['sectionListContinuation']['contents']
            continuations = res['continuationContents']['sectionListContinuation'].get('continuations', [{}])
        else:
            content = res['contents']['sectionListRenderer']['contents']
            continuations = res['contents']['sectionListRenderer'].get('continuations', [{}])

        for row in content:
            list_widget = QListWidget(flow=QListView.LeftToRight, height=200)
            list_widget.setViewMode(QListView.IconMode)
            list_widget.setWrapping(False)
            list_widget.setWordWrap(True)
            list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            list_widget.setFixedHeight(200)
            list_widget.setSelectionMode(QAbstractItemView.SingleSelection)

            section = QVBoxLayout()
            section_title = row['shelfRenderer'].get('title', '')
            if section_title:
                section_title = section_title['runs'][0]['text']

            section.addWidget(QLabel(section_title))
            section.addWidget(list_widget)

            for col in row['shelfRenderer']['content']['horizontalListRenderer']['items']:
                if 'gridButtonRenderer' in col:
                    item = QListWidgetItem(QIcon('img/nav/ontop.png'), 'ON TOP')
                    item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
                    item.video_id = None
                    item.channel_id = None
                    list_widget.addItem(item)
                    self.rec_end = True
                    list_widget.setFocus()
                    item.setSelected(True)
                    self.window().container.ensureWidgetVisible(list_widget, 0, 0)
                    break

                it = col.get('gridVideoRenderer')
                if not it:
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
            list_widget.setIconSize(QSize(240, 320))
            list_widget.itemActivated.connect(self.activate_item)
            self.recs.append(section)
            self.layout.addLayout(section)
        self.rec_next = continuations[0].get('nextContinuationData', {}).get('clickTrackingParams')
        self.rec_continuation = continuations[0].get('nextContinuationData', {}).get('continuation')

    def search_activated(self, event):
        if event.key() == Qt.Key_Return:
            while self.layout.count() > 1:
                c = self.layout.takeAt(1)
                c.itemAt(0).widget().deleteLater()
                c.itemAt(1).widget().deleteLater()
            self.layout.addLayout(self.keyboard_layout)
            self.keyboard.show('ru')
            self.keyboard.setFocus()
            self.keyboard.layout.itemAt(0).widget().setFocus()
            self.layout.addLayout(self.results_layout)
        elif event.key() in (Qt.Key_Up, Qt.Key_Right, Qt.Key_Down, Qt.Key_Left):
            self.keyPressEvent(event)
