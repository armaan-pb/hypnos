import sys
import numpy as np
import matplotlib.pyplot as pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QToolBar, QVBoxLayout, 
    QHBoxLayout, QAction, QFrame, QPushButton
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QPoint

# --- Constants ---
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 720
TITLEBAR_HEIGHT = 30
HOURS_IN_DAY = 24
CIRCLE_RADIANS = 2 * np.pi
TICK_INTERVAL = 1
SLEEP_BAR_COLOR = '#FF0000'
SLEEP_BAR_ALPHA = 0.6
SLEEP_BAR_EDGE_COLOR = 'black'
BACKGROUND_COLOR = '#121212'
FOREGROUND_COLOR = 'white'
GRID_COLOR = 'gray'
GRID_LINESTYLE = '--'
GRID_LINEWIDTH = 0.5
GRID_ALPHA = 0.3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle("Hypnos")
        self.setWindowIcon(QIcon("assets/Hypnos-icon.png"))

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)

        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)

        body = QWidget()
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body.setLayout(body_layout)
        main_layout.addWidget(body)

        self.sleep_chart = SleepDonutChart(sleep_sessions)
        body_layout.addWidget(self.sleep_chart)


class TitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(TITLEBAR_HEIGHT)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e2f;
                color: {FOREGROUND_COLOR};
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {FOREGROUND_COLOR};
                font-size: 16px;
                padding: 0 8px;
            }}
            QPushButton:hover {{
                background-color: #2e2e40;
            }}
            QPushButton#close:hover {{
                background-color: #ff5c5c;
            }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 0, 0)

        self.title = QLabel("Hypnos")
        self.title.setFont(QFont("Arial", 10))
        layout.addWidget(self.title)

        layout.addStretch()

        self.min_btn = QPushButton("-")
        self.max_btn = QPushButton("^")
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("close")

        self.min_btn.clicked.connect(self.parent.showMinimized)
        self.max_btn.clicked.connect(self.toggle_max_restore)
        self.close_btn.clicked.connect(self.parent.close)

        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)
        self.start_pos = None

    def toggle_max_restore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.start_pos:
            delta = event.globalPos() - self.start_pos
            self.parent.move(self.parent.pos() + delta)
            self.start_pos = event.globalPos()


class SleepDonutChart(QWidget):
    def __init__(self, sleep_sessions, parent=None):
        super().__init__(parent)
        self.sleep_sessions = sleep_sessions
        self.initChart()

    def initChart(self):
        self.figure, self.ax = pyplot.subplots(subplot_kw={'projection': 'polar'})
        self.canvas = FigureCanvas(self.figure)

        self.applyStyling()

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.plotSessions()

    def applyStyling(self):
        self.figure.patch.set_facecolor(BACKGROUND_COLOR)
        self.ax.set_facecolor(BACKGROUND_COLOR)
        self.ax.tick_params(colors=FOREGROUND_COLOR)
        self.ax.spines[:].set_color(FOREGROUND_COLOR)
        self.ax.xaxis.label.set_color(FOREGROUND_COLOR)
        self.ax.title.set_color(FOREGROUND_COLOR)
        self.ax.grid(color=GRID_COLOR, linestyle=GRID_LINESTYLE, linewidth=GRID_LINEWIDTH, alpha=GRID_ALPHA)

    def convertSessionsToRadians(self):
        result = []

        for session in self.sleep_sessions:
            start_hour = session['start'] % HOURS_IN_DAY
            end_hour = session['end'] % HOURS_IN_DAY

            start_angle = (start_hour / HOURS_IN_DAY) * CIRCLE_RADIANS
            end_angle = (end_hour / HOURS_IN_DAY) * CIRCLE_RADIANS

            if end_angle <= start_angle:
                end_angle += CIRCLE_RADIANS

            block_width = end_angle - start_angle
            result.append((start_angle, block_width))

        return result

    def plotSessions(self):
        self.ax.clear()
        self.ax.set_theta_zero_location('N')
        self.ax.set_theta_direction(-1)

        ticks = np.linspace(0, CIRCLE_RADIANS, HOURS_IN_DAY // TICK_INTERVAL, endpoint=False)
        labels = [str(hour) for hour in range(0, HOURS_IN_DAY, TICK_INTERVAL)]
        self.ax.set_xticks(ticks)
        self.ax.set_xticklabels(labels)
        self.ax.set_yticklabels([])

        INNER_RADIUS=0.7
        BLOCK_THICKNESS=0.3

        for start_angle, block_width in self.convertSessionsToRadians():
            self.ax.bar(
                start_angle,
                BLOCK_THICKNESS,
                width=block_width,
                bottom=INNER_RADIUS,
                color=SLEEP_BAR_COLOR,
                alpha=SLEEP_BAR_ALPHA,
                edgecolor=SLEEP_BAR_EDGE_COLOR,
                align='edge'
            )

        donut_hole = pyplot.Circle(
            (0, 0),
            INNER_RADIUS,
            transform=self.ax.transData._b,
            facecolor=BACKGROUND_COLOR,
            edgecolor=FOREGROUND_COLOR,
            linewidth=2,
            zorder=3
        )

        self.ax.add_artist(donut_hole)

        self.canvas.draw()


sleep_sessions = [
    {'start': 22, 'end': 6},
    {'start': 12, 'end': 14}
]
