import unittest
import pkg_resources
import cv2
from pathlib import Path
from fire.equipment.presence_predict import TFPresencePredictor


class TFPredictorTest(unittest.TestCase):

    def test_predict(self):
        graph_path = pkg_resources.resource_filename("fire.equipment", "resources/graph/wenxiang_graph.pb")
        predictor = TFPresencePredictor(Path(graph_path))
        img_path = r"C:\Users\h232559\Desktop\fire\wenxiang_train\equipment\4.jpg"
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = predictor.predict(img)
        print(result)
        predictor.close()


if __name__ == "__main__":
    unittest.main()