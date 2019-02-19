import os
import gc
import time
import json
import pickle
import urllib
import requests
from decorators import click_protection
from multiprocessing import Pool
from pprint import pprint

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import conf


def cache_image(f):
    if not f[0]:
        return f[1]

    if not os.path.isfile(f[1]):
        try:
            urllib.request.urlretrieve(*f[:2])
            if f[2][1] != 360:
                w = 480
                h = 360
                if f[2][0] == f[2][1]:
                    w = 256
                    h = 256
                size = '{}x{}'.format(w, h)
                os.system('convert {} -resize {} {}'.format(f[1], size, f[1]))
        except Exception:
            return 'img/youtube_default.png'
    return f[1]


class KeyboardButton(QPushButton):
    def __init__(self, value):
        super().__init__(value)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setStyleSheet('''
            KeyboardButton {
                width: 100px;
                height: 70px;
                padding: 3px;
                font-size: 30px;
            }
            KeyboardButton:hover, KeyboardButton:focus {
                background: rgb(128,128,128);
            }
            KeyboardButton:pressed, KeyboardButton:focus:pressed {
                background: rgb(100,100,100);
            }
        ''')
        self.val = value
        self.clicked.connect(self._click)

    @click_protection
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Down, Qt.Key_Up, Qt.Key_Left, Qt.Key_Right, Qt.Key_Escape):
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
    position = [0, 0]

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

    @click_protection
    def keyPressEvent(self, event, button=None):
        row_count = self.layout.rowCount()
        cols_count = self.layout.columnCount()
        pos = self.layout.getItemPosition(self.layout.indexOf(button))
        if event.key() == Qt.Key_Down:
            if pos[0] < row_count - 1:
                item = self.layout.itemAtPosition(pos[0]+1, pos[1])
                if item:
                    item.widget().setFocus()
                    self.position[0] = pos[0]+1
                else:
                    self.layout.itemAtPosition(pos[0]+1, 1).widget().setFocus()
                    self.position = [pos[0]+1, 1]
            else:
                self.parent().keyPressEvent(event, self)
        elif event.key() == Qt.Key_Up and pos[0]:
            self.layout.itemAtPosition(pos[0]-1, pos[1]).widget().setFocus()
            self.position[0] = pos[0]-1
        elif event.key() == Qt.Key_Left:
            if pos[1]:
                self.layout.itemAtPosition(pos[0], pos[1]-1).widget().setFocus()
                self.position[1] = pos[1]-1
            else:
                self.parent().keyPressEvent(event, self)
        elif event.key() == Qt.Key_Right:
            if pos[1] < cols_count - 1:
                self.layout.itemAtPosition(pos[0], pos[1]+1).widget().setFocus()
                self.position[1] = pos[1]+1
            else:
                self.parent().keyPressEvent(event, self)
        elif event.key() == Qt.Key_Escape:
            self.parent().keyPressEvent(event, self)

    def setFocus(self):
        super().setFocus()
        item = self.layout.itemAtPosition(*self.position)
        item and item.widget().setFocus() or self.layout.itemAt(0).widget().setFocus()

    def show(self, ktype):
        try:
            while self.layout.count():
                c = self.layout.takeAt(0)
                c.widget().deleteLater()
        except RuntimeError:
            self.__init__(parrent=self.parent(), input_field=self.input_field)

        for ri, row in enumerate(getattr(self, '{}_keys'.format(ktype), [])):
            for ci, col in enumerate(row):
                btn = KeyboardButton(col)
                btn.click_handler = self.handle_button
                self.layout.addWidget(btn, ri, ci)
        self.setFocus()

    def handle_button(self, btn):
        val = btn.val.lower()
        if len(val) == 1 or val == 'space':
            self.input_field.insert(val == 'space' and ' ' or val)
        elif val in ('en', 'ru', '123'):
            self.show(val == '123' and 'digital' or val)
        elif val == '<x':
            self.input_field.backspace()
        elif val == 'clear':
            self.input_field.clear()
        elif val == 'enter':
            self.input_field.submit()


