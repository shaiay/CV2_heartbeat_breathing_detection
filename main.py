import time

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
    return ImageTk.PhotoImage(Image.frombuffer('RGBA', (300, 300), figure_canvas_agg.buffer_rgba()))


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
update_interval_sec = 0.01
sampling_interval = 0.2
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
figure = matplotlib.figure.Figure(figsize=(3, 3), dpi=100)
logic = Logic()

t0 = time.time()


def plot_spectrum(fig):
    fig.clf()
    ax = fig.add_subplot(111)
    f, p = signal.welch(logic.green_avg[-2048:], fs=1 / sampling_interval, average='median', nperseg=64)
    ax.plot(f, p, 'r')

    bpm = [150, 120, 90, 60, 45]
    freq = [60 / b for b in bpm]
    ax.set_xticks(freq)
    ax.set_xticklabels(bpm)
    ax.set_xlim(min(freq), max(freq))
    ax.grid()
    return draw_figure(fig)


while True:
    event, values = window.read(timeout=int(update_interval_sec * 1e3))
    dt = time.time() - t0
    if dt < sampling_interval:
        continue
    print(dt / sampling_interval)
    t0 = time.time()

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

    figure.clf()
    ax = figure.add_subplot(111)
    ax.plot(logic.green_avg[-200:-1], 'g')
    figure_avg = draw_figure(figure)
    window['green_avg'].TKCanvas.create_image(150, 150, image=figure_avg)

    if len(logic.green_avg) % 8 == 0:
        figure_spectrum = plot_spectrum(figure)
        window['spectrum'].TKCanvas.create_image(150, 150, image=figure_spectrum)

window.close()
