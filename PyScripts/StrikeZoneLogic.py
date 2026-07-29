#VENV
#Imports
import pandas as pd
from unidecode import unidecode

# Load CSVs once
dim_path = "C:\\Users\\nitro\\WhoCaresAboutHUDandPitchComms\\csv\\NewHeightMetrics(ZoneDim).csv"
dim_df = pd.read_csv(dim_path)

#hand_path = "C:\\Users\\nitro\\WhoCaresAboutHUDandPitchComms\\csv\\Handedness.csv"
#hand_df = pd.read_csv(hand_path)

# Global variables (GUI will set these)
player = None
player_id = None
player_height = None
zone_area = None
zone_top = None
zone_bottom = None
zone_width = 17
handedness = None
zone_height = None


def load_player(batter_name):
	"""
	GUI calls this to load all strike zone data for the current batter.
	"""
	global player, player_id, player_height, zone_area
	global zone_top, zone_bottom, handedness, zone_height
	player = batter_name

	# Lookup values
	player_id = int(dim_df.loc[dim_df['Player Name (ASCII)'] == player, 'SC_ID'].item())
	player_height = int(dim_df.loc[dim_df['Player Name (ASCII)'] == player, 'Height ((ft*12) + in)'].item())
	zone_area = dim_df.loc[dim_df['Player Name (ASCII)'] == player, 'Area of Zone (17 * (Top - Bottom))'].item()
	zone_top = dim_df.loc[dim_df['Player Name (ASCII)'] == player, 'Top of Zone (Height * 0.535)'].item()
	zone_bottom = dim_df.loc[dim_df['Player Name (ASCII)'] == player, 'Bottom of Zone (Height * 0.27)'].item()

	ascii_conversion = dim_df.loc[dim_df['Player Name (ASCII)'] == player, 'Player Name'].item()
	#matches = hand_df.loc[hand_df['Name'] == ascii_conversion, 'Handedness']
	'''
	if len(matches) == 0:
		raise ValueError(f"No handedness found for player: {ascii_conversion}")

	if len(matches) > 1:
		raise ValueError(f"Multiple handedness entries found for player: {ascii_conversion}")

	handedness = matches.iloc[0]
	'''
	zone_height = zone_top - zone_bottom

	print(f"Loaded StrikeZoneLogic for {player}")
	print(f"ID: {player_id}")
	print(f"Height: {player_height}")
	print(f"Zone Top: {zone_top}")
	print(f"Zone Bottom: {zone_bottom}")
	#print(f"Handedness: {handedness}")

# Touch Details
def normalize_touch(touch_x, touch_y, screen_width, screen_height, zone_top, zone_bottom):
	# Convert screen pixels to inches
	inch_x = (touch_x / screen_width) * zone_width - (zone_width / 2)
	inch_y = zone_top - ((touch_y / screen_height) * zone_height)

	# Normalize to -1 to +1
	norm_x = inch_x / (zone_width / 2)
	norm_y = inch_y / (zone_height / 2)

	return norm_x, norm_y
