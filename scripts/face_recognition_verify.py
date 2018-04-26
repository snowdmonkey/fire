import logging
import time
import uuid
from pathlib import Path

import cv2
import face_recognition as fr

from fire.face.face_recognize import SimpleFaceRecognizer
from fire.video import VideoStream

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger(__name__)

video_url = {
    "wenxiang": r"rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LREtfVGVzdGVyKDI0OSkvc3RyZWFtP3N1YnR5cGU9UHJpdmF0ZV9ob25leQ==",
    "yanxiang": r"rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LREtfVGVzdGVyMl8yNDUvc3RyZWFtP3N1YnR5cGU9UHJpdmF0ZV9ob25leQ=="}

# video_url = r"rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcigyNDkpL3N0cmVhbT9zdWJ0eXBlPVByaXZhdGVfaG9uZXk="

face_path = {"wenxiang": r"C:\Users\h232559\Desktop\fire\wenxiang_face",
             "yanxiang": r"C:\Users\h232559\Desktop\fire\yanxiang_face"}


previous_frame = None

if __name__ == "__main__":

    video = VideoStream(video_url.get("wenxiang"), device_id="")
    # video = VideoStream(r"C:\Users\h232559\AppData\Roaming\PotPlayerMini\Capture\live_20180424_103553.avi", device_id="")
    known_face_path = Path(face_path.get("wenxiang"))

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

        if previous_frame is None:
            pass
        elif (frame == previous_frame).all():
            time.sleep(1)
            continue

        previous_frame = frame

        input_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        ids, boxes, scores = recognizer.recognize(input_frame)
        # logger.info("end to process a frame")
        for id, box, score in zip(ids, boxes, scores):
            # frame = cv2.rectangle(frame, (box.x, box.y), (box.x+box.w, box.y+box.h), (0, 0, 255), 1)
            height, width, _ = frame.shape
            frame = cv2.rectangle(frame, (int(width * box.xmin), int(height * box.ymin)),
                                  (int(width * box.xmax), int(height * box.ymax)), (0, 0, 255), 1)
            font = cv2.FONT_HERSHEY_SIMPLEX
            score = round(score, 3)
            if score < 0.5:
                name = "unknown"
            frame = \
                cv2.putText(frame, '{}: {}'.format(names[id], score), (int(width * box.xmin), int(height * box.ymin) - 2),
                            font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        frame = cv2.resize(frame, dsize=None, fx=0.5, fy=0.5)
        # out.write(frame)
        cv2.imshow("frame", frame)

        logger.info("processed one frame")
        time.sleep(0.1)

        key = cv2.waitKey(2) & 0xFF
        if key == ord('q'):
            break
        elif key == ord("s"):
            cv2.imwrite(r"C:\Users\h232559\Desktop\test_folder\{}.jpg".format(uuid.uuid4().hex), frame)

    cv2.destroyAllWindows()
    video.close()
