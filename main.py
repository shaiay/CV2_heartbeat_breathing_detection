import PySimpleGUI as sg
from PIL import Image, ImageTk, ImageOps
import cv2
from scipy import signal

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasAgg
from frame_processing_logic import Logic



def draw_figure(figure):
    figure_canvas_agg = FigureCanvasAgg(figure)
    figure_canvas_agg.draw()
    return ImageTk.PhotoImage(Image.frombuffer('RGBA', (300, 300),figure_canvas_agg.buffer_rgba()))


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
update_interval_msec = 10
layout = [
    [
        sg.Text(key="text")
    ],
    [
        sg.Canvas(key="green_avg", size=(300, 300)),
        sg.Canvas(key="spectrum", size=(300, 300)),
    ],
    [
        sg.Canvas(key="face", size=(cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT))),
    ],
]

window = sg.Window("2 Figures and Text Box", layout)
fig = matplotlib.figure.Figure(figsize=(3, 3), dpi=100)
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

    window['text'].update(f"Samples: {len(logic.green_avg)}")
    frame_with_bbox = ImageTk.PhotoImage(
        ImageOps.mirror(Image.fromarray(logic.render_face_bbox_to_frame(frame)))
    )
    window['face'].TKCanvas.create_image(
        frame_with_bbox.width() / 2, frame_with_bbox.height() / 2, image=frame_with_bbox
    )

    fig.clf()
    ax = fig.add_subplot(111)
    ax.plot(logic.green_avg[-200:-1], 'g')
    figure_avg = draw_figure(fig)
    window['green_avg'].TKCanvas.create_image(150, 150, image=figure_avg)

    if len(logic.green_avg) % 8 == 0:
        fig.clf()
        ax = fig.add_subplot(111)
        f, p = signal.welch(logic.green_avg, fs=1000 / update_interval_msec)
        ax.plot(f, p, 'r')
        figure_spectrum = draw_figure(fig)
        window['spectrum'].TKCanvas.create_image(150, 150, image=figure_spectrum)



window.close()
