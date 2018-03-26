import logging
import time
from multiprocessing import Pool, set_start_method
from pathlib import Path

import cv2
import numpy as np

from src.fire.face.face_recognize import SimpleFaceRecognizer

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger(__name__)

BATCH_SIZE = 10

known_face_folder = Path("/home/xuefeng/fire-demo/wenxiang_face")
recognizer = SimpleFaceRecognizer(known_face_folder)

video_path = r"/home/xuefeng/fire-demo/wenxiang_face.h264"
output_path = r"/home/xuefeng/fire-demo/wenxiang_face_result.avi"
cap = cv2.VideoCapture(video_path)


def iter_video(cap: cv2.VideoCapture) -> np.ndarray:
    while True:
        ret, frame = cap.read()
        if ret is False:
            cap.release()
            break
        else:
            input_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            yield input_frame




# def target_fun():
#     cap = cv2.VideoCapture(video_path)
#     recognizer = SimpleFaceRecognizer(known_face_folder)
#     while True:
#         ret, frame = cap.read()
#         if ret is False:
#             cap.release()
#             break
#         else:
#             input_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             recognizer.recognize(input_frame)



def target_fun(img: np.ndarray):
    recognizer.recognize(img)


if __name__ =="__main__":
    set_start_method("spawn")
    # recognizer.process_stream(iter_video(cap), 2)
    # for img in iter_video(cap):
    #     recognizer.recognize(img)
    imgs = list()
    for img in iter_video(cap):
        imgs.append(img)

    pool = Pool(16)

    start_time = time.time()

    pool.map(target_fun, imgs)
    pool.close()

    end_time = time.time()
    logger.info("it takes {} seconds".format(end_time-start_time))


    # set_start_method("spawn")
    # p1 = Process(target=target_fun)
    # p2 = Process(target=target_fun)
    #
    # p1.start()
    # p2.start()
    # p1.join()
    # p2.join()