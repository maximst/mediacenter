import mpv

class Player(object):
    url = None

    def __init__(self, winid):
        self._player = mpv.MPV(wid=winid, vo='vdpau', log_handler=print)

    def set_url(self, url):
        self.url = url

    def play(self):
        self._player.play(self.url)
