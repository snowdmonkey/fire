import cv2
import requests
from pathlib import Path

path = Path(r"C:\Users\h232559\Desktop\fire\wenxiang_face")

for img_path in path.glob("*.jpg"):
    eid = img_path.stem
    r = requests.post("http://127.0.0.1:5000/factory/0/worker",
                      json={"eid": eid, "name": eid})

    print("{}: {}".format(eid, r.status_code))

    r = requests.post("http://127.0.0.1:5000/factory/0/workstation/1/worker", json={"eid": eid})

    print("{}: {}".format(eid, r.status_code))

    with img_path.open("rb") as f:

        r = requests.post("http://127.0.0.1:5000/factory/0/worker/{}/face".format(eid),
                          files={"file": f})
        print("{}: {}".format(eid, r.status_code))

