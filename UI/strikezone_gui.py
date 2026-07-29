#VENV
import sys
import os
import pandas as pd
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QCheckBox, QPushButton, QGraphicsRectItem
import pyqtgraph as pg

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import PyScripts.StrikeZoneLogic as SZ


class StrikeZoneGUI(QtWidgets.QMainWindow):

    pitch_colors = {
        "FF": "#d22d49", "FT": "#DE6A04", "SI": "#FE9D00",
        "FC": "#933F2C", "CH": "#1DBE3A", "FS": "#3BACAC",
        "FO": "#55CCAB", "SC": "#60DB33", "CU": "#00D1ED",
        "KC": "#6236CD", "CS": "#0068ff", "SL": "#eee716",
        "ST": "#ddb33a", "SV": "#93afd4", "KN": "#3c44cd",
        "EP": "#888888"
    }

    def __init__(self, csv_path, lineup, game_id, side):
        super().__init__()

        # Data
        self.csv_path = csv_path
        self.lineup = lineup
        self.current_index = 0
        self.game_id = game_id
        self.side = side

        # Pitch tracking
        self.pitch_log = []
        self.total_pitches = 0
        self.atbat_pitches = 0
        self.current_pitch_type = None
        self.last_point = None

        # UI
        self.stack = QtWidgets.QStackedLayout()
        central = QtWidgets.QWidget()
        central.setLayout(self.stack)
        self.setCentralWidget(central)

        self.init_pitch_selection_ui()
        self.init_strikezone_ui()

        # Load first batter
        self.load_batter(self.lineup[self.current_index]["name"])


    # ---------------------------------------------------------
    # UI SETUP
    # ---------------------------------------------------------

    def init_pitch_selection_ui(self):
        """Pitch type selection screen."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(widget)

        pitch_types = list(self.pitch_colors.items())
        row = col = 0

        for pitch, color in pitch_types:
            btn = QtWidgets.QPushButton(pitch)
            btn.setStyleSheet(f"background-color: {color}; font-size: 20px; font-weight: bold;")
            btn.clicked.connect(lambda _, p=pitch: self.select_pitch_type(p))
            layout.addWidget(btn, row, col)

            col += 1
            if col >= 4:
                col = 0
                row += 1

        self.next_batter_checkbox = QCheckBox("Next Batter")
        self.pinch_button = QtWidgets.QPushButton("Pinch Hitter")
        self.pinch_button.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.pinch_button.clicked.connect(self.handle_pinch_hitter)
        layout.addWidget(self.pinch_button)


        layout.addWidget(self.pinch_button)

        self.stack.addWidget(widget)
    def init_strikezone_ui(self):
        """Strike zone drawing screen."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # Back button
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self.go_back_to_pitch_selection)
        layout.addWidget(back_btn)

        # Batter label
        self.batter_label = QtWidgets.QLabel("")
        self.batter_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(self.batter_label)

        # Pitch counter
        self.pitch_counter_label = QtWidgets.QLabel("Total: 0 | At-Bat: 0")
        self.pitch_counter_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.pitch_counter_label)

        # Plot
        self.plot = pg.PlotWidget()
        layout.addWidget(self.plot)

        # Confirm button
        confirm_btn = QtWidgets.QPushButton("Confirm Point")
        confirm_btn.clicked.connect(self.confirm_point)
        layout.addWidget(confirm_btn)



        # Plot items
        self.scatter = pg.ScatterPlotItem(size=10, brush=pg.mkBrush('y'))
        self.cursor_dot = pg.ScatterPlotItem(size=12, brush=pg.mkBrush('#00FF00'))
        self.pitch_history = pg.ScatterPlotItem(size=12)

        self.plot.addItem(self.scatter)
        self.plot.addItem(self.cursor_dot)
        self.plot.addItem(self.pitch_history)

        # Events
        self.plot.scene().sigMouseClicked.connect(self.on_plot_clicked)
        self.plot.scene().sigMouseMoved.connect(self.on_mouse_move)

        self.stack.addWidget(widget)

    # ---------------------------------------------------------
    # BATTER LOADING
    # ---------------------------------------------------------

    def load_batter(self, batter_name):
        """Load batter strike zone dimensions and update UI."""
        df = pd.read_csv(self.csv_path)

        try:
            row = df.loc[df['Player Name (ASCII)'] == batter_name].iloc[0]
        except IndexError:
            print(f"Batter '{batter_name}' not found in CSV")
            return

        zone_top = float(row['Top of Zone (Height * 0.535)'])
        zone_bottom = float(row['Bottom of Zone (Height * 0.27)'])
        zone_height = zone_top - zone_bottom
        zone_width = 17.0

        # Update batter label
        self.batter_label.setText(batter_name.split()[-1])

        # Load player into StrikeZoneLogic
        SZ.player = batter_name
        SZ.load_player(batter_name)

        # Reset plot
        self.plot.clear()
        self.plot.showGrid(x=True, y=True)
        self.plot.setXRange(-1, 1)
        self.plot.setYRange(-1, 1)

        self.draw_grid_lines()

        # Re-add scatter items
        self.plot.addItem(self.pitch_history)
        self.plot.addItem(self.scatter)
        self.plot.addItem(self.cursor_dot)

        # Draw strike zone rectangle
        height_scale = 1.0
        width_scale = zone_width / zone_height
        x_left = -width_scale / 2
        y_bottom = -height_scale / 2

        rect = QGraphicsRectItem(x_left, y_bottom, width_scale, height_scale)
        rect.setPen(pg.mkPen('r', width=3))
        self.plot.addItem(rect)

        print(f"Loaded batter: {batter_name}")

    # ---------------------------------------------------------
    # PITCH SELECTION
    # ---------------------------------------------------------

    def select_pitch_type(self, pitch):
        self.current_pitch_type = pitch

        if self.next_batter_checkbox.isChecked():
            self.advance_batter()
            self.next_batter_checkbox.setChecked(False)

        self.stack.setCurrentIndex(1)

    def advance_batter(self):
        self.current_index = (self.current_index + 1) % len(self.lineup)
        self.atbat_pitches = 0
        SZ.player = self.lineup[self.current_index]
        SZ.load_player(SZ.player)
        self.load_batter(self.lineup[self.current_index]['name'])

    def go_back_to_pitch_selection(self):
        if self.total_pitches > 0:
            self.total_pitches -= 1
        if self.atbat_pitches > 0:
            self.atbat_pitches -= 1

        self.pitch_counter_label.setText(
            f"Total: {self.total_pitches} | At-Bat: {self.atbat_pitches}"
        )
        self.stack.setCurrentIndex(0)

    # ---------------------------------------------------------
    # PLOT INTERACTION
    # ---------------------------------------------------------

    def on_plot_clicked(self, event):
        pos = event.scenePos()
        mouse_point = self.plot.plotItem.vb.mapSceneToView(pos)
        x, y = mouse_point.x(), mouse_point.y()

        self.last_point = (x, y)
        self.scatter.addPoints([{'pos': (x, y)}])

        print(f"Clicked point: X={x:.3f}, Y={y:.3f}")

    def on_mouse_move(self, pos):
        mouse_point = self.plot.plotItem.vb.mapSceneToView(pos)
        x, y = mouse_point.x(), mouse_point.y()

        if -1 <= x <= 1 and -1 <= y <= 1:
            self.cursor_dot.setData([{'pos': (x, y)}])

    # ---------------------------------------------------------
    # CONFIRM PITCH
    # ---------------------------------------------------------

    def confirm_point(self):
        if self.last_point is None:
            print("No point selected yet.")
            return

        x, y = self.last_point

        self.total_pitches += 1
        self.atbat_pitches += 1

        self.pitch_counter_label.setText(
            f"Total: {self.total_pitches} | At-Bat: {self.atbat_pitches}"
        )

        color = self.pitch_colors.get(self.current_pitch_type, "white")
        self.pitch_history.addPoints([{
            "pos": (x, y),
            "brush": pg.mkBrush(color),
            "pen": pg.mkPen(color)
        }])

        self.pitch_log.append((x, y, self.current_pitch_type))
        print(f"Confirmed pitch: {self.current_pitch_type} at X={x:.3f}, Y={y:.3f}")

        self.send_to_unity(x, y)
        self.stack.setCurrentIndex(0)

    # ---------------------------------------------------------
    # UNITY SEND
    # ---------------------------------------------------------

    def send_to_unity(self, x, y):
        from PyScripts.JSONWrite import json_template
        from PyScripts.WebSocketsClient import notify_server

        dim_df = pd.read_csv(self.csv_path)

        filename, json_data = json_template(
            pitch_num_total=self.total_pitches,
            pitch_ab=self.atbat_pitches,
            pitch_type=self.current_pitch_type,
            x=x,
            y=y,
            batter=SZ.player,
            id=dim_df.loc[dim_df['Player Name (ASCII)'] == SZ.player, 'SC_ID'].item(),
            zone_b=dim_df.loc[dim_df['Player Name (ASCII)'] == SZ.player, 'Bottom of Zone (Height * 0.27)'].item(),
            zone_t=dim_df.loc[dim_df['Player Name (ASCII)'] == SZ.player, 'Top of Zone (Height * 0.535)'].item(),
            handedness="LOOK UP"
        )

        print("JSON saved:", filename)
        notify_server(json_data)
        print("JSON sent successfully.")

    # ---------------------------------------------------------
    # GRID LINES
    # ---------------------------------------------------------

    def draw_grid_lines(self):
        for item in getattr(self, "grid_lines", []):
            self.plot.removeItem(item)

        self.grid_lines = []

        origin_v = pg.InfiniteLine(pos=0, angle=90, pen=pg.mkPen('#00AAFF', width=2))
        origin_h = pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen('#00AAFF', width=2))

        self.grid_lines.extend([origin_v, origin_h])

        intervals = [0.25, 0.50, 0.75]
        for val in intervals:
            self.grid_lines.append(pg.InfiniteLine(pos=val, angle=90, pen=pg.mkPen('#CCCCCC')))
            self.grid_lines.append(pg.InfiniteLine(pos=-val, angle=90, pen=pg.mkPen('#CCCCCC')))
            self.grid_lines.append(pg.InfiniteLine(pos=val, angle=0, pen=pg.mkPen('#CCCCCC')))
            self.grid_lines.append(pg.InfiniteLine(pos=-val, angle=0, pen=pg.mkPen('#CCCCCC')))

        for line in self.grid_lines:
            self.plot.addItem(line)

    # ---------------------------------------------------------
    # PINCH HANDLER
    # ---------------------------------------------------------
    def handle_pinch_hitter(self):
      from Utils.SubstitutionUtils.pinch_hitter_handler import fetch_updated_lineup
      print("Fetching updated lineup from MLB StatsAPI...")

      updated_lineup = fetch_updated_lineup(self.game_id, self.side)

      if not updated_lineup:
        print("No updated lineup found.")
        return

    # Replace lineup
      self.lineup = updated_lineup
      self.current_index = 0

    # Load new batter
      new_batter = self.lineup[self.current_index]["name"]
      print(f"New batter due to pinch hitter: {new_batter}")

      self.load_batter(new_batter)
