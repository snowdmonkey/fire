import cv2
import time
import face_recognition as fr
from pathlib import Path
from fire.face.face_recognize import SimpleFaceRecognizer
from fire.video import VideoStream
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

# video_url = r"rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcigyNDIpL3N0cmVhbT9zdWJ0eXBlPVByaXZhdGVfaG9uZXk="
path = {"wenxiang": r"rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcigyNDkpL3N0cmVhbT9zdWJ0eXBlPVByaXZhdGVfaG9uZXk=",
        "yanxiang": r"rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcjJfMjQ1L3N0cmVhbT9zdWJ0eXBlPVByaXZhdGVfaG9uZXk="}

# cap = cv2.VideoCapture(video_url)

video = VideoStream(path.get("yanxiang"), device_id="")
video.start()

while True:

    frame = video.read_current_frame()
    # if frame is None:
    #     time.sleep(1)
    #     continue

    if frame is None:
        time.sleep(1)
        continue

    frame = cv2.resize(frame, dsize=None, fx=0.5, fy=0.5)
    # out.write(frame)
    cv2.imshow("frame", frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
    time.sleep(0.1)

cv2.destroyAllWindows()

video.close()