import argparse
import json
import cv2
import base64
import logging
import time
import pika
from datetime import datetime
from typing import List, Union, Dict

import numpy as np
import requests
from kafka import KafkaConsumer
from abc import ABC, abstractmethod
from .equipment.presence_predict import PresencePredictor, TFPresencePredictor
from .face.face_recognize import SimpleFaceRecognizer, FaceRecognizer
from .misc import Box
from .video import VideoStream

logger = logging.getLogger(__name__)


class Result(ABC):

    def __init__(self, device_id: str, confidence: float, prof: np.ndarray = None):
        """
        base class for analysis results

        :param device_id: camera id
        :param confidence: confidence score, between 0 and 1
        :param prof: and numpy array as image
        """
        self.confidence = confidence
        self.device_id = device_id
        self.prof = prof

    def to_base_dict(self) -> Dict[str, Union[int, float, str, bool]]:
        r = {"confidence": self.confidence}
        if self.prof is not None:
            img = cv2.resize(self.prof, dsize=None, fx=0.3, fy=0.3)
            _, buffer = cv2.imencode(".jpg", self.prof)
            img_bytes = buffer.tobytes()
            img_base64_bytes = base64.b64encode(img_bytes)
            img_base64_string=  img_base64_bytes.decode("ascii")

            r.update({"prof": img_base64_string})
        return r

    @abstractmethod
    def to_dict(self) -> Dict[str, Union[int, float, str, bool]]:
        pass


class FaceRecognitionResult(Result):

    def __init__(self, eid: str, device_id: str, confidence: float = 0, prof: np.ndarray = None):
        """
        constructor

        :param eid: worker eid
        :param confidence: 0 to 1, how confident about the result
        :param prof: an ndarray as image serve as the prof
        :param device_id: camera id
        """
        super().__init__(device_id=device_id, confidence=confidence, prof=prof)
        self.eid = eid

    def to_dict(self):
        r = self.to_base_dict()
        r.update({"eid": self.eid})
        return r


class EquipmentResult(Result):
    def __init__(self, confidence: float, device_id: str, prof: np.ndarray = None):
        """
        constructor

        :param confidence: from 0 to 1, how confident the equipment is there
        :param prof: an ndarray as image serve as the prof
        :param device_id: camera id
        """
        super().__init__(device_id=device_id, confidence=confidence, prof=prof)
        self.confidence = confidence

    def to_dict(self):
        r = self.to_base_dict()
        r.update({"toolExists": self.confidence > 0.5})
        return r


class Task(ABC):

    def __init__(self, video: VideoStream):
        """
        abstract class for a task

        :param video: an video stream instance
        """
        self._video = video
        self._start_time = datetime.now()

    @property
    def camera_id(self):
        return self._video.device_id

    @abstractmethod
    def run(self):
        pass

    @property
    def start_time(self) -> datetime:
        return self._start_time


class KeyPersonTask(Task):

    def __init__(self, duration: int,
                 eids: List[str],
                 face_recognizer: FaceRecognizer,
                 video: VideoStream):
        """
        constructor

        :param duration: length of the task to run
        :param eids: list of worker eid
        :param face_recognizer: a face recognizer
        :param video: VideoStream instance
        """
        super().__init__(video)
        self._duration = duration
        self._eids = eids
        # self._start_time = datetime.now()
        self._recognizer = face_recognizer
        # self._video = video

    def run(self) -> List[FaceRecognitionResult]:
        """
        run the task

        :return: face recognition result

        :raise ReadFrameError: if read the video frame failed
        """

        self._video.start()

        result = list()  # type: List[FaceRecognitionResult]
        for eid in self._eids:
            result.append(FaceRecognitionResult(eid=eid, device_id=self._video.device_id))

        while True:

            # stop the loop if all key persons are captured
            if all([x.confidence > 0.5 for x in result]):
                break

            # stop the loop if timeout
            current_time = datetime.now()
            if (current_time - self._start_time).seconds > self._duration:
                break

            frame = self._video.read_current_frame()
            if frame is None:
                time.sleep(1)
                continue

            ids, _, scores = self._recognizer.recognize(frame)
            for id, score in zip(ids, scores):
                if result[id].confidence < score:
                    result[id].confidence = score
                    result[id].prof = frame

        self._video.close()

        return result


class EquipmentTask(Task):
    def __init__(self,
                 presence_predictor: PresencePredictor,
                 video: VideoStream):
        """
        constructor

        :param presence_predictor: predictor to predict whether an equipment exists
        :param video: video source
        """
        super().__init__(video)
        self._predictor = presence_predictor
        # self._start_time = datetime.now()

    def run(self) -> EquipmentResult:
        """
        run the task

        :param max_attempts: maximum number of attempts to run the program

        :return: task result
        """

        self._video.start()
        time.sleep(3)  # wait 3 seconds to skip the incomplete frames

        attempts = 0
        while True:
            if attempts > 10:
                raise Exception("fail to read a frame")
            try:
                frame = self._video.read_current_roi()
            except Exception as e:
                self._video.close()
                raise e
            if frame is not None:
                self._video.close()
                break
            else:
                attempts += 1
                time.sleep(1)
                continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        confidence, conclusion = self._predictor.predict(frame)
        return EquipmentResult(confidence=confidence, prof=frame, device_id=self._video.device_id)


