from musicbot.util import *
from base64 import b64encode
from ts3plugin import ts3plugin
from PythonQt.QtCore import QTimer
from configparser import ConfigParser
from PythonQt.QtCore import QIODevice, QFile
from musicbot.gui.configdialog import ConfigDialog

import os
import json
import time
import math
import ts3lib
import pytson
import requests
import traceback
import ts3defines
import musicbot.player

CONFIG = {}

class musicbot(ts3plugin):
    name = "musicbot"
    requestAutoload = True
    version = "1.0"
    apiVersion = 21
    author = "wvffle"
    description = "wvffle's music bot"
    offersConfigure = True
    commandKeyword = ""
    infoTitle = ""
    menuItems = []
    hotkeys = []

    music_queue = []

    moderators = [
        'BYMcL6d/yR5GNqcRB52qILPwRpc=',
    ]

    def __init__(self):
        global CONFIG


        self.dlg = None
        self.playing = False

        try:
            self.cfg_schema = {
                'token': ('',         'Youtube API Key'),
                'nick':  ('musicbot', 'Bot Nickname'   ),
            }

            self.cp = ConfigParser({k: v[0] for k, v in self.cfg_schema.items()})

            p = pytson.getConfigPath("musicbot.ini")
            if os.path.isfile(p):
                self.cp.read(p)

            CONFIG = self.cp['DEFAULT']
        except:
            debug(traceback.format_exc())

        self.vlc = player.VLC(CONFIG.get('token'))

        id, err = me()
        if not err:
            err, self.nick = ts3lib.getClientDisplayName(schid(), id)
            self.nickname()

        debug("[musicbot] enabled")

    def stop(self):
        if self.dlg:
            self.dlg.close()
            self.dlg = None

        with open(pytson.getConfigPath("musicbot.ini"), "w") as f:
            self.cp.write(f)

    def configure(self, parent):
        try:
            if not self.dlg:
                self.dlg = ConfigDialog(CONFIG, self.cfg_schema, self, parent)
            self.dlg.show()
            self.dlg.raise_()
        except:
            debug(traceback.format_exc())

    def cmd_clear(self, args, uid, uname, privilaged):
        if privilaged:
            pass
        else:
            error(uid, "no permission for that bro ;/")

    def cmd_q(self, args, uid, uname, privilaged):
        self.cmd_queue(args, uid, uname, privilaged)

    def cmd_queue(self, args, uid, uname, privilaged):

        tmp_playlist = []
        update_names = {}
        queue = []

        meta = self.vlc.meta()

        page = 0
        max_pages = math.floor(len(meta) / 10)

        if len(args) > 0:
            try:
                page = min(max(int(args[0]) - 1, 1), max_pages)
            except:
                page = 0

        for i, item in enumerate(meta[page * 10:(page + 1) * 10]):
            name = item.get('name')
            sid = item.get('id')

            if '?v=' in name:
                vid = name.split('?v=')[1].split('&')[0]
                update_names[vid] = None
                tmp_playlist.append(((i + 1) + 10 * page, vid, bool(item.get('current'))))
            else:
                tmp_playlist.append(((i + 1) + 10 * page, name, bool(item.get('current'))))

        if update_names:
            ids = []

            for vid in list(update_names):
                ids.append(vid)

            resp = requests.get(url = "https://www.googleapis.com/youtube/v3/videos", params = {
                'key': CONFIG.get('token'),
                'part': 'snippet',
                'id': ','.join(ids),
            })

            data = json.loads(resp.text)
            if data.get('error'):
                cerror(data.get('error').get('errors')[0].get('message'))

            for item in data.get('items'):
                name = item.get('snippet').get('title')
                vid = item.get('id')
                update_names[vid] = name

        for song in tmp_playlist:
            i = song[0]
            name = song[1]
            current = song[2]

            if update_names.get(name):
                name = update_names.get(name)

            queue.append(f'{i}. ' + ('[COLOR=#0AF]▶[/COLOR] ' if current else '') + name)

        if not len(queue):
            return info(uid, "add some thomas or somethin!")

        info(uid, f"[{page + 1}/{max_pages + 1}] current queue:\n" + '\n'.join(queue))

    def cmd_play(self, args, uid, uname, privilaged):
        if not self.playing:
            self.playing = True
            self.vlc.play()

            meta = self.vlc.meta()

            if not len(meta):
                return

            song = meta[0]
            name = song.get('name')
            duration = song.get('duration')


            if '?v=' in name:
                err, duration = yt_get_duration(name, CONFIG.get('token'))

                if err:
                    return debug(err)

                err, name = yt_get_name(name, CONFIG.get('token'))

                if err:
                    return debug(err)

            print(name, duration)

            self.nickname(song = name)
            cinfo(f'[COLOR=#0AF]▶[/COLOR] {name}')
            self.playing = False
            self.nickname()

    def cmd_stop(self, args, uid, uname, privilaged):
            self.vlc.stop()

    def cmd_skip(self, args, uid, uname, privilaged):
        name = self.vlc.meta()[1].get('name')

        if self.playing:
            self.vlc.skip()

        cinfo(f'[COLOR=#0AF]▶[/COLOR] {name}')

    def cmd_yt(self, args, uid, uname, privilaged):
        id, list, index, url =  parse_url(args[0])

        if list != None:
            err, playlist = fetch_playlist(list, CONFIG.get('token'))

            if err:
                error(uid, err)

            for video in playlist:
                self.vlc.enqueue(video)

            if len(playlist):
                resp = requests.get(url = "https://www.googleapis.com/youtube/v3/playlists", params = {
                    'key': CONFIG.get('token'),
                    'part': 'snippet',
                    'id': list,
                })

                data = json.loads(resp.text)

                if data.get('error'):
                    return

                info(uid, "[COLOR=#0AF]+[/COLOR] " + data.get('items')[0].get('snippet').get('title') + ' (playlist)')

        elif id != None:
            resp = requests.get(url = "https://www.googleapis.com/youtube/v3/videos", params = {
                'key': CONFIG.get('token'),
                'part': 'snippet',
                'id': id,
            })

            data = json.loads(resp.text)

            if data.get('error'):
                return error(uid, data.get('error').get('errors')[0].get('message'))

            title = data.get('items')[0].get('snippet').get('title')

            info(uid, "[COLOR=#0AF]+[/COLOR] " + title)

            self.vlc.enqueue(id)
        else:
            resp = requests.get(url = "https://www.googleapis.com/youtube/v3/search", params = {
                'q': ' '.join(args),
                'key': CONFIG.get('token'),
                'part': 'snippet',
                'type': 'video|playlist',
                'maxResults': 1,
            })

            data = json.loads(resp.text)

            if data.get('error'):
                return error(uid, data.get('error').get('errors')[0].get('message'))

            items = data.get('items')

            if len(items) == 0:
                info(uid, "song not found :c")

            item = items[0]

            id = item.get('id')
            snippet = item.get('snippet')

            if id.get('videoId'):
                info(uid, "[COLOR=#0AF]+[/COLOR] " + snippet.get('title'))
                self.vlc.enqueue(id.get('videoId'))

            if id.get('playlistId'):
                err, playlist = fetch_playlist(id.get('playlistId'), CONFIG.get('token'))

                if err:
                    error(uid, err)

                if len(playlist):
                    info(uid, "[COLOR=#0AF]+[/COLOR] " + snippet.get('title') + ' (playlist)')
                    self.music_queue = self.music_queue + playlist

        if not self.playing:
            self.cmd_play(args, uid, uname, privilaged)


    def onTextMessageEvent(self, _schid, targetMode, toID, fromID, fromName, fromUID, message, ffIgnored):
        err, myid = ts3lib.getClientID(schid())
        privilaged = fromUID in self.moderators

        if err != ts3defines.ERROR_ok:
            return False

        if message[0] == '!':
            args = message.split(' ')

            cmd = args.pop(0)

            debug("[" + fromUID + "] " + ('@' if privilaged else '') + fromName + ": " + message)

            def notFound():
                error(fromID, "commad '" + cmd[1:] + "' not found")

            try:
                getattr(self, "cmd_" + cmd[1:], notFound)(args, fromID, fromName, privilaged)
            except:
                debug(traceback.format_exc())

    def onConnectStatusChangeEvent(self, _schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            err, self.nick = ts3lib.getClientDisplayName(schid(), me()[0])
            self.nickname()

    def onConfigUpdate(self):
        self.nickname()

    def nickname(self, nick = None, song = None):
        MAX_SIZE = ts3defines.TS3_MAX_SIZE_CLIENT_NICKNAME_NONSDK

        if not nick:
            nick = CONFIG.get('nick')

        if self.nick == nick: return
        self.nick = nick

        if song:
            nick = f'{nick} [{ song[:(MAX_SIZE - len(nick) - 3)] }]'

        ts3lib.setClientSelfVariableAsString(schid(), ts3defines.ClientProperties.CLIENT_NICKNAME, nick)
        ts3lib.flushClientSelfUpdates(schid())

    def nextsong(self):
        meta = self.vlc.meta()

        if len(meta) > 0:
            self.vlc.dequeue(meta[0].get('id'))

        if len(meta) == 1 or not self.playing:
            self.playing = False
            self.nickname()
            return

        if len(meta) > 1:
            song = meta[1]
            name = song.get('name')
            duration = song.get('duration')

            if '?v=' in name:
                err, duration = yt_get_duration(name, CONFIG.get('token'))

                if err:
                    return debug(err)

                err, name = yt_get_name(name, CONFIG.get('token'))

                if err:
                    return debug(err)

            self.vlc.play()

            print(name, duration)
            self.nickname(song = name)
            cinfo(f'[COLOR=#0AF]▶[/COLOR] {name}')
            QTimer.singleShot(duration * 1000, self.nextsong)
