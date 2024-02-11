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


class MainWindow:
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.update_interval_sec = 0.01
        self.sampling_interval = 0.2
        layout = [
            [
                sg.Text(key="text")
            ],
            [
                sg.Canvas(key="green_avg", size=(300, 300)),
                sg.Canvas(key="spectrum", size=(300, 300)),
            ],
            [
                sg.Canvas(key="face", size=(
                    int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                )),
            ],
        ]
        self.window = sg.Window("2 Figures and Text Box", layout)
        self.figure = matplotlib.figure.Figure(figsize=(3, 3), dpi=100)
        self.logic = Logic()

    def plot_spectrum(self):
        self.figure.clf()
        ax = self.figure.add_subplot(111)
        f, p = signal.welch(self.logic.green_avg[-2048:], fs=1 / self.sampling_interval, average='median', nperseg=64)
        ax.plot(f, p, 'r')

        bpm = [150, 120, 90, 60, 45]
        freq = [60 / b for b in bpm]
        ax.set_xticks(freq)
        ax.set_xticklabels(bpm)
        ax.set_xlim(min(freq), max(freq))
        ax.grid()
        return draw_figure(self.figure)

    def run(self):
        t0 = time.time()
        while True:
            event, values = self.window.read(timeout=int(self.update_interval_sec * 1e3))
            dt = time.time() - t0
            if dt < self.sampling_interval:
                continue
            print(dt / self.sampling_interval)
            t0 = time.time()

            if event == sg.WIN_CLOSED:
                break

            ok, frame = self.cap.read()
            if not ok:
                print('Failed to read video from camera')
                break

            self.logic.process_new_frame(frame)

            self.window['text'].update(f"Samples: {len(self.logic.green_avg)}")
            frame_with_bbox = ImageTk.PhotoImage(
                ImageOps.mirror(Image.fromarray(self.logic.render_face_bbox_to_frame(frame)))
            )
            self.window['face'].TKCanvas.create_image(
                frame_with_bbox.width() / 2, frame_with_bbox.height() / 2, image=frame_with_bbox
            )

            self.figure.clf()
            ax = self.figure.add_subplot(111)
            ax.plot(self.logic.green_avg[-200:-1], 'g')
            figure_avg = draw_figure(self.figure)
            self.window['green_avg'].TKCanvas.create_image(150, 150, image=figure_avg)

            if len(self.logic.green_avg) % 8 == 0:
                figure_spectrum = self.plot_spectrum()
                self.window['spectrum'].TKCanvas.create_image(150, 150, image=figure_spectrum)

        self.window.close()


if __name__ == '__main__':
    MainWindow().run()
