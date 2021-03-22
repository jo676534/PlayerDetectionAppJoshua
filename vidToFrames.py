import cv2
import os
vidcap = cv2.VideoCapture('Sample Soccer Video.mp4')
dirname = 'vid2img'
os.mkdir(dirname)

def getFrame(sec):
    vidcap.set(cv2.CAP_PROP_POS_MSEC, sec*1000)
    hasFrames, image = vidcap.read()
    if hasFrames:
        cv2.imwrite(os.path.join(dirname,"image"+str(count) + ".jpg"), image)
    return hasFrames


sec = 0
frameRate = 0.0335
count = 1
success = getFrame(sec)
while success:
    count = count + 1
    sec = sec + frameRate
    sec = round(sec, 2)
    success = getFrame(sec)
