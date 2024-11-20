import time

import cv2


cap = cv2.VideoCapture(2)

if not cap.isOpened():
    exit()

while True:
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    ret, frame = cap.read()

    if not ret:
        time.sleep(2)
        continue

    cv2.imshow("Image", frame)

cap.release()
cv2.destroyAllWindows()
