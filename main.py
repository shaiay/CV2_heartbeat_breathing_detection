import PySimpleGUI as sg
import matplotlib.pyplot as plt

import cv2

from frame_processing_logic import Logic


def create_layout():
    layout = [
        [sg.Text("Enter data for both graphs:"), sg.InputText(key="data")],
        [
            sg.Canvas(key="face"),
            sg.Canvas(key="green_avg"),
        ],
        [sg.Button("Plot Graphs")],
    ]
    return layout


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
update_interval_msec = 100
layout = create_layout()

window = sg.Window("2 Figures and Text Box", layout)
logic = Logic()

while True:
    event, values = window.read(timeout=update_interval_msec)

    if event == sg.WIN_CLOSED:
        break

    ok, frame = cap.read()
    if not ok:
        print('Failed to read video from camera')
        break

    logic.process_new_frame(frame)
    window['face'].update(logic.render_face_bbox_to_frame(frame))

window.close()
