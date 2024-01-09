import os
import json
from bs4 import BeautifulSoup
from data_utility import DataUtility
from tkinter import filedialog

data_utility = DataUtility()

OUTPUT_FILE_NAME = "data/all_players_data_fixture6.json"
ROOT_DIRECTORY = "data/players/players_fixture6/"


def extract_player_profile(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    player_name = soup.find("p", class_="player-name").get_text(strip=True)
    player_position = soup.find(
        "p", class_="player-position").get_text(strip=True)
    player_team = soup.find("p", class_="player-team").get_text(strip=True)
    player_price = int(
        soup.find("p", class_="player-value")
        .get_text(strip=True)
        .replace("מחיר ", "")
        .replace("M", "")
    )
    injury_icon = soup.find("img", alt="פצוע")
    injury = True if injury_icon is not None else False

    player_position = data_utility.position_mapping.get(
        player_position, player_position
    )

    player_points = int(soup.find("div", class_="points").get_text(strip=True))

    player_object = {
        "name": player_name,
        "position": player_position,
        "team": player_team,
        "price": player_price,
        "points": player_points,
        "stars": 0,
        "injury": injury,
        "fixtures": {},
    }

    return player_object


def fixture_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    data = []

    trs = soup.find_all("tr")[1:]

    for tr in trs:
        tds = tr.find_all("td")
        if len(tds) == 3:
            event_name = tds[0].text.strip()
            quantity = int(tds[1].text.strip())
            points = int(tds[2].text.strip())

            event_name = data_utility.stats_hebrew_english.get(
                event_name, event_name)

            data.append(
                {"Event": event_name, "Quantity": quantity, "Points": points})

    table_dict = {
        item["Event"]: {"Quantity": item["Quantity"], "Points": item["Points"]}
        for item in data
    }

    return table_dict


def process_player_folder(player_folder_path):
    profile_html_path = os.path.join(player_folder_path, "profile.html")
    fixture_folder_path = os.path.join(player_folder_path, "fixture")

    player_data = extract_player_profile(
        open(profile_html_path, "r", encoding="utf-8").read())

    if os.path.exists(fixture_folder_path):
        for fixture_file in os.listdir(fixture_folder_path):
            fixture_file_path = os.path.join(fixture_folder_path, fixture_file)
            fixture_name = os.path.splitext(fixture_file)[0]
            fixture = fixture_data(
                open(fixture_file_path, "r", encoding="utf-8").read())
            player_data["fixtures"][fixture_name] = fixture

    return player_data


def update_json_structure(output_file):
    with open(output_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    for position_data in data.values():
        for player in position_data:
            for fixture_data in player["fixtures"].values():
                total_points = 0
                events = {}

                for event_key, event_values in fixture_data.items():
                    if event_key != "Points":
                        events[event_key] = event_values
                        total_points += event_values["Points"]

                fixture_data.clear()
                fixture_data["Points"] = total_points
                fixture_data["events"] = events

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def process_player_folders(root_directory):
    all_players_data = {}

    for player_folder in os.listdir(root_directory):
        player_folder_path = os.path.join(root_directory, player_folder)

        if os.path.isdir(player_folder_path):
            print(f"Processing player folder: {player_folder_path}")
            player_data = process_player_folder(player_folder_path)

            if player_data["position"] not in all_players_data:
                all_players_data[player_data["position"]] = []
            all_players_data[player_data["position"]].append(player_data)

    with open(OUTPUT_FILE_NAME, "w", encoding="utf-8") as json_file:
        json.dump(all_players_data, json_file, ensure_ascii=False, indent=4)

    update_json_structure(OUTPUT_FILE_NAME)

    print(f"Player data saved to {OUTPUT_FILE_NAME}")
    total_players = sum(len(players) for players in all_players_data.values())
    print(f"Total number of players: {total_players}")


def main():
    root_directory = filedialog.askdirectory(title="Select Root Directory for Player Data")
    if root_directory:
        process_player_folders(root_directory)
    else:
        print("Please select a root directory for player data.")


if __name__ == "__main__":
    main()
