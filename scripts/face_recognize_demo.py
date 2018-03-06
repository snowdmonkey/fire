import logging
from pathlib import Path

import cv2

from fire.face.face_recognize import SimpleFaceRecognizer

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

known_face_folder = Path(r"C:\Users\h232559\Desktop\fire\wenxiang_face")
recognizer = SimpleFaceRecognizer(known_face_folder)

video_path = r"C:\Users\h232559\Desktop\fire\wenxiang_face.h264"
output_path = r"C:\Users\h232559\Desktop\fire\wenxiang_face_result.avi"
cap = cv2.VideoCapture(video_path)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_path,fourcc, 20.0, (640, 480))


while True:
    ret, frame = cap.read()
    if ret is False:
        break

    input_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    ids, boxes, scores = recognizer.recognize(input_frame)

    for name, box, score in zip(ids, boxes, scores):
        frame = cv2.rectangle(frame, (box.x, box.y), (box.x+box.w, box.y+box.h), (0, 0, 255), 1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        score = round(score, 3)
        if score < 0.5:
            name = "unknown"
        frame = \
            cv2.putText(frame, '{}: {}'.format(name, score), (box.x, box.y-2), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

    out.write(frame)
    # cv2.imshow("frame", frame)
    # if cv2.waitKey(25) & 0xFF == ord('q'):
    #     break

cap.release()
out.release()
# cv2.destroyAllWindows()