import time
import numpy as np
import cv2
import json
from gpiozero import LED
from gpiozero import Buzzer
import board
import busio
import adafruit_lsm9ds0
startTime = time.time()
motion = False
usbDir = '/media/pi/SAVE'
with open(usbDir+'/config.json') as f:
  cfg = json.load(f)
buzzer = Buzzer(cfg['buzzer'])
statLED = LED(cfg['statLED'])
statLED.on()

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_lsm9ds0.LSM9DS0_I2C(i2c)

try:
  cap = cv2.VideoCapture(50)
  width = 1280
  height = 960
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
  ret, frame = cap.read()
  avg = cv2.blur(frame, (4, 4))
  avg_float = np.float32(avg)
  fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
  while(cap.isOpened()):
    accel_x, accel_y, accel_z = sensor.acceleration
    acc = pow((pow(accel_x,2)+pow(accel_y,2)+pow(accel_z,2)),0.5)
    print(acc)
    if abs(acc-cfg['accMid'])>=cfg['acc'] and (time.time() - startTime) > 10:
      buzzer.on()
      print('Warning! Camera has been moved!')
    statLED.on()
    cycTime = time.time()
    ret, frame = cap.read()
    if ret == False:
      break
    blur = cv2.blur(frame, (4, 4))
    diff = cv2.absdiff(avg, blur)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, cfg['thresh'], 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
      if cv2.contourArea(c) < cfg['contourValue']:
        continue
      mTime = time.time()
      if motion != True and cfg['recording'] == 'enable':
        motion = True
        stTime = time.time()
        filename = usbDir+'/'+time.strftime("%Y-%m-%d_%H%M%S", time.localtime())+'.mp4'
        out = cv2.VideoWriter(filename,fourcc,cfg['fps'],(640,480),isColor=True)
      (x, y, w, h) = cv2.boundingRect(c)
      cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    frame = cv2.resize(frame, (640, 480))
    if motion:
      out.write(frame)
      if (time.time() - mTime) > cfg['freezeLength']:
        motion = False
        out.release()
      if(time.time() - stTime) > cfg['videoMaxLength']:
        motion = False
        out.release()
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
    cv2.accumulateWeighted(blur, avg_float, 0.01)
    avg = cv2.convertScaleAbs(avg_float)
  cap.release()
  if motion:
    out.release()
    print('Saved')
  statLED.off()
except:
  if motion:
    out.release()
    print('ERROR')
  statLED.off()
