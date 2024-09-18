import cv2
import time

cap = cv2.VideoCapture(3)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        time.sleep(2)
    cv2.imshow("Camera Output", frame)


cap.release()
cv2.destroyAllWindows()
