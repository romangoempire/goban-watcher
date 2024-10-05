import time

import cv2

from custom_logger import logger

cap = cv2.VideoCapture(5)

if not cap.isOpened():
    logger.fatal("Could not open camera")
    exit()

last_frame = None
while True:
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    ret, frame = cap.read()

    if not ret:
        logger.warning("Could not read frame")
        time.sleep(2)
        continue

    # first frame
    if last_frame is None:
        last_frame = frame
        continue

    cv2.imshow("Image", frame)

    last_frame = frame

cap.release()
cv2.destroyAllWindows()
