import logging
import random
import argparse
from pathlib import Path
from typing import Tuple, List, IO, Dict
from tensorflow.python.framework import graph_util

import cv2
import json
import numpy as np
import pkg_resources
import tensorflow as tf


class TransferTrainer:
    def __init__(self, n_classes: int, learning_rate: float = 0.01):
        """
        constructor
        :param n_classes: number of classes to predict
        :param learning_rate: learning rate
        """
        self._n_classes = n_classes
        self._learning_rate = learning_rate
        self._graph = self._build_graph()
        self._sess = self._build_session()
        self._class_map = dict()
        self._logger = logging.getLogger(self.__class__.__name__)

    def _build_graph(self) -> tf.Graph:
        """
        build the graph for transfer learning
        :return: graph with prediction layer removed
        """
        graph_file_path = pkg_resources.resource_filename("fire.equipment",
                                                          "resources/inception-2015-12-05/classify_image_graph_def.pb")

        with tf.Graph().as_default() as graph:
            # init = tf.global_variables_initializer()
            with open(graph_file_path, "rb") as f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name="")

            bottleneck_tensor_name = 'pool_3/_reshape:0'
            bottleneck_tensor_size = 2048
            input_width = 299
            input_height = 299
            input_depth = 3
            resized_input_tensor_name = 'Mul:0'

            bottleneck_tensor = graph.get_tensor_by_name('pool_3/_reshape:0')
            # img_input_tensor = graph.get_tensor_by_name("import/Mul:0")

            with tf.name_scope("input"):
                bottleneck_input = tf.placeholder_with_default(bottleneck_tensor,
                                                               shape=[None, 2048],
                                                               name="BottleneckInputPlaceholder")
                # img_input = tf.placeholder_with_default(img_input_tensor, shape=[None, 299, 299, 3], name="Features")
                ground_truth_input = tf.placeholder(tf.int64, [None], name="GroundTruthInput")

            layer_name = "final_retrain_ops"
            with tf.name_scope(layer_name):
                with tf.name_scope("weights"):
                    initial_value = tf.truncated_normal([bottleneck_tensor_size, self._n_classes],
                                                        stddev=0.001)
                    layer_weights = tf.Variable(initial_value, name="final_weights")
                with tf.name_scope("biases"):
                    layer_biases = tf.Variable(tf.zeros([self._n_classes]), name="final_biases")

                with tf.name_scope("Wx_plus_b"):
                    logits = tf.matmul(bottleneck_input, layer_weights) + layer_biases

            # tf.contrib.quantize.create_training_graph()
            with tf.name_scope("cross_entropy"):
                cross_entropy_mean = tf.losses.sparse_softmax_cross_entropy(labels=ground_truth_input,
                                                                            logits=logits)
            with tf.name_scope("train"):
                optimizer = tf.train.GradientDescentOptimizer(self._learning_rate)
                train_step = optimizer.minimize(cross_entropy_mean, name="TrainOp")
            with tf.name_scope("eval"):
                probs = tf.nn.softmax(logits, name="Probs")
                prediction = tf.argmax(probs, 1)
                correct_prediction = tf.equal(prediction, ground_truth_input)
                accuracy_op = tf.reduce_mean(tf.cast(correct_prediction, tf.float32), name="Accuracy")
        return graph

    def _build_session(self) -> tf.Session:
        """
        build tf session
        :return: tf session to conduct the training
        """
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.Session(graph=self._graph, config=config)
        # sess.run(tf.global_variables_initializer())
        with self._graph.as_default():
            # init = tf.global_variables_initializer()
            # sess.run(init)
            sess.run(tf.global_variables_initializer())

        return sess

    def __del__(self):
        self._sess.close()

    def _create_train_sets(self, path: Path, train_proportion: float) -> \
            Tuple[List[Tuple[int, np.ndarray]], List[Tuple[int, np.ndarray]]]:
        """
        create the train and test dataset from a path contain sub-folders of images
        :param path: path of the folder contain folders of images
        :param train_proportion: proportion of the training set
        :return: (train_dataset, test_dataset)
        """
        sub_folders = [x for x in path.iterdir() if x.is_dir()]  # type: List[Path]
        if len(sub_folders) != self._n_classes:
            raise RuntimeError("number of n_classes does not match number of sub folders")

        sub_folders.sort()

        train_set = list()
        test_set = list()

        for i, folder in enumerate(sub_folders):
            self._class_map.update({i: folder.stem})
            imgs = list()
            for image_path in folder.glob("*.jpg"):
                img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (299, 299))
                img = (img - 128.0) / 128.0
                imgs.append((i, img))
            random.shuffle(imgs)
            train_num = int(len(imgs) * train_proportion)

            train_set.extend(imgs[:train_num])
            test_set.extend(imgs[train_num:])

        random.shuffle(train_set)
        random.shuffle(test_set)
        return train_set, test_set

    def _train_or_eval_one_epoch(self, dataset: List[Tuple[int, np.ndarray]],
                                 batch_size: int, eval: bool) -> Tuple[float, float]:
        """
        train one epoch on the dataset
        :param dataset: dict create in _create_train_dataset
        :param batch_size: batch size
        :param eval: true for eval mode, false for train equipment_model
        :return: accuracy mean, cross entropy mean
        """
        train_op = self._graph.get_operation_by_name("train/TrainOp")
        # feature_entry = self._graph.get_tensor_by_name("import/Mul:0")
        # label_entry = self._graph.get_operation_by_name("input/GroundTruthInput")
        bottleneck_tensor = self._graph.get_tensor_by_name('pool_3/_reshape:0')
        acc_list = list()
        cross_entropy_list = list()
        for i in range(len(dataset) // batch_size):
            data_batch = dataset[(i*batch_size):((i+1)*batch_size)]
            features = [x[1] for x in data_batch]
            bottlenecks = list()
            for feature in features:
                feature = np.stack([feature])
                bottleneck = self._sess.run(bottleneck_tensor, feed_dict={"Mul:0": feature})
                bottleneck = np.squeeze(bottleneck)
                bottlenecks.append(bottleneck)
            bottlenecks = np.stack(bottlenecks)

            label = np.array([x[0] for x in data_batch])
            if eval is True:
                acc, cross_entropy = self._sess.run(
                    ["eval/Accuracy:0", "cross_entropy/sparse_softmax_cross_entropy_loss/value:0"],
                    feed_dict={"input/BottleneckInputPlaceholder:0": bottlenecks, "input/GroundTruthInput:0": label})
            else:
                acc, cross_entropy, _ = self._sess.run(
                    ["eval/Accuracy:0", "cross_entropy/sparse_softmax_cross_entropy_loss/value:0", train_op],
                    feed_dict={"input/BottleneckInputPlaceholder:0": bottlenecks, "input/GroundTruthInput:0": label})
                # self._logger.info("batch {} finished".format(i))
            acc_list.append(acc)
            cross_entropy_list.append(cross_entropy)
        acc_mean = sum(acc_list) / len(acc_list)
        cross_entropy_mean = sum(cross_entropy_list) / len(cross_entropy_list)
        # x = self._sess.run("final_retrain_ops/biases/final_biases:0")
        return acc_mean, cross_entropy_mean

    def train_folder(self, folder_path: Path, batch_size: int, train_proportion: float, n_epochs: int):
        """
        train equipment_model based on images in a folder. In this folder the subfolder name should be the class name
        :param folder_path: path of the folder contains the images
        :param batch_size: batch size for training
        :param train_proportion: percentage of the train images
        :param n_epochs: number of epochs to run
        :return: None
        """
        # with self._graph.as_default():
        #     init = tf.global_variables_initializer()
        #     self._sess.run(init)
        train_set, test_set = self._create_train_sets(folder_path, train_proportion)

        for i in range(n_epochs):
            acc, loss = self._train_or_eval_one_epoch(train_set, batch_size=batch_size, eval=False)
            self._logger.info("epoch {}: train accuracy: {}; train loss: {}".format(i, round(acc, 5), round(loss, 5)))

            acc, loss = self._train_or_eval_one_epoch(test_set, batch_size=batch_size, eval=True)
            self._logger.info("epoch {}: test  accuracy: {}; test  loss: {}".format(i, round(acc, 5), round(loss, 5)))
            #     self._eval_one_epoch(test_set)

    def export(self, fp: IO[bytes]):
        """
        export the current graph
        :param fp: io to write the equipment_model
        :return: a dict mapping equipment_model output to class name
        """
        output_graph_def = graph_util.convert_variables_to_constants(self._sess,
                                                                     self._sess.graph.as_graph_def(),
                                                                     ["eval/Probs"])
        fp.write(output_graph_def.SerializeToString())
        return self._class_map


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="folder that the images are stored")
    args = parser.parse_args()

    trainer = TransferTrainer(2)
    img_path = Path(args.path)
    pb_path = img_path / "result.pb"
    class_map_path = img_path / "class_map.json"

    trainer.train_folder(img_path, batch_size=100, train_proportion=0.8, n_epochs=5)

    with pb_path.open("wb") as f:
        class_map=trainer.export(f)

    with class_map_path.open("w") as f:
        json.dump(class_map, f)

    # with open("result.pb", "wb") as f:
    #     trainer.export(f)

    # with open("class_map.json", "w") as f:
    #     json.dump(class_map, f)


    # train_set, test_set = trainer._create_train_sets(Path("/home/xuefeng/flower_photos"), 0.8)
    # print(test_set[0])

    # for op in trainer._graph.get_operations():
    #     print(op.name)
        # op = trainer._graph.get_operation_by_name("import/Mul")
        # print(op.shape)
