import numpy as np
import cv2
from matplotlib import pyplot as plt
import time


class FaceROI:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def get_face_ROI(self, img):
        x1 = 0.4
        x2 = 0.6
        y1 = 0.1
        y2 = 0.25
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)

        if len(faces) > 0:
            img = cv2.rectangle(
                img,
                (faces[0][0] + int(x1 * faces[0][2]), faces[0][1] + int(y1 * faces[0][3])),
                (faces[0][0] + int(x2 * faces[0][2]), faces[0][1] + int(y2 * faces[0][3])),
                (255, 0, 0),
                2
            )

            return [faces[0][0] + int(x1 * faces[0][2]), faces[0][1] + int(y1 * faces[0][3]),
                    faces[0][0] + int(x2 * faces[0][2]), faces[0][1] + int(y2 * faces[0][3])]
        else:
            return [0, 0, 0, 0]


cv2.namedWindow("tracking")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cap.set(cv2.CAP_PROP_FPS, 10)
fps = cap.get(cv2.CAP_PROP_FPS)
print(fps)
step = int(1000 / fps)

ok, frame = cap.read()
if not ok:
    print('Failed to read video from camera')
    exit()

plt.close()
fig = plt.figure()
plt.grid(True)
plt.ion()  # interactive mode on
plt.xlabel('Time'),
plt.ylabel('Amplitude')

plt.title('Heart rate and breath detection')
DELTA_FRAME_TO_UPDATE_FACE_ROI = 15
INDEX_TO_START_ACCUMULATING_DATA = 50


class Logic:
    def __init__(self):
        self.face_roi = FaceROI()
        self.frame_index = 0
        self.bbox = [0, 0, 10, 10]
        self.previous_frame = None
        self.green_avg = []

    def process_new_frame(self, frame):
        if self.previous_frame is None:
            self._update_bbox_from_frame(frame)
        else:
            df = (frame - self.previous_frame).abs().mean()
            if df > DELTA_FRAME_TO_UPDATE_FACE_ROI:
                self._update_bbox_from_frame(frame)

        self.previous_frame = frame
        self.frame_index += 1

        if self.frame_index > INDEX_TO_START_ACCUMULATING_DATA:
            roi = frame[bbox[1]:bbox[3], bbox[0]:bbox[2]]
            self.green_avg.append(roi[:, :, 1].mean())

    def render_face_bbox_to_frame(self, frame):
        return cv2.rectangle(frame, (self.bbox[0], self.bbox[1]), (self.bbox[2], self.bbox[3]), (255, 0, 0), 2)

    def _update_bbox_from_frame(self, frame):
        roi = self.face_roi.get_face_ROI(frame)
        if roi[3] > 0:
            self.bbox = roi


flag = True
while (flag):
    # start = time.clock()
    ret, frame = cap.read()

    if (idf == 0):

        droi = face_roi.get_face_ROI(frame)
        if (droi[3] > 0):
            bbox = droi

    if (idf > 0):
        df = cv2.absdiff(frame, previous_frame)
        m_diff = 1.0 * df.sum() / (df.shape[0] * df.shape[1])

        if (m_diff > 15):
            droi = face_roi.get_face_ROI(frame)
            if (droi[3] > 0):
                bbox = droi

    roi = frame[bbox[1]:bbox[3], bbox[0]:bbox[2]];
    frame = cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)

    green = getColorAverage(roi, 1)  ## 2nd channel for Green color
    if (idf > 50):
        gsums.append(green)

    idf += 1
    previous_frame = frame
    cv2.imshow("tracking", frame);

    if (idf > 0):
        plt.clf()
        plt.plot(gsums[-200:-1], 'g')
        plt.pause(0.001)
        plt.ioff()
    k = cv2.waitKey(step) & 0xff
    # end = time.clock()
    if k == 27:  # esc pressed
        flag = False
        break

        # exit when tracking windows is closed
    if cv2.getWindowProperty('tracking', cv2.WND_PROP_AUTOSIZE) < 1:
        cap.release()
        break

plt.close()
cv2.destroyAllWindows()
cv2.waitKey(1)
print("Execution has finished")
