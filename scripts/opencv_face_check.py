import cv2

import logging
from pathlib import Path
import time
import cv2

from fire.face.face_recognize import SimpleFaceRecognizer

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger(__name__)

BATCH_SIZE = 50

known_face_folder = Path("/home/xuefeng/fire-demo/wenxiang_face")
recognizer = SimpleFaceRecognizer(known_face_folder)

video_path = r"/home/xuefeng/fire-demo/wenxiang_face.h264"
cap = cv2.VideoCapture(video_path)

output_path = r"/home/xuefeng/fire-demo/wenxiang_face_result.avi"

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))

face_cascade = cv2.CascadeClassifier('/home/xuefeng/anaconda3/envs/py36/lib/python3.6/site-packages/cv2/data/haarcascade_frontalface_default.xml')

start_time = time.time()
while True:

    # logger.info("start to read a frame")
    ret, frame = cap.read()
    if ret is False:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    logger.info("detect {} faces".format(len(faces)))

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    out.write(frame)


end_time = time.time()
logger.info("it takes {} seconds".format(end_time-start_time))

cap.release()
out.release()