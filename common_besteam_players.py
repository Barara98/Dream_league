import json
from collections import Counter
import random

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

# Usage example:
# Enter best team file:
json_file_path = 'best_teams/fixture14.json'  

player_count_list = count_players_in_teams(json_file_path)

# Print the list of player names and their counts
for player_name, count in player_count_list:
    print(f"{player_name}: {count}")

display_random_team()
