import json
import ts3lib
import isodate
import requests
import ts3defines

from hashlib import md5

def schid():
    _schid = ts3lib.getCurrentServerConnectionHandlerID()

    if not _schid:
        _schid = 1

    return _schid

def me():
    err, uid = ts3lib.getClientID(schid())
    return uid, err

def ume():
    id, err = me()

    if err:
        return None, err

    err, uid = ts3lib.getClientVariableAsString(schid(), id, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)

    return uid, err


def send(userid, message = None):

    if not userid:
        useid, err = me()
        if err:
            return err

    if type(userid) is tuple:
        if userid[1]:
            return userid[1]

        userid = userid[0]


    if not message:
        return 'no message'

    return ts3lib.requestSendPrivateTextMsg(schid(), message, userid)

def error(userid, message):
    return send(userid, "[[COLOR=RED]error[/COLOR]] " + message)

def info(userid, message):
    return send(userid, "[[COLOR=GREEN]info[/COLOR]] " + message)

def debug(message):
    ts3lib.printMessageToCurrentTab(message)
    print(message)

def csend(message):
    if message == None: return 'no message'

    err, client = ts3lib.getClientID(schid())

    if err:
        return err

    err, channelid = ts3lib.getChannelOfClient(schid(), client)

    if err:
        return err

    return ts3lib.requestSendChannelTextMsg(schid(), message, channelid)

def cerror(message):
    return csend("[[COLOR=RED]error[/COLOR]] " + message)

def cinfo(message):
    return csend("[[COLOR=GREEN]info[/COLOR]] " + message)

def avatar(img):
    hash_md5 = md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    ts3lib.setClientSelfVariableAsString(schid(), ts3defines.ClientPropertiesRare.CLIENT_FLAG_AVATAR, hash_md5.hexdigest())
    ts3lib.flushClientSelfUpdates(schid())

def parse_url(url):
    if url[:5] == '[URL]':
        url = url[5:]

    if url[-6:] == '[/URL]':
        url = url[:-6]

    path = url.split('v=')
    id = (path[1] if len(path) > 1 else '').split('&')[0]
    id = None if id == '' else id

    path = url.split('list=')
    list = (path[1] if len(path) > 1 else '').split('&')[0]
    list = None if list == '' else list

    path = url.split('index=')
    index = int((path[1] if len(path) > 1 else '1').split('&')[0])

    return id, list, index, url

def fetch_playlist(id, api_key, token = '', videos = []):
    resp = requests.get(url = "https://www.googleapis.com/youtube/v3/playlistItems", params = {
        'key': api_key,
        'part': 'snippet',
        'maxResults': 50,
        'playlistId': id,
        'pageToken': token,
    })

    data = json.loads(resp.text)

    if data.get('error'):
        err = data.get('error').get('errors')[0].get('message')
        return err, videos

    for item in data.get('items'):
        video = item.get('snippet')
        videos.append(video.get('resourceId').get('videoId'))

    if data.get('nextPageToken'):
        return fetch_playlist(id, api_key, data.get('nextPageToken'), videos)

    return None, videos

def yt_get_duration(url, token):
    id = parse_url(url)

    resp = requests.get(url = "https://www.googleapis.com/youtube/v3/videos", params = {
        'key': token,
        'part': 'contentDetails',
        'id': id,
    })

    data = json.loads(resp.text)

    if data.get('error'):
        return data.get('error').get('errors')[0].get('message'), None

    duration = data.get('items')[0].get('contentDetails').get('duration')

    return None, isodate.parse_duration(duration).total_seconds()

def yt_get_name(url, token):
    id = parse_url(url)

    resp = requests.get(url = "https://www.googleapis.com/youtube/v3/videos", params = {
        'key': token,
        'part': 'snippet',
        'id': id,
    })

    data = json.loads(resp.text)

    if data.get('error'):
        return data.get('error').get('errors')[0].get('message'), None

    return None, data.get('items')[0].get('snippet').get('title')
#.encode('ascii', 'xmlcharrefreplace')
