import mpv
import conf


class Player(object):
    url = None
    is_playing = False
    win_id = None

    def __init__(self, winid):
        self.win_id = winid

    def set_url(self, url):
        self.url = url

    def play(self):
        self._player = mpv.MPV(
            wid=self.win_id,
            ytdl=True,
            vo=conf.MPV_VO,
            log_handler=print,
            #watch_later_directory='~/.config/mpv/watch_later'
        )
        self._player.play(self.url)
        self.is_playing = True

    def stop(self):
        self._player.quit_watch_later(0)
        self._player.terminate()
        self.is_playing = False

    def pause(self):
        self._player.pause()
