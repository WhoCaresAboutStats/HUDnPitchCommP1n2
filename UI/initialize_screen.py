#VENV
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import statsapi as st
import pandas as pd
from datetime import datetime as dt
import tkinter as tk
from tkcalendar import Calendar
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QWidget, QApplication, QCheckBox, QPushButton, QGraphicsRectItem, QMainWindow, QVBoxLayout, QHBoxLayout, QCalendarWidget, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import QDate, Qt
import pyqtgraph as pg
from functools import partial

from Utils.LineUpUtils.debut_handler import new_height
from PyScripts import LineupManager
from PyScripts.LineupManager import load_lineup
from UI.strikezone_gui import StrikeZoneGUI


class LandingPage(QMainWindow):
  def __init__(self):
    super().__init__()
    self.selected_game = None

    self.height_csv = r"C:\Users\nitro\WhoCaresAboutHUDandPitchComms\csv\NewHeightMetrics(ZoneDim).csv"
    self.height_df = pd.read_csv(self.height_csv)

    self.init_ui()

  def init_ui(self):
    layout = QVBoxLayout()
    self.resize(1280, 720)
    self.move(
        (1920 - 1280)
        (1080 - 720)
    )



    self.calendar = QCalendarWidget()
    layout.addWidget(self.calendar)

    self.btn_transfer = QPushButton("Load Games for Selected Date")
    self.btn_transfer.clicked.connect(self.get_source_date)
    layout.addWidget(self.btn_transfer)

    container = QWidget()
    container.setLayout(layout)
    self.setCentralWidget(container)

    self.setWindowTitle('MLB Game Selector')
    self.show()

  def get_source_date(self):
    selected_date = self.calendar.selectedDate()
    print("Selected:", selected_date.toString())
    formated_date = selected_date.toString("yyyy-MM-dd")
    print("Formated:", formated_date)
    self.load_games(formated_date)
    return selected_date, formated_date

  def load_games(self, date):
    games = st.schedule(date=date)

    # Build list of game dictionaries
    games_list = []
    for game in games:
        games_list.append({
            'game_id': game['game_id'],
            'home_team': game['home_name'],
            'away_team': game['away_name'],
            'status': game['status'],
            'venue': game['venue_name'],
            'datetime': game['game_datetime']
        })

    # --- Create new screen ---
    game_screen = QWidget()
    main_layout = QVBoxLayout(game_screen)

    # Title
    title = QLabel(f"Games on {date}")
    title.setStyleSheet("font-size: 24px; font-weight: bold;")
    title.setContentsMargins(0, 20, 0, 20)
    main_layout.addWidget(title)

    # Scroll area
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    main_layout.addWidget(scroll)

    # Inner widget for scroll area
    inner = QWidget()
    inner_layout = QVBoxLayout(inner)

    # Create a button for each game
    for info in games_list:
        text = f"{info['away_team']} @ {info['home_team']} - {info['status']}"
        btn = QPushButton(text)

        # Make buttons bigger
        btn.setMinimumHeight(60)

        #ADD IN TEAM GRADIENTS
        btn.setStyleSheet("color: red; font-size: 18px")
        # Correct lambda capture
        btn.clicked.connect(partial(self.set_selected_game, info))

        inner_layout.addWidget(btn)

    scroll.setWidget(inner)


    footer = QWidget()
    footer_layout = QHBoxLayout(footer)

    btn_home = QPushButton("Home")
    btn_away = QPushButton("Away")

    btn_home.setMinimumHeight(50)
    btn_away.setMinimumHeight(50)

    btn_home.setStyleSheet("font-size: 20px; padding: 10px;")
    btn_away.setStyleSheet("font-size: 20px; padding: 10px;")

    btn_home.clicked.connect(lambda: self.confirm_side("home"))
    btn_away.clicked.connect(lambda: self.confirm_side("away"))

    footer_layout.addWidget(btn_home)
    footer_layout.addWidget(btn_away)

    main_layout.addWidget(footer)

    # Replace screen
    self.setCentralWidget(game_screen)

  def confirm_game(self, game_info):
    print("Selected Game:")
    print(game_info)

  def set_selected_game(self, game_info):
    self.selected_game = game_info
    print("Selected game:", game_info)

  def confirm_side(self, side):
    if self.selected_game is None:
      print("No game selected yet.")
      return

    print(f"Confirmed: {side.upper()} side for game:")
    box = st.boxscore_data(self.selected_game['game_id'])
    print(box)
    print(self.selected_game)
    if side == "away":
      lineup = self.get_away_lineup()

      validated_lineup = self.validate_lineup(lineup)

      # Send lineup directly to StrikeZone GUI
      self.send_lineup_to_strikezone(validated_lineup, side)

      # Optional: show lineup screen
      self.show_away_lineup_screen()
    elif side == "home":
      #FILL IN HOME
      pass

  def get_away_lineup(self):
    if self.selected_game is None:
      print("No game selected yet.")
      return []

    game_id = self.selected_game['game_id']
    box = st.boxscore_data(game_id)

    player_info = box["playerInfo"]
    lineup = []

    for player in box["awayBatters"]:
      order = player.get("battingOrder", "")
      if order == "":
        continue

      pid = player["personId"]
      key = f"ID{pid}"

      name = player_info[key]["fullName"]

      lineup.append({
        "order": int(order),
        "player_id": pid,
        "name": name,
        "position": player.get("position", "N/A")
      })

    lineup.sort(key=lambda x: x["order"])
    return lineup

  def show_away_lineup_screen(self):
    lineup = self.get_away_lineup()

    if not lineup:
      print("No lineup found.")
      return

    # New screen
    screen = QWidget()
    main_layout = QVBoxLayout(screen)

    # Title
    title = QLabel(f"Away Lineup for {self.selected_game['away_team']}")
    title.setStyleSheet("font-size: 24px; font-weight: bold;")
    title.setContentsMargins(0, 20, 0, 20)
    main_layout.addWidget(title)

    # Scroll area
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    main_layout.addWidget(scroll)

    # Inner widget
    inner = QWidget()
    inner_layout = QVBoxLayout(inner)

    # Add lineup rows
    for batter in lineup:
      row = QLabel(f"{batter['order']}. {batter['name']} - {batter['position']}")
      row.setStyleSheet("font-size: 18px; padding: 10px;")
      inner_layout.addWidget(row)

    scroll.setWidget(inner)

    # Back button
    back_btn = QPushButton("Back")
    back_btn.setMinimumHeight(50)
    back_btn.setStyleSheet("font-size: 20px; padding: 10px;")
    back_btn.clicked.connect(lambda: self.load_games(self.selected_game['datetime'][:10]))
    main_layout.addWidget(back_btn)

    # Replace screen
    self.setCentralWidget(screen)

  def player_in_height_csv(self, player_id):
    return player_id in self.height_df["SC_ID"].values

  def validate_lineup(self, lineup):
    # lineup is a list of dicts from get_away_lineup()
    for player in lineup:
      pid = player["player_id"]
      name = player["name"]

      if not self.player_in_height_csv(pid):
        print(f"{name} missing from height CSV — adding now...")
        new_height(pid)

        # Reload CSV after adding
        self.height_df = pd.read_csv(self.height_csv)

    # Return comma-separated names
    return lineup

  def send_lineup_to_strikezone(self, lineup, side):
    self.strikezone_window = StrikeZoneGUI(self.height_csv, lineup, self.selected_game['game_id'], side=side)
    self.strikezone_window.show()

if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = LandingPage()
  sys.exit(app.exec())