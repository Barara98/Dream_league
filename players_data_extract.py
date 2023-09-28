import json
import os
from bs4 import BeautifulSoup
from data_utility import DataUtility

data_utility = DataUtility()


def update_json_structure(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as file:
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


def fixture_data(html_file_path):

    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")

    data = []

    # Find all <tr> elements starting from the third one
    trs = soup.find_all("tr")[1:]

    for tr in trs:
        tds = tr.find_all("td")
        if len(tds) == 3:
            event_name = tds[0].text.strip()  # Event name
            quantity = int(tds[1].text.strip())  # Quantity
            # Points (assuming they are integers)
            points = int(tds[2].text.strip())

            # Translate the event name from Hebrew to English
            event_name = data_utility.stats_hebrew_english.get(event_name, event_name)

            # Append the data as a dictionary
            data.append({"Event": event_name, "Quantity": quantity, "Points": points})

    # Convert the data list to a dictionary with event names in English
    table_dict = {
        item["Event"]: {"Quantity": item["Quantity"], "Points": item["Points"]}
        for item in data
    }

    return table_dict


def extract_player_profile(html_file_path):
    # Parse the HTML content
    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract the player information
    player_name = soup.find("p", class_="player-name").get_text(strip=True)
    player_position = soup.find("p", class_="player-position").get_text(strip=True)
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

    # Extract the player points
    player_points = int(soup.find("div", class_="points").get_text(strip=True))

    # Build the object
    player_object = {
        "name": player_name,
        "position": player_position,
        "team": player_team,
        "price": player_price,
        "points": player_points,
        "stars": 0, 
        "injury": injury,
        "fixtures": {}
    }

    return player_object


def process_player_folders(root_directory):
    all_players_data = {}
    # Iterate over player(number) folders
    for player_folder in os.listdir(root_directory):
        player_folder_path = os.path.join(root_directory, player_folder)

        # Check if it's a directory
        if os.path.isdir(player_folder_path):
            print(f"Processing player folder: {player_folder_path}")

            # Look for profile.html
            profile_html_path = os.path.join(player_folder_path, "profile.html")

            # Check if profile.html exists
            if os.path.exists(profile_html_path):
                print(f"Found profile.html in {player_folder_path}")
                player_data = extract_player_profile(profile_html_path)

            # Look for the fixture folder
            fixture_folder_path = os.path.join(player_folder_path, "fixture")

            # Check if fixture folder exists
            if os.path.exists(fixture_folder_path):
                # Iterate over fixture(number).html files
                for fixture_file in os.listdir(fixture_folder_path):
                    fixture_file_path = os.path.join(fixture_folder_path, fixture_file)
                    fixture_name = os.path.splitext(fixture_file)[0]
                    fixture = fixture_data(fixture_file_path)
                    player_data["fixtures"][fixture_name] = fixture
                    
            if player_data["position"] not in all_players_data:
                all_players_data[player_data["position"]] = []
            all_players_data[player_data["position"]].append(player_data)

    file_path = "all_players_data_fixture4.json"

    # Write the player data to the JSON file
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(all_players_data, json_file, ensure_ascii=False, indent=4)

    update_json_structure(file_path, file_path)

    print(f"Player data saved to {file_path}")
    total_players = sum(len(players) for players in all_players_data.values())

    print(f"Total number of players: {total_players}")


# Define the root directory
root_directory = "players_fixture4/"

# Call the function to process player folders
process_player_folders(root_directory)
