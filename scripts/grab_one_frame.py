import cv2
import time
import face_recognition as fr
from pathlib import Path
from fire.face.face_recognize import SimpleFaceRecognizer
from fire.video import VideoStream

video_url = r"rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcigyNDIpL3N0cmVhbT9zdWJ0eXBlPVByaXZhdGVfaG9uZXk="

folder = r"C:\Users\h232559\Desktop\test_imgs"

cap = cv2.VideoCapture(video_url)

video = VideoStream(video_url, device_id="")
video.start()

for i in range(1000):

    frame = video.read_current_frame()
    # frame = cv2.resize(frame, (800, 600))
    cv2.imwrite(r"C:\Users\h232559\Desktop\test_imgs\{}.jpg".format(i), frame)
    time.sleep(2)

video.close()

