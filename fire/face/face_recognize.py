import face_recognition
import numpy as np
import logging
from typing import List, Tuple
from abc import ABC, abstractmethod
from ..misc import Box
from pathlib import Path


class FaceRecognizer(ABC):

    @abstractmethod
    def recognize(self, img: np.ndarray) -> Tuple[List[str], List[Box], List[float]]:
        """
        detect and recognize all the faces in an image
        :param img: img with faces to
        :return: list of face_id, list of face bounding box, list of recognition confidence
        """
        pass


class SimpleFaceRecognizer(FaceRecognizer):

    def __init__(self, known_faces_folder: Path):
        """
        constructor
        :param known_faces_folder: a folder that contains all known faces
        """
        self._face_ids = list() # type: List[str]
        self._face_encodings = list() # type: List[np.ndarray]
        self._logger = logging.getLogger(self.__class__.__name__)
        self._load_known_faces(known_faces_folder)

    def _load_known_faces(self, folder: Path):
        """
        load and encode known faces
        :param folder: a folder contain all the known faces
        :return: None
        """
        for img_path in folder.glob("*.jpg"):

            self._logger.debug("loading known face image {}".format(img_path))
            known_image = face_recognition.load_image_file(str(img_path))

            known_encodings = face_recognition.face_encodings(known_image)

            if len(known_encodings) == 1:
                self._face_encodings.append(known_encodings[0])
                self._face_ids.append(img_path.stem)
            else:
                self._logger.error("fail to decode known face image {}".format(img_path))

    def recognize(self, img: np.ndarray) -> Tuple[List[str], List[Box], List[float]]:

        boxes = list()  # type: List[Box]
        scores = list()  # type: List[float]
        ids = list()  # type: List[str]

        face_locations = face_recognition.face_locations(img)
        self._logger.debug("found {} faces".format(len(face_locations)))
        face_encodings = face_recognition.face_encodings(img, known_face_locations=face_locations)

        for face_encoding in face_encodings:
            distance = face_recognition.face_distance(self._face_encodings, face_encoding)
            min_index = distance.argmin()
            ids.append(self._face_ids[min_index])
            scores.append(1.0 - distance[min_index])

        for face_location in face_locations:
            box = Box(face_location[3], face_location[0],
                      face_location[1]-face_location[3], face_location[2]-face_location[0])
            boxes.append(box)

        return ids, boxes, scores


