import sys
import os
import numpy as np
import matplotlib.pyplot as pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QToolBar, QVBoxLayout, 
    QHBoxLayout, QAction, QFrame, QPushButton, QLineEdit, QMessageBox, 
    QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QDialogButtonBox, QFormLayout, QAbstractItemView
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QPoint

from logic import SleepSessionManager


# --- Constants ---
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
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
    def __init__(self, session_manager):
        super().__init__()
        self.session_manager = session_manager
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle("Hypnos")
        self.setWindowIcon(QIcon("assets/Hypnos-icon.png"))

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()
        self.load_stylesheet()

    def load_stylesheet(self):
        try:
            from stylesloading import load_stylesheet
            self.setStyleSheet(load_stylesheet("#9F0707"))
        except Exception as e:
            print(f"Warning: Could not load stylesheet: {e}")


    def initUI(self):
        central_widget = QWidget()
        central_widget.setObjectName('centralWidget')
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)

        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)

        body = QWidget()
        body.setObjectName("body")
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(15, 15, 15, 15)
        body_layout.setSpacing(30)
        body.setLayout(body_layout)
        main_layout.addWidget(body)

        self.sleep_chart = SleepDonutChart(self.session_manager.get_sessions())
        self.sleep_chart.setMinimumSize(450, 450)
        self.sleep_chart.setMaximumSize(600, 600)
        self.sleep_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body_layout.addWidget(self.sleep_chart)

        self.sessions_panel = SessionsPanel(self)
        body_layout.addWidget(self.sessions_panel)

    def refresh_chart(self):
        self.sleep_chart.sleep_sessions = self.session_manager.get_sessions()
        self.sleep_chart.plotSessions()


class TitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("titleBar")
        self.setFixedHeight(TITLEBAR_HEIGHT)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 0, 0)

        self.title = QLabel("Hypnos")
        self.setObjectName("titleLabel")
        self.title.setFont(QFont("Arial", 10))
        layout.addWidget(self.title)

        layout.addStretch()

        self.min_btn = QPushButton("-")
        self.min_btn.setObjectName("minButton")
        self.min_btn.setToolTip("Minimize")
        self.max_btn = QPushButton("^")
        self.max_btn.setObjectName("maxButton")
        self.max_btn.setToolTip("Maximize")
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setToolTip("Close")

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
            linewidth=1,
            zorder=3
        )

        self.ax.add_artist(donut_hole)

        self.canvas.draw()


class AddSessionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Sleep Session")
        self.setModal(True)
        self.setFixedSize(300, 150)
        self.setObjectName("addSessionDialog")
        
        layout = QFormLayout()
        
        self.start_input = QLineEdit()
        self.start_input.setObjectName("dialogStartInput")
        self.start_input.setPlaceholderText("0-23")
        self.end_input = QLineEdit()
        self.end_input.setObjectName("dialogEndInput")
        self.end_input.setPlaceholderText("0-23")
        
        layout.addRow("Start Hour:", self.start_input)
        layout.addRow("End Hour:", self.end_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setObjectName("dialogButtons")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)
        self.setLayout(layout)
    
    def get_values(self):
        return self.start_input.text().strip(), self.end_input.text().strip()


class SessionsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.MainWindow = parent
        self.session_manager = parent.session_manager
        self.setObjectName("sessionsPanel")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        self.title_label = QLabel('Sessions', self)
        self.title_label.setObjectName("sessionsTitleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Segoe UI", 12))
        self.title_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.session_table = QTableWidget(self)
        self.session_table.setObjectName("sessionTable")
        self.session_table.setColumnCount(5)
        self.session_table.setHorizontalHeaderLabels(["Start Hour", "End Hour", "Duration", "Edit", "Delete"])

        h_header = self.session_table.horizontalHeader()
        h_header.setStretchLastSection(False)
        h_header.setSectionResizeMode(0, QHeaderView.Stretch)
        h_header.setSectionResizeMode(1, QHeaderView.Stretch)
        h_header.setSectionResizeMode(2, QHeaderView.Stretch)
        h_header.setSectionResizeMode(3, QHeaderView.Stretch)
        h_header.setSectionResizeMode(4, QHeaderView.Stretch)
        h_header.resizeSection(3, 50)
        h_header.resizeSection(4, 50)

        v_header = self.session_table.verticalHeader()
        v_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        v_header.setVisible(False)

        self.session_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.session_table.setAlternatingRowColors(False)
        self.session_table.setShowGrid(True)
        self.session_table.setMinimumHeight(200)

        self.add_button = QPushButton("Add Session", self)
        self.add_button.setObjectName("addButton")
        self.add_button.clicked.connect(self.show_add_dialog)

        self.populate_sessions_table()

        layout.addWidget(self.title_label)
        layout.addWidget(self.session_table)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def show_add_dialog(self):
        dialog = AddSessionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            start_text, end_text = dialog.get_values()
            try:
                start = int(start_text)
                end = int(end_text)
                if not (0 <= start < 24 and 0 <= end < 24):
                    raise ValueError

                self.session_manager.add_session(start, end)
                self.populate_sessions_table()
                self.MainWindow.refresh_chart()

            except ValueError:
                warn = QMessageBox(self.MainWindow)
                warn.setObjectName("warningDialog")
                warn.setIcon(QMessageBox.Warning)
                warn.setText("Invalid input")
                warn.setInformativeText("Please enter valid start and end hours (0-23)")
                warn.setWindowTitle("Warning")
                warn.exec()

    def edit_session(self, row):
        sessions = self.session_manager.get_sessions()
        if row >= len(sessions):
            return
            
        current_session = sessions[row]
        dialog = AddSessionDialog(self)
        dialog.setObjectName("editDialog")
        dialog.setWindowTitle("Edit Sleep Session")
        dialog.start_input.setText(str(current_session['start']))
        dialog.end_input.setText(str(current_session['end']))
        
        if dialog.exec_() == QDialog.Accepted:
            start_text, end_text = dialog.get_values()
            try:
                start = int(start_text)
                end = int(end_text)
                if not (0 <= start < 24 and 0 <= end < 24):
                    raise ValueError

                # Update the session
                sessions[row] = {"start": start, "end": end}
                self.session_manager.sessions = sessions
                self.session_manager.save_sessions()
                self.populate_sessions_table()
                self.MainWindow.refresh_chart()

            except ValueError:
                warn = QMessageBox(self.MainWindow)
                warn.setObjectName("warningDialog")
                warn.setIcon(QMessageBox.Warning)
                warn.setText("Invalid input")
                warn.setInformativeText("Please enter valid start and end hours (0-23)")
                warn.setWindowTitle("Warning")
                warn.exec()

    def delete_session(self, row):
        sessions = self.session_manager.get_sessions()
        if row >= len(sessions):
            return
            
        reply = QMessageBox(self)
        reply.setObjectName("warningDialog")
        reply.setIcon(QMessageBox.Question)
        reply.setWindowTitle('Delete Session')
        reply.setText('Are you sure you want to delete this session?')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply.setDefaultButton(QMessageBox.No)
        
        if reply.exec_() == QMessageBox.Yes:
            sessions.pop(row)
            self.session_manager.sessions = sessions
            self.session_manager.save_sessions()
            self.populate_sessions_table()
            self.MainWindow.refresh_chart()

    def populate_sessions_table(self):
        sessions = self.session_manager.get_sessions()
        self.session_table.setRowCount(len(sessions))

        for row, session in enumerate(sessions):
            start = session['start']
            end = session['end']

            if end >= start:
                duration = end - start
            else:
                duration = (24 - start) + end

            start_item = QTableWidgetItem(str(start))
            end_item = QTableWidgetItem(str(end))
            duration_item = QTableWidgetItem(f"{duration}h")

            start_item.setFlags(start_item.flags() & ~Qt.ItemIsEditable)
            end_item.setFlags(end_item.flags() & ~Qt.ItemIsEditable)
            duration_item.setFlags(duration_item.flags() & ~Qt.ItemIsEditable)

            start_item.setTextAlignment(Qt.AlignCenter)
            end_item.setTextAlignment(Qt.AlignCenter)
            duration_item.setTextAlignment(Qt.AlignCenter)

            self.session_table.setItem(row, 0, start_item)
            self.session_table.setItem(row, 1, end_item)
            self.session_table.setItem(row, 2, duration_item)

            edit_btn = QPushButton("✎")
            edit_btn.setObjectName("editButton")
            edit_btn.setToolTip("Edit Session")
            edit_btn.setFocusPolicy(Qt.NoFocus)
            edit_btn.clicked.connect(lambda checked, r=row: self.edit_session(r))
            self.session_table.setCellWidget(row, 3, edit_btn)

            delete_btn = QPushButton("✕")
            delete_btn.setObjectName("deleteButton")
            delete_btn.setToolTip("Delete Session")
            delete_btn.setFocusPolicy(Qt.NoFocus)
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_session(r))
            self.session_table.setCellWidget(row, 4, delete_btn)

        self.session_table.resizeRowsToContents()