from pathlib import Path

import requests

BASE_URL = "http://47.92.83.188:5000"

# add test factory
requests.post(BASE_URL + "/factory",
              json={"factoryId": 1, "name": "圣赛尔1", "description": "西安圣赛尔工厂"})

# add equipment
requests.post(BASE_URL + "/factory/{}/equipment".format(1),
              json={
                  "equipmentId": 1,
                  "description": "标签机"
              })

# add workstation
requests.post(BASE_URL + "/factory/{}/workstation".format(1),
              json={
                  "workstationId": 1,
                  "name": "烟箱",
                  "description": "string"
              })

requests.post(BASE_URL + "/factory/{}/workstation".format(1),
              json={
                  "workstationId": 2,
                  "name": "温箱",
                  "description": "string"
              })

# add worker
path = Path(r"C:\Users\h232559\Desktop\fire\yanxiang_face")

for img_path in path.glob("*.jpg"):
    eid = img_path.stem
    r = requests.post(BASE_URL+"/factory/1/worker",
                      json={"eid": eid, "name": eid})

    print("{}: {}".format(eid, r.status_code))

    r = requests.post(BASE_URL+"/factory/1/workstation/1/worker", json={"eid": eid})

    print("{}: {}".format(eid, r.status_code))

    with img_path.open("rb") as f:
        r = requests.post(BASE_URL+"/factory/1/worker/{}/face".format(eid),
                          files={"file": f})
        print("{}: {}".format(eid, r.status_code))

path = Path(r"C:\Users\h232559\Desktop\fire\wenxiang_face")

for img_path in path.glob("*.jpg"):
    eid = img_path.stem
    r = requests.post(BASE_URL+"/factory/1/worker",
                      json={"eid": eid, "name": eid})

    print("{}: {}".format(eid, r.status_code))

    r = requests.post(BASE_URL+"/factory/1/workstation/2/worker", json={"eid": eid})

    print("{}: {}".format(eid, r.status_code))

    with img_path.open("rb") as f:
        r = requests.post(BASE_URL+"/factory/1/worker/{}/face".format(eid),
                          files={"file": f})
        print("{}: {}".format(eid, r.status_code))

# add camera
camera_ids = ["242", "249", "245"]
camera_urls = [
    "rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcigyNDIpL3N0cmVhbT9zdWJ0eXBlPVByaXZhdGVfaG9uZXk=",
    "rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcigyNDkpL3N0cmVhbT9zdWJ0eXBlPVByaXZhdGVfaG9uZXk=",
    "rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcjJfMjQ1L3N0cmVhbT9zdWJ0eXBlPVByaXZhdGVfaG9uZXk="
]

for camera_id, camera_url in zip(camera_ids, camera_urls):
    requests.post(BASE_URL + "/camera", json={
        "cameraId": camera_id,
        "uri": camera_url
    })

requests.put(BASE_URL + "/camera/equipment_camera/equipment/{}".format(1),
              json={
                  "cameraId": "242",
                  "xmin": 0.23385,
                  "xmax": 0.57604,
                  "ymin": 0.10556,
                  "ymax": 0.40556
              })

requests.put(BASE_URL + "/camera/keyperson_camera/workstation/{}".format(1),
              json={
                  "cameraId": "245"
              })

requests.put(BASE_URL + "/camera/keyperson_camera/workstation/{}".format(2),
              json={
                  "cameraId": "249"
              })

# upload equipment model
model_file_path = Path(r"C:\Users\h232559\Desktop\test_imgs\result.pb")
with model_file_path.open("rb") as f:
    requests.put(BASE_URL + "/equipment/{}/equipment_model".format(1), files={"file": f})
