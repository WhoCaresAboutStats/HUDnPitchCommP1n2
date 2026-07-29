import pandas as pd
import statsapi as st
import requests

height_csv = r"C:\Users\nitro\WhoCaresAboutHUDandPitchComms\csv\NewHeightMetrics(ZoneDim).csv"
height_df = pd.read_csv(height_csv)

def new_height(player_id):
  bio = get_player_height(player_id)
  if not bio:
    print("Could not fetch height.")
    return

  metrics = compute_height_metrics(bio)
  add_player_to_csv(metrics)

def get_player_height(player_id):
    # Convert Statcast ID → MLB People ID
  mlb_id = get_mlb_people_id(player_id)
  if mlb_id is None:
    print("Could not resolve MLB People ID")
    return None

  url = f"https://statsapi.mlb.com/api/v1/people/{mlb_id}"
  response = requests.get(url).json()

  if "people" not in response or len(response["people"]) == 0:
    print("nobody there")
    return None

  player = response["people"][0]

  full_name = player.get("fullName")
  height_raw = player.get("height")  # example: 6' 2"

  if not height_raw:
    return None

    # Convert "6' 2\"" → "6-2"
  feet, inches = height_raw.replace('"', '').split("' ")
  height_ft_in = f"{feet}-{inches}"

  return {
    "player_id": player_id,
    "full_name": full_name,
    "ascii_name": full_name.encode("ascii", "ignore").decode(),
    "height_ft": int(feet),
    "height_in": int(inches),
    "height_ft_in": height_ft_in
  }

def get_mlb_people_id(statcast_id):
    players = st.lookup_player(statcast_id)
    if not players:
        return None
    return players[0]["id"]   # MLB People ID

def compute_height_metrics(bio):
  feet = bio["height_ft"]
  inches = bio["height_in"]

  feet_times_12 = feet * 12
  total_inches = feet_times_12 + inches

  top_zone = total_inches * 0.535
  top_zone = round(top_zone, 4)

  bottom_zone = total_inches * 0.27
  bottom_zone = round(bottom_zone, 4)

  area_zone = 17 * (top_zone - bottom_zone)
  area_zone = round(area_zone, 4)

  midpoint = (top_zone + bottom_zone) / 2
  midpoint = round(midpoint, 4)

  return {
    "ascii_name": bio["ascii_name"],
    "height_ft_in": bio["height_ft_in"],
    "feet_times_12": feet_times_12,
    "total_inches": total_inches,
    "top_zone": top_zone,
    "bottom_zone": bottom_zone,
    "area_zone": area_zone,
    "midpoint": midpoint,
    "full_name": bio["full_name"],
    "player_id": bio["player_id"]
  }

def add_player_to_csv(metrics):
  columns = [
    "Player Name (ASCII)",
    "Height (ft - in)",
    "Height (ft * 12) w/o in",
    "Height ((ft*12) + in)",
    "Top of Zone (Height * 0.535)",
    "Bottom of Zone (Height * 0.27)",
    "Area of Zone (17 * (Top - Bottom))",
    "Midpoint ((Top + Bottom) / 2)",
    "Player Name",
    "SC_ID"
  ]

  df = height_df  # already loaded at top

    # Skip if exists
  if metrics["player_id"] in df["SC_ID"].values:
    print(f"{metrics['full_name']} already exists.")
    return df

  df.loc[len(df)] = [
    metrics["ascii_name"],
    metrics["height_ft_in"],
    metrics["feet_times_12"],
    metrics["total_inches"],
    metrics["top_zone"],
    metrics["bottom_zone"],
    metrics["area_zone"],
    metrics["midpoint"],
    metrics["full_name"],
    metrics["player_id"]
  ]

  df.to_csv(height_csv, index=False)
  print(f"Added {metrics['full_name']} to CSV.")
  return df

# Test Shawn Ross
#print(new_height(676566))
