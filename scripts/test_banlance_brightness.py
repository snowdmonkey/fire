import logging
from pathlib import Path

import cv2
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


video_path = r"C:\Users\h232559\Desktop\fire\wenxiang_face.h264"
output_path = r"C:\Users\h232559\Desktop\fire\wenxiang_face_brightness_balance.avi"

cap = cv2.VideoCapture(video_path)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_path,fourcc, 20.0, (640*2, 480))

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

while True:

    ret, frame = cap.read()
    if ret is False:
        break

    b_frame = frame.copy()

    b_frame = cv2.cvtColor(b_frame, cv2.COLOR_BGR2YUV)
    b_frame[:, :, 0] = clahe.apply(b_frame[:, :, 0])
    b_frame = cv2.cvtColor(b_frame, cv2.COLOR_YUV2BGR)

    output_frame = np.hstack((frame, b_frame))

    out.write(output_frame)

cap.release()
out.release()
