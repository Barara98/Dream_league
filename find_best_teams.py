from collections import Counter
import random
import sys
import json
from player_data_analyzer import PlayersDataAnalyzer

# Create an instance of PlayersDataAnalyzer
json_file_path = "all_players_data.json"
analyzer = PlayersDataAnalyzer(json_file_path)


def load_existing_teams(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_teams_to_json(file_name, teams):
    with open(file_name, "w") as file:
        json.dump(teams, file, ensure_ascii=False, indent=4)

def is_team_unique(teams, new_team):
    # Check if the new team is unique by comparing player names
    for team in teams:
        if set(player["name"] for player in team) == set(
            player["name"] for player in new_team
        ):
            return False
    return True

def find_unique_teams(fixture_name):
    file_name = f"best_teams/{fixture_name}.json"
    existing_unique_teams = load_existing_teams(file_name)

    if fixture_name == "all":
        team, _, _ = analyzer.find_best_team_lp()
    else:
        team, _, _ = analyzer.find_best_team_lp_by_fixture(fixture_name)

    if is_team_unique(existing_unique_teams, team):
        existing_unique_teams.append(team)
        save_teams_to_json(file_name, existing_unique_teams)
    else:
        print("Team is already exists")

def count_players_in_teams(json_file_path):
    # Load the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Flatten all player names into a single list
    all_player_names = [player['name'] for player_array in data for player in player_array]

    # Count the occurrences of each player name
    player_counts = Counter(all_player_names)

    # Convert the Counter object to a list of (player_name, count) tuples
    player_count_list = list(player_counts.items())

    # Sort the list by count in descending order
    sorted_player_count_list = sorted(player_count_list, key=lambda x: x[1], reverse=True)

    return sorted_player_count_list

def display_random_team():
        # Load the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Calculate the length of the data list
    data_length = len(data)

    # Generate a random index within the range [0, data_length - 1]
    random_index = random.randint(0, data_length - 1)

    # Access the element at the randomly selected index
    best_team = data[random_index]

    print("Best Team:")
    for player in best_team:
        print(f"{player['name']} ({player['position']}) - {player['team']} - Price: {player['price']} - Points: {player['points']}")
    print(f"Total Points: {sum(player['points'] for player in best_team)}")
    print(f"Total Cost: {sum(player['price'] for player in best_team)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        json_file_path = 'best_teams/all.json'
        player_count_list = count_players_in_teams(json_file_path)
        # Print the list of player names and their counts
        for player_name, count in player_count_list:
            print(f"{player_name}: {count}")
        display_random_team()
    else:
        fixture_name = sys.argv[1]
        find_unique_teams(fixture_name)


#     for i in {1..1000}; do
#     echo "Iteration: $i"
#     python -u "/Users/shlomi/DreamLeague/find_best_teams.py" "all"
# done
