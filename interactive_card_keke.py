import cv2
import numpy as np
from Ax12 import Ax12
import sys, time

thresh = 25
max_diff = 5
n = 17

cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1360)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 765)
fps = int(cap.get(cv2.CAP_PROP_FPS))

width = int(1360 / n)

if not cap.isOpened():
    sys.exit()

ax12 = Ax12(n)
ax12.ready()

ret, frame1 = cap.read()
ret, frame2 = cap.read()

gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

start_time = time.time()
while True:
    if time.time() - start_time > 60:
        ax12.set_index()
        start_time = time.time()

    ret, frame = cap.read()

    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    diff1 = cv2.absdiff(gray1, gray)
    diff2 = cv2.absdiff(gray2, gray)

    ret, diff1_t = cv2.threshold(diff1, thresh, 255, cv2.THRESH_BINARY)
    ret, diff2_t = cv2.threshold(diff2, thresh, 255, cv2.THRESH_BINARY)

    diff = cv2.bitwise_and(diff1_t, diff2_t)

    k = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, k)

    for i in range(n):
        res = diff[:, width * i : width * (i + 1)]
        diff_cnt = cv2.countNonZero(res)
        if diff_cnt > max_diff:
            nzero = np.nonzero(res)
            cv2.rectangle(
                frame,
                (width * i, 0),
                (width * (i + 1), 718),
                (0, 255, 0),
                2,
            )
            ax12.move(i)
        else:
            ax12.center(i)

    stacked = np.hstack((frame, cv2.cvtColor(diff, cv2.COLOR_GRAY2BGR)))
    cv2.imshow("motion", stacked)

    key = cv2.waitKey(fps) & 0xFF
    if key == 27:
        break
    elif key == ord("r"):
        ret, frame1 = cap.read()
        ret, frame2 = cap.read()

        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

cv2.destroyAllWindows()
cap.release()
ax12.release()