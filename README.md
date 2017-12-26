ts3-musicbot
=======

A python script that creates command interface and plays Youtube streams through VLC using [pyTSon](https://github.com/pathmann/pyTSon)

Getting Started
---------------

```bash
$ cd ~/.ts3client/plugins/pyTSon/scripts
$ git clone https://github.com/wvffle/ts3-musicbot.git
```

#### Requirements
- pulseaudio
- vlc
- requests (python module)

#### Installation
Unfortunately, pyTSon cannot change your teamspeak client settings, so there are some requirements to do ;/

1. pyTSon
    - Enable script
    - Configure [Youtube API key](https://developers.google.com/youtube/v3/getting-started) in script settings
    - Configure bot name in script settings
2. Teamspeak
    - Go to `Tools > Options > Playback`
        - Set `Voice Volume Adjustment` to -40.0 dB
        - Set `Sound Pack Volume` to -40.0 dB
    - Go to `Tools > Options > Capture`
        - Set `Capture Mode` to `PulseAudio`
        - Check `Voice Activation Detection`
        - Set the slider to -50.0 dB

#### Usage
Whole bot is controlled over chat commands
A chat command starts with `!` and is followed by command name and arguments

```bash
!cmd arg1 arg2 arg3
```

Available commands:
```bash
!yt <video url|playlist url|search text>   # add video / playlist to queue or find a video / playlist and add to queue
!stop                                      # stop the playlist
!play                                      # resume the playlist
!skip                                      # skip current song
!queue [<page>]                            # display queue
!q [<page>]                                # alias for !queue
!clear                                     # clear queue
```
