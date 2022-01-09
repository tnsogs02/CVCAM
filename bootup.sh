#!/bin/sh
### BEGIN INIT INFO
# Provides: bootup.sh
# Required-Start:
# Required-Stop:
# Should-Start:      
# Default-Start: 5
# Default-Stop:
# Short-Description:
# Description:
### END INIT INFO
while [ ! -d "/media/pi/SAVE"]; do
    sleep 5
done
sudo modprobe -r v4l2loopback
sudo modprobe v4l2loopback video_nr=49,50
sudo service vsftpd start
sudo service nginx start
ffmpeg -f video4linux2 -i /dev/video0 -codec copy -f v4l2 /dev/video49 -codec copy -f v4l2 /dev/video50&
sleep 5 && gst-launch-1.0 -v v4l2src device=/dev/video49 ! queue ! videoconvert ! omxh264enc !  h264parse ! flvmux ! rtmpsink location='rtmp://localhost:1935/demo/test'&
sleep 5 && python3 /media/pi/SAVE/cvcam.py
