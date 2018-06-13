import re
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class URLS(object):
    @classmethod
    def sts(self):
        return ''

    @classmethod
    def tnt(self):
        return ''

    @classmethod
    def ntv(self):
        res = requests.get('http://www.ntv.ru/air/')
        r = re.compile("\/\/mob3\-ntv\.cdnvideo\.ru\/ntv\/smil\:ntvair003\.smil\/playlist\.m3u8\?e\=[0-9]+\&md5=[^']+")
        sr = r.search(res.text)
        if sr:
            url = sr.group().replace('playlist', 'chunklist_b1500000_DVR')
            return 'http:{}&hls_proxy_host=pub4.rtmp.s01.l.ntv'.format(url)
        return ''

    @classmethod
    def five(self):
        return ''

    @classmethod
    def che(self):
        return ''

    @classmethod
    def x2(self):
        return ''

    @classmethod
    def pyatnica(self):
        return ''

    @classmethod
    def fashiontv(self):
        return ''


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
        'UHD',
        'fashion_tv'
    ]
]

class TVView(QWidget):
    rendered = False
    playlist = []

    def __init__(self, parent=None):
        super().__init__(parent)

        for channel in CHANNELS:
            img = 'img/channels/{}.png'.format(channel[3])
            title = '{} [{}]'.format(channel[0], channel[2])
            self.playlist.append([channel[1], title, img])

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
        elif event.key() == Qt.Key_Return:
            self.window().player.play()
            self.window().player.pause()
        super().keyPressEvent(event)
