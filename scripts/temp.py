import cv2
import time


video_url = r"rtmp://119.23.207.98:1934/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcigyNDIpL3N0cmVhbT9zdWJ0eXBlPVByaXZhdGVfaG9uZXk="


cap = cv2.VideoCapture(video_url)

while True:
    _, frame = cap.read()

    if frame is None:
        continue

    frame = cv2.resize(frame, dsize=None, fx=0.5, fy=0.5)

    cv2.imshow("frame", frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
    # time.sleep(2)

cv2.destroyAllWindows()

cap.release()