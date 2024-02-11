import cv2
import numpy as np


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
            df = np.abs(frame - self.previous_frame).mean()
            if df > DELTA_FRAME_TO_UPDATE_FACE_ROI:
                self._update_bbox_from_frame(frame)

        self.previous_frame = frame
        self.frame_index += 1

        if self.frame_index > INDEX_TO_START_ACCUMULATING_DATA:
            roi = frame[self.bbox[1]:self.bbox[3], self.bbox[0]:self.bbox[2]]
            self.green_avg.append(roi[:, :, 1].mean())

    def render_face_bbox_to_frame(self, frame):
        return cv2.rectangle(frame, (self.bbox[0], self.bbox[1]), (self.bbox[2], self.bbox[3]), (255, 0, 0), 2)

    def _update_bbox_from_frame(self, frame):
        roi = self.face_roi.get_face_ROI(frame)
        if roi[3] > 0:
            self.bbox = roi
