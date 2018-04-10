import cv2
import logging

path = {"wenxiang": r"rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcigyNDkpL3N0cmVhbT9zdWJ0eXBlPVByaXZhdGVfaG9uZXk=",
        "yanxiang": r"rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcjJfMjQ1L3N0cmVhbT9zdWJ0eXBlPVByaXZhdGVfaG9uZXk="}

# cap = cv2.VideoCapture(path)
cap = cv2.VideoCapture(path.get("yanxiang"))

while True:

    if cap.isOpened() is False:
        break
    _, frame = cap.read()
    # if frame is None:
    #     time.sleep(1)
    #     continue

    if frame is None:
        print("frame is None")
        continue

    frame = cv2.resize(frame, dsize=None, fx=0.5, fy=0.5)
    # out.write(frame)
    cv2.imshow("frame", frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

cap.release()