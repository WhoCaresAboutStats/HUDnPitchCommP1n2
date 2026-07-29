#VENV
import json
def json_template(pitch_num_total, pitch_ab, pitch_type, x, y, batter, id, zone_b, zone_t, handedness):
	if batter is None:
		raise ValueError("JSONWrite received batter=None — GUI did not load player correctly.")

	if " " in batter:
		first, last = batter.split(" ", 1)
	else:
		first = batter
		last = ""

	new_json_out = {
		"pitch_count_details": {
			"pitch_num_total": pitch_num_total,
			"pitch_num_at_bat": pitch_ab
		},
		"pitch_details": {
			"pitch_type": pitch_type,
			"location_normalized_x": x,
			"location_normalized_y": y
		},
		"strike_zone_details": {
			"player_name": batter,
			"player_id": id,
			"zone_bottom": zone_b,
			"zone_top": zone_t,
			"handedness": "LOOK UP"
		}
	}

	filename = f"jsons/total_{pitch_num_total:03d}_ab_{pitch_ab:02d}_{first}{last}.json"

	with open(filename, 'w') as file:
		json.dump(new_json_out, file, indent=4, sort_keys=True)

	print("Sending Json Out Now")
	return filename, new_json_out