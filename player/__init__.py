import os
import json
import time
import pytson
import urllib
import requests
import traceback

from musicbot.util import *
from PythonQt.QtCore import QUrl
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest

class VLC():
    def __init__(self, api_key, port = 8080, passw = '123'):
        os.system('/usr/bin/pkill -9 vlc')
        os.system(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'vlc.sh') + f' {passw}')

        self.auth   = requests.auth.HTTPBasicAuth('', passw)
        self.host   = f'http://127.0.0.1:{port}/'
        self.req    = self.host + 'requests/'
        self.controll = self.req + 'status.json?command='

    # documented on:
    # https://github.com/videolan/vlc/tree/master/share/lua/http/requests

    def stop(self):
        requests.get(self.controll + 'pl_stop', auth=self.auth)

    def play(self):
        requests.get(self.controll + 'pl_play', auth=self.auth)

    def skip(self):
        requests.get(self.controll + 'pl_next', auth=self.auth)

        meta = self.meta()
        if len(meta) > 0:
            self.dequeue(meta[0].get('id'))

    def clear(self):
        requests.get(self.controll + 'pl_empty', auth=self.auth)

    def dequeue(self, id):
        requests.get(self.controll + 'pl_delete&id=' + id, auth=self.auth)

    def enqueue(self, id):
        requests.get(self.controll + 'in_enqueue&input=' + urllib.parse.quote_plus('https://youtube.com/watch?v=' + id), auth=self.auth)

    def meta(self):
        resp = requests.get(self.req + 'playlist.json', auth=self.auth)
        data = json.loads(resp.text)
        return data.get('children')[0].get('children')
