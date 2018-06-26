import time

def click_protection(f, s=None):
    pause = 0.2
    def ws(self, event, *args, **kwargs):
        if not hasattr(self, 'keys_time'):
            self.keys_time = {}

        if (time.time() - self.keys_time.get(event.key(), 0)) > pause:
            self.keys_time[event.key()] = time.time()
            return f(self, event, *args, **kwargs)
        return

    def w(event, *args, **kwargs):
        if not hasattr(s, 'keys_time'):
            s.keys_time = {}

        if (time.time() - s.keys_time.get(event.key(), 0)) > pause:
            s.keys_time[event.key()] = time.time()
            return f(event, *args, **kwargs)
        return
    if s is None:
        return ws
    return w
