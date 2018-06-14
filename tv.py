import re
import requests
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


CHASTV_QUERY = ''


def update_chastv(r):
    r = r or re.compile('wmsAuthSign\=[^"^ ]+')
    global CHASTV_QUERY

    resp = requests.get('http://chas.tv/channel/pervyi')
    rs = r.search(resp.text)
    if rs:
        CHASTV_QUERY = rs.group()

    resp = requests.get('https://chas.tv/channel/rossiya-1')
    rs = r.search(resp.text)
    if rs:
        CHASTV_QUERY = rs.group()


class URLS(object):
    ntv_re = re.compile('\/\/mob3\-ntv\.cdnvideo\.ru\/ntv\/smil\:ntvair003\.smil\/playlist\.m3u8\?e\=[0-9]+\&md5=[^\']+')
    five_re = re.compile('\/watch\?v=[^"]+')


    @classmethod
    def sts(cls):
        return 'http://178.162.218.83:8081/chas/sts-hq.stream/chunks.m3u8?{}'.format(CHASTV_QUERY)

    @classmethod
    def tnt(cls):
        url = ''
        resp = requests.get('http://192.168.1.1:8080/tnt.json')
        f = open('cache/storage.json', 'rw+')
        fc = f.read()
        st = {}
        if fc:
            st = json.loads(fc)

        try:
            rsp = list(requests.get(resp.json['live_streams']['hls'][0]['url']).iter_lines())
            rsp.reverse()
            for st in rsp:
                if st:
                    url = st.split('?')[0]
                    st['tnt_url'] = url
                    f.write(json.dumps(st))

        except Exception:
            url = st.get('tnt_url')

        f.close()

        url = url or 'http://cdn-01.bonus-tv.ru/btv/sm-tnt/type/user/devname/LG-SmartTV/devid/LG-1477141994/eol/20200101T0000/hash/ec3a7b7757181408093b5c1ee40a288028a9ba15/chunklist_b2128000.m3u8?fake'

        return url

    @classmethod
    def ntv(cls):
        res = requests.get('http://www.ntv.ru/air/')
        sr = cls.ntv_re.search(res.text)
        if sr:
            url = sr.group().replace('playlist', 'chunklist_b1500000_DVR')
            return 'http:{}&hls_proxy_host=pub4.rtmp.s01.l.ntv'.format(url)
        return ''

    @classmethod
    def five(cls):
        resp = requests.get('https://www.youtube.com/channel/UCGM8ZTtduKll7X8RiGe6N8g')
        sr = cls.five_re.search(resp.text)
        if sr:
            return 'https://www.youtube.com{}'.format(sr.group())
        return ''

    @classmethod
    def che(self):
        return 'http://178.162.205.85:8081/chas/perec-hq.stream/playlist.m3u8?{}'.format(CHASTV_QUERY)

    @classmethod
    def x2(self):
        return 'http://178.162.205.85:8081/chas/dva-hq.stream/playlist.m3u8?{}'.format(CHASTV_QUERY)

    @classmethod
    def pyatnica(self):
        return 'http://178.162.218.87:8081/chas/pyatnica.stream/playlist.m3u8?{}'.format(CHASTV_QUERY)


