import cv2
import numpy as np
import tensorflow as tf
import argparse

def main():
    parser = argparse.ArgumentParser(description="classify an image")
    parser.add_argument("img", type=str, help="path of the image")
    args = parser.parse_args()

    pb_path = r"/home/xuefeng/PycharmProjects/testres/result.pb"
    img_path = args.img
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    feature = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    feature = cv2.resize(feature, (299, 299))
    feature = (feature - 128.0) / 128.0
    feature = np.stack([feature])

    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(pb_path, mode="rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    sess = tf.Session(graph=graph)
    x = sess.run("import/eval/Probs:0", feed_dict={"import/import/Mul:0": feature})
    # x = sess.run("import/final_retrain_ops/biases/final_biases")
    print(x)

if __name__ == "__main__":
    main()