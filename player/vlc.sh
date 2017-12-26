#!/bin/bash

# run new vlc instance on own sink in background
echo running new vlc instance
# check if sink exists
if [[ $(pacmd list-sinks | grep teamspeak -c) -eq 0 ]]
then

  # create sink
  echo creating new sink
  pacmd load-module module-null-sink sink_name=teamspeak sink_properties=device.description=Teamspeak

fi

echo running new vlc instance
sink=$(pacmd list-sinks | grep teamspeak -B1 | grep -oP "index: \K\d+")
PULSE_SINK=$sink vlc --no-video --http-password $1 -I http &
