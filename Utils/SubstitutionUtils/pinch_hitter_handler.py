import statsapi as st

def fetch_updated_lineup(game_id, side):
    box = st.boxscore_data(game_id)
    player_info = box["playerInfo"]

    if side == "away":
        batters = box["awayBatters"]
    else:
        batters = box["homeBatters"]

    lineup = []
    for p in batters:
        order = p.get("battingOrder", "")
        if order == "":
            continue

        pid = p["personId"]
        key = f"ID{pid}"
        name = player_info[key]["fullName"]

        lineup.append({
            "order": int(order),
            "player_id": pid,
            "name": name,
            "position": p.get("position", "N/A")
        })

    lineup.sort(key=lambda x: x["order"])
    return lineup
