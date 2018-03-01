import mpv

class Player(object):
    url = None

    def __init__(self, winid):
        self._player = mpv.MPV(
            wid=winid,
            ytdl=True,
            vo='vdpau',
            log_handler=print,
            save_position_on_quit=True
        )

    def set_url(self, url):
        self.url = url

    def play(self):
        self._player.play(self.url)

    def stop(self):
        self._player.stop()

    def pause(self):
        self._player.pause()
