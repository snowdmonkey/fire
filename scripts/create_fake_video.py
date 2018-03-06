from fire.misc import Box
from fire.equipment.presence_predict import TFPresencePredictor
from pathlib import Path
import pkg_resources
import cv2
import logging

GREEN = (0, 255, 0)
RED = (0, 0, 255)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

graph_path = pkg_resources.resource_filename("fire.equipment", "resources/graph/wenxiang_graph.pb")
predictor = TFPresencePredictor(Path(graph_path))

roi = Box(16, 300, 248, 138)
fake_roi = Box(640-248, 300, 248, 138)

video_path = r"C:\Users\h232559\Desktop\fire\温箱机器.avi"
output_path = r"C:\Users\h232559\Desktop\fire\wenxiang_fake_temp.avi"

cap = cv2.VideoCapture(video_path)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_path,fourcc, 20.0, (640, 480))

fake_percent = 0.0

frame_index = 0

result = True
color = GREEN
score = 1.0

while True:
    # print("processing frame {}".format(frame_index))
    logging.info("processing frame {}".format(frame_index))

    ret, frame = cap.read()
    if ret is False:
        break

    fake_frame = frame.copy()
    fake_piece = frame[248: 480, (640-316): 640, :]
    fake_piece = cv2.flip(fake_piece, 1)

    fake_frame[248: 480, 0: 316, :] = fake_piece

    output_frame = cv2.addWeighted(frame, 1.0-fake_percent, fake_frame, fake_percent, 0)

    if (fake_percent < 0.98) and (frame_index % 2 == 0):
        score, result = predictor.predict(output_frame, roi)

        if score > 0.5:
            color = GREEN
        else:
            color = RED

    font = cv2.FONT_HERSHEY_SIMPLEX

    output_frame = \
        cv2.putText(output_frame, 'Presence score: {}'.format(score), (10, 240), font, 1, color, 2, cv2.LINE_AA)

    out.write(output_frame)

    if fake_percent < 0.98 and frame_index > 100:
        fake_percent += 0.005

    frame_index += 1


cap.release()
out.release()
predictor.close()
