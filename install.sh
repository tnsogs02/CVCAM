#! /bin/bash
sudo apt-get update
sudo apt-get install nginx libnginx-mod-rtmp vsftpd gstreamer1.0-tools python3-gpiozero libatlas-base-dev -y
sudo pip3 install opencv-python adafruit-circuitpython-lsm9ds0 
sudo pip3 install -U numpy
sudo apt-get install --reinstall raspberrypi-bootloader raspberrypi-kernel -y
sudo apt-get install raspberrypi-kernel-headers v4l2loopback-dkms -y
sudo sh -c "echo 'rtmp{server{listen 1935;chunk_size 4096;application demo{live on;}}}' >> /etc/nginx/nginx.conf"
sudo sh -c "echo 'local_root=/media/pi/SAVE' >> /etc/vsftpd.conf"
sudo cp /media/pi/SAVE/bootup.sh /etc/init.d/bootup.sh
sudo chmod +x /etc/init.d/bootup.sh
sudo update-rc.d bootup.sh defaults
sudo reboot