class TaskFactory:
    def __init__(self, controller_base_url: str):
        """
        constructor

        :param controller_base_url: base url for the controller app to retrieve necessary information
        """
        self._controller_base_url = controller_base_url

    def create_task(self, topic: str, payload: str) -> Union[KeyPersonTask, EquipmentTask]:
        """
        create a task from
        :param topic: task topic
        :param payload: message payload
        :return: a task to run
        """
        if topic == "keyperson":
            task = self.create_face_recognition_task(payload)
        elif topic == "equipment":
            task = self.create_equipment_task(payload)
        else:
            raise ValueError("unknown task topic")

        return task

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
        r = requests.get("{}/workstation/{}/worker".format(self._controller_base_url, workstation_id))
        if r.status_code != 200:
            raise Exception("request {} error {}".format(r.url, r.status_code))
        eids = [x.get("eid") for x in r.json()]
        face_encodings = [x.get("faceEncoding") for x in r.json()]

        # retrieve relevant camera information
        r = requests.get("{}/camera/keyperson_camera/workstation/{}".format(self._controller_base_url, workstation_id))
        if r.status_code != 200:
            raise Exception("fail to retrieve camera information, {}, {}".format(r.url, r.status_code))
        else:
            camera_uri = r.json().get("uri")
            camera_id = r.json().get("id")

        recognizer = SimpleFaceRecognizer(face_encodings=face_encodings)
        video = VideoStream(url=camera_uri, device_id=camera_id)
        task = KeyPersonTask(duration=duration, eids=eids, face_recognizer=recognizer, video=video)

        return task

    def create_equipment_task(self, payload: str) -> EquipmentTask:
        """
        create a equipment existence task

        :param payload: message from task queue
        :return: equipment existence task
        """
        payload_dict = json.loads(payload)
        equipment_id = payload_dict.get("equipmentId")

        # retrieve relevant camera information
        r = requests.get("{}/camera/equipment_camera/equipment/{}".format(self._controller_base_url, equipment_id))
        if r.status_code != 200:
            raise Exception("request {} error {}".format(r.url, r.status_code))
        video = VideoStream(url=r.json().get("uri"),
                            device_id=r.json().get("id"),
                            roi=Box(xmin=r.json().get("xmin"),
                                    xmax=r.json().get("xmax"),
                                    ymin=r.json().get("ymin"),
                                    ymax=r.json().get("ymax")))

        # retrieve equipment model file
        r = requests.get("{}/equipment/{}/equipment_model/pb".format(self._controller_base_url, equipment_id),
                         stream=True)
        if r.status_code != 200:
            raise Exception("request {} error {}".format(r.url, r.status_code))
        predictor = TFPresencePredictor(r.raw)
        r.raw.close()

        task = EquipmentTask(presence_predictor=predictor, video=video)

        return task


