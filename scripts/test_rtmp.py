import cv2
import time
import face_recognition as fr
from pathlib import Path
from fire.face.face_recognize import SimpleFaceRecognizer
from fire.video import VideoStream

video_url = r"rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcigyNDkpL3N0cmVhbT9zdWJ0eXBlPVByaXZhdGVfaG9uZXk="


cap = cv2.VideoCapture(video_url)

video = VideoStream(video_url, device_id="")
video.start()

while True:

    frame = video.read_current_frame()
    # if frame is None:
    #     time.sleep(1)
    #     continue

    if frame is None:
        time.sleep(1)
        continue

    frame = cv2.resize(frame, (800, 600))
    # out.write(frame)
    cv2.imshow("frame", frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
    time.sleep(2)

cv2.destroyAllWindows()

video.close()