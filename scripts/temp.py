import cv2
import requests
from pathlib import Path

path = Path(r"C:\Users\h232559\Desktop\fire\yanxiang_face")

for img_path in path.glob("*.jpg"):
    eid = img_path.stem
    with img_path.open("rb") as f:

        r = requests.post("http://47.92.83.188:5000/factory/100/worker/{}/face".format(eid),
                          files={"file": f})
        print("{}: {}".format(eid, r.status_code))

