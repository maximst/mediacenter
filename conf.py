YOUTUBE_API = 'https://www.youtube.com/youtubei/v1/'
YOUTUBE_SEARCH_TIPS_API = 'https://clients1.google.com/complete/search'
YOUTUBE_API_KEY = ''

MPV_VO = 'vdpau'

MEDIA_SERVER = 'localhost:8080'

try:
    from local_conf import *
except:
    pass
