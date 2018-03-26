import cv2

url = r"rtsp://119.23.207.98:2553/stream/live?token=dXJsOk1TQ1A6Ly9LX1Rlc3RlcjI0NC9zdHJlYW0/c3VidHlwZT1Qcml2YXRlX2hvbmV5"

cap = cv2.VideoCapture(url)

while True:
    _, frame = cap.read()

    cv2.imshow("", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()