class KeyboardTips(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setStyleSheet('''
            KeyboardTips {
                font-size: 30px;
            }
        ''')

    @click_protection
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.parent().keyPressEvent(event, self)
        else:
            super().keyPressEvent(event)


class ResultList(QListWidget):
    def __init__(self, *args, activated=None, render_more=None, **kwargs):
        super().__init__(*args, flow=QListView.LeftToRight, **kwargs)
        self.setViewMode(QListView.IconMode)
        self.setWrapping(False)
        self.setWordWrap(True)
        self.setIconSize(QSize(360, 480))
        self.setFixedHeight(400)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        if activated:
            self.itemActivated.connect(activated)
        if render_more:
            self.render_more = render_more

        self.setAttribute(Qt.WA_StyledBackground)
        self.setStyleSheet('''
            ResultList:item:focus:selected {
                background-color: rgb(100,100,100);
            }
            ResultList:focus {
                background-color: rgb(80,80,80);
            }
        ''')

    @click_protection
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            selected = self.selectedItems()[0]
            if self.row(selected) >= self.count() - 1:
                self.render_more(selected)
        super().keyPressEvent(event)

    def render_more(self, item):
        print(item)


class YouTubeView(QWidget):
    search_rendered = False
    channel_rendered = False
    api = requests.session()
    current_focus = 0
    results = []
    rendered = False
    recs = []
    rec_next = None
    rec_continuation = None
    rec_end = False
    api_data = {
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
    search_tips_data = {
        "client": "youtube-lr",
        "ds": "yt",
        "hl": "ru_RU",
        "xhr": "t",
        "oe": "utf-8",
        "q": ""
    }
    cookies = {}

    def __init__(self, parent=None):
        super().__init__(parent)
        if os.path.isfile('cache/cookies'):
            with open('cache/cookies', 'rb') as f:
                self.cookies = pickle.load(f)
                self.api.cookies = requests.utils.cookiejar_from_dict(self.cookies)

        #self.parent = parent
        self.search = QLineEdit()
        self.search.keyPressEvent = self.search_activated
        self.search.submit = self.do_search
        self.search.textChanged.connect(self.tips_update)

        self.init_keyboard()

        self.layout = QVBoxLayout()
        #self.layout.setLabelAlignment(Qt.AlignHorizontal_Mask)

        self.search_layout = QHBoxLayout()
        self.search_layout.addWidget(QLabel('Search'))
        self.search_layout.addWidget(self.search)
        self.layout.addLayout(self.search_layout)
        self.layout.setContentsMargins(70, 50, 70, 50)
        self.layout.setSpacing(0)

    def init_keyboard(self):
        self.keyboard_layout = QHBoxLayout()
        self.keyboard = Keyboard(input_field=self.search)
        self.keyboard_tips = KeyboardTips()
        self.keyboard_tips.itemActivated.connect(self.set_search_from_tip)
        self.keyboard_layout.addWidget(self.keyboard_tips)
        self.keyboard_layout.addWidget(self.keyboard)

        self.results = ResultList(activated=self.activate_item, render_more=self.search_continue)
        self.results_layout = QVBoxLayout()
        self.results_layout.addWidget(QLabel('Results'))
        self.results_layout.addWidget(self.results)

    def render(self):
        print('RENDER')
        self.setLayout(self.layout)
        self.recomendations()
        self.rendered = True

    def get(self, *args, **kwargs):
        kwargs['headers'] = {'Content-Type': 'application/json'}
        res = self.api.get(*args, **kwargs, cookies=self.cookies)
        with open('cache/cookies', 'wb+') as f:
            self.cookies.update(requests.utils.dict_from_cookiejar(self.api.cookies))
            pickle.dump(self.cookies, f)
        return res

    def post(self, *args, **kwargs):
        kwargs['headers'] = {'Content-Type': 'application/json'}
        res = self.api.post(*args, **kwargs, cookies=self.cookies)
        with open('cache/cookies', 'wb+') as f:
            self.cookies.update(requests.utils.dict_from_cookiejar(self.api.cookies))
            pickle.dump(self.cookies, f)
        return res

    #def show(self):
    #    self.setLayout(self.layout)

    def setFocus(self):
        super().setFocus()
        self.current_focus = 0
        w = self.layout.itemAt(self.current_focus).itemAt(1).widget()
        w.setFocus()
        self.window().container.ensureWidgetVisible(w, 0, 0)
        _si = lambda: True
        not getattr(w, 'selectedItems', _si)() and w.item(0) and w.item(0).setSelected(True)
        #print(self.layout.takeAt(self.current_focus))
       # print(w)
       # w.setFocus()
        #w.setCurrentRow(1)

    @click_protection
    def keyPressEvent(self, event, elem=None):
        print(event.key())
        print(self.cookies)
        w = None
        _si = lambda: True

        if event.key() == Qt.Key_Escape:
            if self.search_rendered and self.channel_rendered:
                e = type('Obj', (), {'key': lambda self: Qt.Key_Return})()
                self.search_activated(e)
                self.channel_rendered = False
            elif self.channel_rendered:
                self.clear_results()
                self.recomendations(init=True)
            elif self.search_rendered:
                self.clear_results()
                self.recomendations(init=True)
                self.search_rendered = False
            else:
                self.window().keyPressEvent(event)
        elif event.key() == Qt.Key_Down:
            if self.current_focus >= self.layout.count() - 1 and not self.rec_end:
                self.recomendations()
            w = self.layout.itemAt(self.current_focus+1).itemAt(1).widget()
            w.setFocus()

            not getattr(w, 'selectedItems', _si)() and w.item(0) and w.item(0).setSelected(True)
            self.current_focus += 1
        elif event.key() == Qt.Key_Up:
            item = self.layout.itemAt(self.current_focus-1)
            w = item and item.itemAt(1).widget() or None
            w and w.setFocus()
            w and not getattr(w, 'selectedItems', _si)() and w.item(0) and w.item(0).setSelected(True)

            self.current_focus -= 1
        elif event.key() == Qt.Key_Left:
            if elem == self.keyboard:
                self.keyboard_layout.itemAt(0).widget().setFocus()
            else:
                self.window().categories.show()
                self.window().categories.categories_list.setFocus()
        elif event.key() == Qt.Key_Right:
            if elem == self.keyboard_tips:
                self.keyboard.setFocus()
        self.window().container.ensureWidgetVisible(w, 0, 0)

    def activate_item(self, item):
        if hasattr(item, 'video_id') and item.video_id:
            self.play(item.video_id, item.playlist_id, item.yt_params, item.title, item.img)
        elif hasattr(item, 'channel_id') and item.channel_id:
            self.render_channel(item.channel_id, item.tracking_params)

    def play(self, video_id, playlist_id, params, title, img):
        self.get('https://www.youtube.com/watch?v={}'.format(video_id))
        data = self.api_data.copy()
        data.pop('browseId', None)
        data.update({
            'contentCheckOk': True,
            'racyCheckOk': True,
            'playlistId': playlist_id,
            'videoId': video_id
        })

        if params:
            data['params'] = params

        url = '{}{}?key={}'.format(conf.YOUTUBE_API, 'next', conf.YOUTUBE_API_KEY)
        res = self.post(url, data=json.dumps(data))
        res = res.json()
        content = res['contents']['singleColumnWatchNextResults']['pivot']['pivot']
        cont = content['contents'][0]['pivotShelfRenderer'].get('content')

        if not cont:
            QMessageBox.about(self, u'Видео недоступно', u'Это видео недоступно')
            return None

        plst = cont['pivotHorizontalListRenderer']
        playlist = [['https://www.youtube.com/watch?v={}'.format(video_id), title, img]]
        rows = []

        for row in plst['items']:
            r = row.get('pivotVideoRenderer')
            if r:
                url = 'https://www.youtube.com/watch?v={}'.format(r['videoId'])
                playlist.append([url, r['title']['runs'][0]['text'], None])
                rows.append(row)

        images = self.cache_images(rows)
        for i, img in enumerate(images):
            playlist[i+1][2] = img

        self.window().player.playlist = playlist
        self.window().player.current_index = plst.get('selectedIndex', 0)

        continuations = plst.get('continuations')
        if continuations:
            continuation = continuations[0]['nextContinuationData']['continuation']
            click_tracking_params = continuations[0]['nextContinuationData']['clickTrackingParams']
            self.window().player.new_playlist_items = self.next_playlist(continuation, click_tracking_params)
        self.window().player.play()
        self.window().setFocus()

    def next_playlist(self, conts, ctp):
        def get_next_items():
            continuation = conts
            click_tracking_params = ctp
            data = self.api_data.copy()
            data.pop('browseId', None)
            data['continuation'] = continuation
            data['context'].update({
                'clickTracking': {
                    'clickTrackingParams': click_tracking_params,
                }
            })

            url = '{}{}?key={}'.format(conf.YOUTUBE_API, 'next', conf.YOUTUBE_API_KEY)
            res = self.post(url, data=json.dumps(data))
            res = res.json()

            cont = res['continuationContents']['pivotHorizontalListContinuation']
            playlist = []
            rows = []
            for row in cont['items']:
                r = row.get('pivotVideoRenderer')
                if r:
                    url = 'https://www.youtube.com/watch?v={}'.format(r['videoId'])
                    playlist.append([url, r['title']['runs'][0]['text'], None])
                    rows.append(row)

            images = self.cache_images(rows)
            for i, img in enumerate(images):
                playlist[i][2] = img

            continuations = cont.get('continuations')
            if continuations:
                continuation = continuations[0]['nextContinuationData']['continuation']
                click_tracking_params = continuations[0]['nextContinuationData']['clickTrackingParams']
                self.window().player.new_playlist_items = self.next_playlist(continuation, click_tracking_params)
            else:
                self.window().player.new_playlist_items = lambda self: []

            return playlist
        return get_next_items

    def render_channel(self, id, tracking_params):
        self.setFocus()
        self.clear_results()
        self.recomendations(browse_id=id, tracking_params=tracking_params)
        print('Render channel', id)
        self.channel_rendered = True

    def recomendations(self, browse_id=None, tracking_params=None, init=False):
        _tmp = self.get('https://www.youtube.com/tv').text
        del _tmp
        url = '{}{}?key={}'.format(conf.YOUTUBE_API, 'browse', conf.YOUTUBE_API_KEY)
        data = self.api_data.copy()
        data['browseId'] = browse_id or 'default'
        if tracking_params:
            data['context']['clickTracking'] = {"clickTrackingParams": tracking_params}
        elif self.rec_next and self.rec_continuation and not init:
            data['context']['clickTracking'] = {"clickTrackingParams": self.rec_next}
            data['continuation'] = self.rec_continuation
            #data.pop('browseId', None)
        res = self.post(url, data=json.dumps(data))
        res = res.json()

        if self.rec_next and self.rec_continuation and 'continuationContents' in res:
            content = res['continuationContents']['sectionListContinuation']['contents']
            continuations = res['continuationContents']['sectionListContinuation'].get('continuations', [{}])
        else:
            content = res['contents']['sectionListRenderer']['contents']
            continuations = res['contents']['sectionListRenderer'].get('continuations', [{}])

        first_w = None
        for row in content:
            section = QVBoxLayout()
            section_title = row['shelfRenderer'].get('title', '')
            if section_title:
                section_title = section_title['runs'][0]['text']

            section.addWidget(QLabel(section_title))

            list_widget = ResultList()

            items = self.render_row_result(row['shelfRenderer']['content']['horizontalListRenderer']['items'])
            for item in items:
                list_widget.addItem(item)
            del items
            list_widget.itemActivated.connect(self.activate_item)
            section.addWidget(list_widget)
            self.recs.append(section)
            self.layout.addLayout(section)
            first_w = not first_w and list_widget or first_w
        self.rec_next = continuations[0].get('nextContinuationData', {}).get('clickTrackingParams')
        self.rec_continuation = continuations[0].get('nextContinuationData', {}).get('continuation')
        self.window().container.ensureWidgetVisible(first_w, 0, 0)
        self.search.setFocus()

    @click_protection
    def search_activated(self, event):
        if event.key() == Qt.Key_Return:
            self.clear_results()
            self.init_keyboard()
            self.layout.addLayout(self.keyboard_layout)
            self.keyboard.show('ru')
            self.layout.addLayout(self.results_layout)
            self.current_focus = 1
            self.tips_update()
            self.search_rendered = True
        elif event.key() in (Qt.Key_Up, Qt.Key_Right, Qt.Key_Down, Qt.Key_Left):
            self.keyPressEvent(event)

    def clear_results(self):
        while self.layout.count() > 1:
            c = self.layout.takeAt(1)
            w0 = c.itemAt(0).widget()
            w0 and w0.deleteLater()
            w1 = c.itemAt(1).widget()

            while hasattr(w1, 'count') and w1.count():
                w1.removeItemWidget(w1.takeItem(0))
            w1 and hasattr(w1, 'clear') and w1.clear()
            w1 and w1.deleteLater()

        gc.collect(0)

    def tips_update(self):
        data = self.search_tips_data.copy()
        data['q'] = self.search.text()
        res = self.get(conf.YOUTUBE_SEARCH_TIPS_API, params=data)
        if res.ok:
            while self.keyboard_tips.count():
                self.keyboard_tips.takeItem(0)

            self.keyboard_tips.insertItems(0, [i[0] for i in res.json()[1]])

    def search_continue(self, last_item):
        self.do_search(False)

    def do_search(self, init=True):
        _null = self.get('https://www.youtube.com/results', params={'search_query': self.search.text()}).text
        del _null
        url = '{}{}?key={}'.format(conf.YOUTUBE_API, 'search', conf.YOUTUBE_API_KEY)
        data = self.api_data.copy()
        data.pop('browseId', None)
        if not init:
            data['continuation'] = self.results.continuation['continuation']
            data['context']['clickTracking'] = {'clickTrackingParams': self.results.continuation['clickTrackingParams']}
        else:
            data['query'] = self.search.text()

        res = self.post(url, data=json.dumps(data))
        res = res.json()

        if init:
            isr = res['contents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']
        else:
            isr = res['continuationContents']['itemSectionContinuation']
        contents = isr['contents']
        self.results.continuation = isr['continuations'][0]['nextContinuationData']
        self.set_results(self.render_row_result(contents), init)
        self.results.setFocus()
        if init:
            self.results.item(0).setSelected(True)

    def set_search_from_tip(self, item):
        self.search.clear()
        self.search.insert(item.text())
        self.search.submit()

    def set_results(self, items, init):
        if init:
            while self.results.count():
                self.results.takeItem(0)
        for item in items:
            self.results.addItem(item)
        del items

    def render_row_result(self, row):
        items = []

        images = self.cache_images(row)

        for i, col in enumerate(row):
            if 'gridButtonRenderer' in col:
                item = QListWidgetItem(QIcon('img/nav/ontop.png'), 'ON TOP')
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
                item.video_id = None
                item.channel_id = None
                items.append(item)
                self.rec_end = True
                item.setSelected(True)
                break

            keys = (
                'gridVideoRenderer',
                'gridChannelRenderer',
                'gridPlaylistRenderer',
                'pivotVideoRenderer',
                'pivotChannelRenderer',
                'pivotPlaylistRenderer',
                'compactVideoRenderer',
                'compactChannelRenderer',
                'compactPlaylistRenderer'
            )
            for key in keys:
                it = col.get(key)
                if it:
                    break
            else:
                continue

            title = it['title']['runs'][0]['text'][:32]
            if len(title) < len(it['title']['runs'][0]['text']):
                title += '...'

            badges = it.get('badges')
            mode = ''
            if badges and 'textBadge' in badges[0]:
                mode = '[{}] '.format(badges[0]['textBadge']['label']['runs'][0]['text'])

            try:
                item = QListWidgetItem(QIcon(images[i]), '{}{}'.format(mode, title))
                img = images[i]
            except IndexError as e:
                item = QListWidgetItem(QIcon('img/youtube_default.png'), '{}{}'.format(mode, title))
                img = 'img/youtube_default.png'
                print(i, images)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
            item.video_id = it.get('videoId', it.get('navigationEndpoint', {}).get('watchEndpoint', {}).get('videoId'))
            item.yt_params = it.get('navigationEndpoint', {}).get('watchEndpoint', {}).get('params')
            item.channel_id = it.get('channelId')
            item.tracking_params = it.get('trackingParams')
            item.playlist_id = it.get('navigationEndpoint', {}).get('watchEndpoint', {}).get('playlistId')
            item.title = title
            item.img = img
            items.append(item)
        del images
        return items

    def cache_images(self, row):
        size = (480, 360)
        images = []
        pool = Pool(processes=16)
        for col in row:
            keys = (
                'gridVideoRenderer',
                'gridChannelRenderer',
                'gridPlaylistRenderer',
                'pivotVideoRenderer',
                'pivotChannelRenderer',
                'pivotPlaylistRenderer',
                'compactVideoRenderer',
                'compactChannelRenderer',
                'compactPlaylistRenderer'
            )
            for key in keys:
                it = col.get(key)
                if it:
                    break
            else:
                filepath = 'img/youtube_default.png'
                images.append((None, filepath, size))
                continue

            thumb = it.get('thumbnail')
            if thumb:
                thumbs = thumb['thumbnails']
                for t in thumbs:
                    if t['height'] >= 360:
                        thumb = t['url']
                        size = (t['width'], t['height'])
                        break
                else:
                    thumb = thumbs[-1]['url']
                    size = (t['width'], t['height'])

                url = not thumb.startswith('http') and 'https:{}'.format(thumb) or thumb
                filepath = 'cache/{}'.format(thumb.replace('/', '_'))
                images.append((url, filepath, size))
            else:
                filepath = 'img/youtube_default.png'
                images.append((None, filepath, size))
        result = pool.map(cache_image, images)
        pool.terminate()
        return result
