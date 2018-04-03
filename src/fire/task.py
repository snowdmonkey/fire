from typing import List, BinaryIO, Union
from datetime import datetime
from .face.face_recognize import SimpleFaceRecognizer, FaceRecognizer
from .equipment.presence_predict import PresencePredictor
from .video import VideoStream, ReadFrameError
import cv2
import numpy as np
import json
import requests


class FaceRecognitionResult:

    def __init__(self, eid: str, confidence: float = 0, prof: np.ndarray = None):
        """
        constructor

        :param eid: worker eid
        :param confidence: 0 to 1, how confident about the result
        :param prof: an ndarray as image serve as the prof
        """
        self.eid = eid
        self.confidence = confidence
        self.prof = prof


class EquipmentResult:

    def __init__(self, confidence: float, prof: np.ndarray = None):
        """
        constructor

        :param confidence: from 0 to 1, how confident the equipment is there
        :param prof: an ndarray as image serve as the prof
        """
        self.confidence = confidence
        self.prof = prof


class KeyPersonTask:

    def __init__(self, duration: int,
                 eids: List[str],
                 face_recognizer: FaceRecognizer,
                 video: VideoStream):
        """
        constructor

        :param duration: length of the task to run
        :param eids: list of worker eid
        :param face_recognizer: a face recognizer
        :param video_url: url for the video resource
        """

        self._duration = duration
        self._eids = eids
        self._start_time = datetime.now()
        self._recognizer = face_recognizer
        self._video = video

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
            # cap = cv2.VideoCapture(self._video_url)
            # ret, frame = cap.read()
            # if ret is False:
            #     raise ReadFrameError("fail to read frame from video source")
            # cap.release()
            frame = self._video.read_current_frame()

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

    def __init__(self,
                 presence_predictor: PresencePredictor,
                 video: VideoStream):
        """
        constructor

        :param presence_predictor: predictor to predict whether an equipment exists
        :param video: video source
        """
        self._predictor = presence_predictor
        self._video = video

    def run(self) -> EquipmentResult:
        """
        run the task

        :return: task result
        """
        frame = self._video.read_current_roi()
        confidence, conclusion = self._predictor.predict(frame)
        return EquipmentResult(confidence=confidence, prof=frame)


class TaskFactory:

    def __init__(self, base_url: str):
        """
        constructor

        :param base_url: base url for the controller app to retrieve necessary information
        """
        self._base_url = base_url

    def create_task(self, topic: str, payload: str) -> Union[FaceRecognitionResult, EquipmentResult]:
        """
        create a task from
        :param topic: task topic
        :param payload: message payload
        :return: a task to run
        """
        pass

    def create_face_recognition_task(self, payload: str) -> KeyPersonTask:
        """
        create a face recognition task
        :param payload: message from task queue
        :return: a key person task
        """
        payload_dict = json.loads(payload)
        workstation_id = payload_dict.get("workstationId")
        duration = payload_dict.get("duration")

        # retrieve relevant worker information
        r = requests.get("{}/workstation/{}/worker".format(self._base_url, workstation_id))
        if r.status_code != 200:
            raise Exception("request {} error {}".format(r.url, r.status_code))
        eids = [x.get("eid") for x in r.json()]
        face_encodings = [x.get("faceEncoding") for x in r.json()]

        # retrieve relevant camera information
        r = requests.get("{}/camera/keyperson_camera/workstation/{}".format(self._base_url, workstation_id))
        if r.status_code != 200:
            raise Exception("fail to retrieve camera information, {}, {}".format(r.url, r.status_code))
        else:
            camera_uri = r.json().get("uri")

        recognizer = SimpleFaceRecognizer(face_encodings=face_encodings)
        video = VideoStream(url=camera_uri)
        task = KeyPersonTask(duration=duration, eids=eids, face_recognizer=recognizer, video=video)

        return task


    def create_equipment_task(self, payload: str) -> EquipmentTask:
        """
        create a equipment existence task
        :param payload: message from task queue
        :return: equipment existence task
        """
        pass