import cv2
import face_recognition as fr
import time
from pathlib import Path
from fire.face.face_recognize import SimpleFaceRecognizer
from fire.video import VideoStream

video_url = r"rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcigyNDkpL3N0cmVhbT9zdWJ0eXBlPVByaXZhdGVfaG9uZXk="
video = VideoStream(video_url)

known_face_path = Path(r"C:\Users\h232559\Desktop\fire\wenxiang_face")



names = list()
known_face_encodings = list()
for path in known_face_path.glob("*.jpg"):
    known_image = fr.load_image_file(str(path))
    try:
        known_face_encodings.append(fr.face_encodings(known_image)[0])
        names.append(path.name)
    except Exception as e:
        print(e)
        print("error while encoding {}".format(str(path)))

recognizer = SimpleFaceRecognizer(face_encodings=known_face_encodings)

video.start()
while True:
    frame = video.read_current_frame()
    if frame is None:
        time.sleep(1)
        continue

    input_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    ids, boxes, scores = recognizer.recognize(input_frame)
    # logger.info("end to process a frame")
    for id, box, score in zip(ids, boxes, scores):
       # frame = cv2.rectangle(frame, (box.x, box.y), (box.x+box.w, box.y+box.h), (0, 0, 255), 1)
       height, width, _  = frame.shape
       frame = cv2.rectangle(frame, (int(width*box.xmin), int(height*box.ymin)),
                             (int(width*box.xmax), int(height*box.ymax)), (0, 0, 255), 1)
       font = cv2.FONT_HERSHEY_SIMPLEX
       score = round(score, 3)
       if score < 0.5:
           name = "unknown"
       frame = \
           cv2.putText(frame, '{}: {}'.format(names[id], score), (int(width*box.xmin), int(height*box.ymin)-2), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

    frame = cv2.resize(frame, (800, 600))
    # out.write(frame)
    cv2.imshow("frame", frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
video.close()