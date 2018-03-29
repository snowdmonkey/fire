from typing import List, BinaryIO
from datetime import datetime
from .face.face_recognize import SimpleFaceRecognizer
import cv2
import numpy as np


class ReadFrameError(Exception):
    pass


class FaceRecognitionResult:

    def __init__(self, eid: str, confidence: float = 0, prof: np.ndarray = None):
        """
        constructor

        :param eid: worker eid
        :param confidence: 0 to 1, hwo confident about the result
        :param prof: an ndarray as image serve as the prof
        """
        self.eid = eid
        self.confidence = confidence
        self.prof = prof


class TaskFactory:
    pass


class KeyPersonTask:

    def __init__(self, duration: int,
                 eids: List[str],
                 face_encodings: List[List[float]],
                 video_url: str):
        """
        constructor

        :param duration: length of the task to run
        :param eids: list of worker eid
        :param face_encodings: list of face encodings
        :param video_url: url for the video resource
        """

        self._duration = duration
        self._eids = eids
        self._face_encodings = face_encodings
        self._start_time = datetime.now()
        self._recognizer = SimpleFaceRecognizer(face_encodings=face_encodings)
        self._video_url = video_url

    def run(self) -> List[FaceRecognitionResult]:
        """
        run the task

        :return: face recognition result

        :raise ReadFrameError: if read the video frame failed
        """

        result = list()  # type: List[FaceRecognitionResult]
        for eid in self._eids:
            result.append(FaceRecognitionResult(eid=eid))

        while True:
            cap = cv2.VideoCapture(self._video_url)
            ret, frame = cap.read()
            if ret is False:
                raise ReadFrameError("fail to read frame from video source")
            cap.release()

            ids, _, scores = self._recognizer.recognize(frame)
            for id, score in zip(ids, scores):
                if result[id].confidence < score:
                    result[id].confidence = score
                    result[id].prof = frame

            # stop the loop if all key persons are captured
            if all([x.confidence > 0.5 for x in result]):
                break

            # stop the loop if timeout
            current_time = datetime.now()
            if (current_time - self._start_time).seconds > self._duration:
                break

        return result


class EquipmentTask:

    def __init__(self, model_io: BinaryIO, result_order: int):
        """
        constructor

        :param model_io: io to load the model file
        :param result_order: order of the expected result
        """

