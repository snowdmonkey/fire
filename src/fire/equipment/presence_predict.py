import tensorflow as tf
import numpy as np
import cv2
from abc import ABC, abstractmethod
from typing import Tuple, Optional, BinaryIO
from pathlib import Path
from ..misc import Box


class PresencePredictor(ABC):

    @abstractmethod
    def predict(self, img: np.ndarray) -> Tuple[float, bool]:
        """
        take in a picture of ROI and predict whether the equipment still exists
        :param img: 3-d array of the img to predict, of size HxWxC, channel order RGB
        # :param roi: region of interest box
        :return: existence confidence, existence conclusion
        """
        pass


class TFPresencePredictor(PresencePredictor):

    def __init__(self, graph_io: BinaryIO):
        """
        constructor
        """
        super().__init__()
        self._graph = self._load_graph(graph_io)
        self._sess = tf.Session(graph=self._graph)

    @staticmethod
    def _load_graph(graph_io: BinaryIO) -> tf.Graph:
        """
        load tf.Graph from a path
        :param graph_path: path the graph file
        :return: tensorflow graph
        """
        graph = tf.Graph()
        graph_def = tf.GraphDef()

        # with graph_path.open(mode="rb") as f:
        #     graph_def.ParseFromString(f.read())
        graph_def.ParseFromString(graph_io.read())
        with graph.as_default():
            tf.import_graph_def(graph_def)
        return graph

    def predict(self, img: np.ndarray) -> Tuple[float, bool]:
        # if box is not None:
        #     img = img[box.y: (box.y+box.h), box.x: (box.x+box.w), :]

        img = cv2.resize(img, (299, 299))
        img = (img - 128.0) / 128.0
        img = np.resize(img, new_shape=(1,)+img.shape)

        input_name = "import/Mul"
        output_name = "import/final_result"

        input_operation = self._graph.get_operation_by_name(input_name)
        output_operation = self._graph.get_operation_by_name(output_name)

        result = self._sess.run(output_operation.outputs[0], {input_operation.outputs[0]: img})[0]

        return result[1], result[1] > 0.5

    def __del__(self):
        self._sess.close()
