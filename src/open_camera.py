import time

import cv2

from custom_logger import logger

cap = cv2.VideoCapture(2)

if not cap.isOpened():
    logger.fatal("Could not open camera")
    exit()

while True:
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    ret, frame = cap.read()

    if not ret:
        logger.warning("Could not read frame")
        time.sleep(2)
        continue

    cv2.imshow("Image", frame)

cap.release()
cv2.destroyAllWindows()