def publish_mq(body: str, topic: str, rabbit_url: str):
    try:
        connection = pika.BlockingConnection(pika.URLParameters(rabbit_url))
    except Exception as e:
        logger.error("fail to establish rabbitmq connection")
        return
    else:
        try:
            channel = connection.channel()
            if topic == "equipment":
                # channel.queue_declare(queue="alarm.equipment.move")
                channel.basic_publish(exchange="alarm.equipment.move",
                                      routing_key="alarm.equipment.move.#",
                                      body=body)
                logger.info("rabbitmq publish success")
            elif topic == "keyperson":
                # channel.queue_declare(queue="alarm.worker.diff")
                channel.basic_publish(exchange="alarm.worker.diff",
                                      routing_key="alarm.worker.diff.#",
                                      body=body)
                logger.info("rabbitmq publish success")

        except Exception as e:
            logger.error("fail to publish to rabbitmq")
        finally:
            connection.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("controller_base_url", type=str, help="url to the controller app", )
    parser.add_argument("kafka", type=str, help="url to kafka broker")
    parser.add_argument("rabbit", type=str, help="rabbitmq url parameter")

    args = parser.parse_args()

    controller_base_url = args.controller_base_url
    task_factory = TaskFactory(controller_base_url=args.controller_base_url)

    while True:
        consumer = KafkaConsumer("equipment", "keyperson", bootstrap_servers=args.kafka, group_id="3cf")
        msg = next(consumer)
        consumer.commit()
        consumer.close()

        logger.info("revieced task topic: {}; value: {}".format(msg.topic, msg.value.decode()))

        output_payload = dict()

        try:
            # try to decode task payload
            payload = json.loads(msg.value.decode())
            task_id = payload.get("taskId")
            deadline = datetime.strptime(payload.get("deadline"), "%Y-%m-%dT%H:%M:%S")
            if task_id is None:
                raise Exception("cannot find task id")
        except Exception as e:
            # if decode task payload fails, continue directly
            logger.exception(e)
            continue
        else:
            # update task id in output payload
            output_payload.update({"taskId": task_id})

        # check if deadline is passed
        if datetime.now() > deadline:
            logger.info("task overdue")
            output_payload.update({"status": "failed"})
            requests.put("{}/task/{}".format(controller_base_url, task_id),
                         json={"status": "failed", "result": "task overdue"})
            publish_mq(body=json.dumps(output_payload), topic=msg.topic, rabbit_url=args.rabbit)
            continue

        try:
            # try to create task from payload
            task = task_factory.create_task(topic=msg.topic, payload=msg.value.decode())
        except Exception as e:
            # if create task fails, set task status to fail
            logger.info("fail to create task {}".format(payload.get("taskId")))
            requests.put("{}/task/{}".format(controller_base_url, task_id),
                         json={"status": "failed", "result": "create task failed" + str(e)})
            publish_mq(body=json.dumps(output_payload), topic=msg.topic, rabbit_url=args.rabbit)
            continue
        else:
            #  if task is successfully created, update task status to ongoing and update output payload
            logger.info("successfully create task {}".format(output_payload.get("taskId")))
            requests.put("{}/task/{}".format(controller_base_url, task_id),
                         json={"status": "ongoing", "startTime": task.start_time.strftime("%Y-%m-%dT%H:%M:%S")})
            output_payload.update({"time": task.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                                   "deviceId": task.camera_id})

        try:
            #  try to run a equipment task
            result = task.run()  # type: Union[EquipmentResult, List[FaceRecognitionResult]]

        except Exception as e:

            # if task fails, update task status to failed and update output payload
            logger.error("task {} fails".format(output_payload.get("taskId")))
            output_payload.update({"success": False})
            requests.put("{}/task/{}".format(controller_base_url, task_id),
                         json={"status": "failed", "result": "execute task failed" + str(e)})
            publish_mq(body=json.dumps(output_payload), topic=msg.topic, rabbit_url=args.rabbit)
        else:
            # if task succeed, update task status to success, task end time and encode result
            if msg.topic == "equipment":
                output_payload.update({"data": result.to_dict()})
            elif msg.topic == "keyperson":
                output_payload.update({"data": [x.to_dict() for x in result]})

            requests.put("{}/task/{}".format(controller_base_url, task_id),
                         json={
                             "status": "success",
                             "endTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                             "result": json.dumps(output_payload)})
            publish_mq(body=json.dumps(output_payload), topic=msg.topic, rabbit_url=args.rabbit)
            logger.info("task {} succeed".format(output_payload.get("taskId")))


        # if msg.topic == "equipment":
        #     try:
        #         #  try to run a equipment task
        #         result = task.run()  # type: EquipmentResult
        #
        #     except Exception as e:
        #
        #         # if task fails, update task status to failed and update output payload
        #         logger.error("task {} fails".format(output_payload.get("taskId")))
        #         output_payload.update({"success": False})
        #         requests.put("{}/task/{}".format(controller_base_url, task_id),
        #                      json={"status": "failed", "result": "execute task failed" + str(e)})
        #     else:
        #         # if task succeed, update task status to success, task end time and encode result
        #         output_payload.update({"data": result.to_dict()})
        #         requests.put("{}/task/{}".format(controller_base_url, task_id),
        #                      json={
        #                          "status": "success",
        #                          "endTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        #                          "result": json.dumps(output_payload)})
        #         logger.info("task {} succeed".format(output_payload.get("taskId")))
        # elif msg.topic == "keyperson":
        #     try:
        #         #  try to run a equipment task
        #         result = task.run()  # type: List[FaceRecognitionResult]
        #
        #     except Exception as e:
        #
        #         # if task fails, update task status to failed and update output payload
        #         logger.error("task {} fails".format(output_payload.get("taskId")))
        #         output_payload.update({"success": False})
        #         requests.put("{}/task/{}".format(controller_base_url, task_id),
        #                      json={"status": "failed", "result": "execute task failed" + str(e)})
        #         logger.error("task {} fails".format(output_payload.get("taskId")))
        #     else:
        #         # if task succeed, update task status to success, task end time and encode result
        #         output_payload.update({"data": [x.to_dict() for x in result]})
        #         requests.put("{}/task/{}".format(controller_base_url, task_id),
        #                      json={
        #                          "status": "success",
        #                          "endTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        #                          "result": json.dumps(output_payload)})
        #         logger.info("task {} succeed".format(output_payload.get("taskId")))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler()])
    logging.getLogger("pika").setLevel(logging.ERROR)
    logging.getLogger("kafka").setLevel(logging.ERROR)
    main()