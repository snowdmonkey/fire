import tensorflow as tf
import numpy as np
import cv2
import argparse
from abc import ABC, abstractmethod
from typing import Tuple, Optional, BinaryIO
from pathlib import Path


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
            tf.import_graph_def(graph_def, name="")
        return graph

    def predict(self, img: np.ndarray) -> Tuple[float, bool]:
        """
        predict the result

        :param img: img of RGB channels
        :return:
        """
        # if box is not None:
        #     img = img[box.y: (box.y+box.h), box.x: (box.x+box.w), :]

        img = cv2.resize(img, (299, 299))
        img = (img - 128.0) / 128.0
        img = np.resize(img, new_shape=(1,)+img.shape)

        input_name = "Mul"
        output_name = "eval/Probs"

        input_operation = self._graph.get_operation_by_name(input_name)
        output_operation = self._graph.get_operation_by_name(output_name)

        result = self._sess.run(output_operation.outputs[0], {input_operation.outputs[0]: img})[0]

        return result[1], result[1] > 0.5

    def __del__(self):
        self._sess.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pb_path", type=str)
    parser.add_argument("img_path", type=str)
    args = parser.parse_args()

    with open(args.pb_path, "rb") as f:
        predictor = TFPresencePredictor(f)

    img = cv2.imread(args.img_path, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    print(predictor.predict(img))


if __name__ == "__main__":
    main()