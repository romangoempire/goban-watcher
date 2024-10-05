import time

import cv2
import numpy as np
from icecream import ic

from custom_logger import logger

cap = cv2.VideoCapture(5)

if not cap.isOpened():
    logger.fatal("Could not open camera.")
    exit()

last_frame = None
while True:
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    ret, frame = cap.read()

    if not ret:
        logger.warning("Could not read frame.")
        time.sleep(2)
        continue

    # first frame
    if last_frame is None:
        last_frame = frame
        continue

    difference = cv2.absdiff(last_frame, frame)
    difference = cv2.convertScaleAbs(difference)
    gray_diff = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

    amount_difference = np.count(gray_diff)
    w, h = gray_diff.shape
    percentage_difference = round(amount_difference / (w * h) * 100, 1)
    ic(percentage_difference)
    cv2.imshow("Original Frame", frame)
    cv2.imshow("Change", cv2.cvtColor(gray_diff, cv2.COLOR_GRAY2BGR))

    last_frame = frame

cap.release()
cv2.destroyAllWindows()