CHANNELS = [
    [
        'Первый канал',
        'http://192.168.1.1:8080/hls-live10/streams/1tv/1tv5.m3u8',
        'HD',
        'perviy'
    ],
#    ['Россия 1', "http://192.168.1.1:8080/hls/russia_hd/playlist_vhig.m3u8", 'HD', 'rossia_1'],
    [
        'Россия 1',
        'http://cdn-01.bonus-tv.ru/btv/russiahd/type/user/devname/LG-SmartTV/devid/LG-1469703292/eol/20200101T0000/hash/1b7599c0021067fe3590d9ed45db70712b2b1ef8/track_0_2000/playlist.m3u8',
        'HD',
        'rossia_1'
    ],
    [
        'СТС',
        URLS.sts,
        'HD',
        'sts'
    ],
    [
        'СТС',
        'http://192.168.1.1:8080/hls-live10/streams/ctc/ctc3.m3u8',
        'SD',
        'sts'
    ],
#    ['ТНТ', "http://cdn-01.bonus-tv.ru/btv/sm-tnt/type/user/devname/LG-SmartTV/devid/LG-1477141994/eol/20200101T0000/hash/ec3a7b7757181408093b5c1ee40a288028a9ba15/chunklist_b2128000.m3u8", 'SD', 'tnt'],
    [
        'ТНТ',
        URLS.tnt,
        'HD',
        'tnt'
    ],
    [
        'Звезда',
        'https://cdn-01.bonus-tv.ru/zvezda/zvezda/type/none/eol/20200101T000000/hash/1/playlist.m3u8',
        'SD',
        'zvezda'
    ],
    [
        'НТВ',
        URLS.ntv,
        'SD',
        'ntv'
    ],
    [
        'РЕН ТВ',
        'http://192.168.1.1:8080/hls-live10/streams/ren-tv/ren-tv5.m3u8',
        'HD',
        'ren_tv'
    ],
    [
        'Пятый канал',
        URLS.five,
        'HD',
        'piatiy'
    ],
    [
        'МИР',
        'http://hls.mirtv.cdnvideo.ru/mirtv-parampublish/mirtv_2500/playlist.m3u8',
        'SD',
        'mir'
    ],
    [
        'МИР HD',
        'http://hls.mirtv.cdnvideo.ru/mirtv-parampublish/hd/playlist.m3u8',
        'FHD',
        'mir'
    ],
#    ['ТВЦ', URLS.tvc, 'SD', 'tvc'],
    [
        'ТВЦ',
        'http://tvc.cdnvideo.ru/tvc-p212/smil:tvc.smil/playlist.m3u8',
        'SD',
        'tvc'
    ],
    [
        'Че',
        URLS.che,
        'HD',
        'che'
    ],
    [
        '2x2',
        URLS.x2,
        'HD',
        '2x2'
    ],
    [
        'Пятница',
        URLS.pyatnica,
        'SD',
        'pyatnica'
    ],
#    ['Россия 24', "http://192.168.1.1:8080/live/smil:r24.smil/chunklist_b800000.m3u8", 'SD', 'rossia_24'],
    [
        'Россия 24',
        "http://cdnmg.secure.live.rtr-vesti.ru/live/smil:r24.smil/chunklist_b800000.m3u8",
        'SD',
        'rossia_24'
    ],
    [
        'RT Док',
        'https://rtmp.api.rt.com/hls/rtdru.m3u8',
        'HD',
        'rt_doc'
    ],
    [
        '1HD Music Television',
        'https://cdn-01.bonus-tv.ru:8090/1HDmusic/tracks-v2a1/index.m3u8',
        'FHD',
        '1hd_music_television'
    ],
    [
        'World Fashion Channel',
        'https://cdn-01.bonus-tv.ru:8090/wfcru/tracks-v1a1/index.m3u8',
        'HD',
        'world_fashion_channel'
    ],
    [
        'Fashion TV',
        'https://www.youtube.com/watch?v=MyDCoVf9nVE',
        'FHD',
        'fashion_tv'
    ]
]


class TVView(QWidget):
    rendered = False
    playlist = []
    chastv_re = re.compile('wmsAuthSign\=[^"^ ]+')

    def __init__(self, parent=None):
        super().__init__(parent)

        self.timer = QTimer()
        self.timer.timeout.connect(self._timer)
        self.timer.start(600000)
        update_chastv(self.chastv_re)

        for channel in CHANNELS:
            img = 'img/channels/{}.png'.format(channel[3])
            title = '{} [{}]'.format(channel[0], channel[2])
            self.playlist.append([channel[1], title, img])

    def _timer(self):
        update_chastv(self.chastv_re)

    def render(self):
        print('RENDER')
        self.window().player.set_icon_size(100, 100)
        self.window().player.playlist = self.playlist
        self.window().player.current_index = 0
        self.window().player.play()
        self.window().player.pause()
        self.window().setFocus()
        self.rendered = True
        self.window().setStyleSheet("""
            QScrollArea {
                background-image: url(./img/channels/cinema.jpg);
                background-size: auto 1080px;
            }
        """)

    def show(self):
        super().show()
        self.window().player.play()
        self.window().player.pause()
        self.window().setFocus()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Escape, Qt.Key_Right):
            self.window().categories.show()
            self.window().categories.widget().setFocus()
        elif event.key() == Qt.Key_Return and not self.window().player.is_playing:
            self.window().player.play()
            self.window().player.pause()
        super().keyPressEvent(event)
