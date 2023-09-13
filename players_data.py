import os
import re
import json
from bs4 import BeautifulSoup

# Define a function to extract player data from an HTML file


def extract_player_data(file_path, position):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

        # Find all the rows in the table
        player_rows = soup.find_all('tr')

        # Initialize a list to store player data for this position
        players_data = []

        # Iterate through each row and extract player data
        for row in player_rows:
            cells = row.find_all('td')
            if len(cells) >= 5:
                player_name = cells[1].get_text()
                team = cells[2].get_text()
                price_text = cells[3].get_text()
                points_text = cells[4].get_text()

                # Extract numeric values from price and points using regular expressions
                price_match = re.match(r'(\d+)', price_text)
                points_match = re.match(r'(-?\d+)', points_text)  # Allow negative points

                if price_match and points_match:
                    price = int(price_match.group(1))
                    points = int(points_match.group(1))
                else:
                    price = 0
                    points = 0

                player_data = {
                    'name': player_name,
                    'position': position,
                    'team': team,
                    'price': price,
                    'points': points
                }
                players_data.append(player_data)

        return players_data

def extract_unique_team_names(input_file_path, output_file_path):
    # Read the HTML content from the input file
    with open(input_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all the <tr> elements in the table
    tr_elements = soup.find_all('tr')

    # Initialize a set to store unique team names
    unique_team_names = set()

    # Extract the team names from the 3rd <td> element in each <tr>
    for tr in tr_elements:
        td_elements = tr.find_all('td')
        if len(td_elements) >= 3:
            team_name = td_elements[2].get_text()
            unique_team_names.add(team_name)

    # Write the unique team names to the output file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for team_name in unique_team_names:
            output_file.write(f'{team_name}\n')

def read_unique_team_names_from_file(file_path):
    unique_team_names = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            team_name = line.strip()  # Remove leading/trailing whitespace and newline character
            unique_team_names.append(team_name)
    return unique_team_names


# Define a dictionary to store all player data
all_players_data = {}

# Define the folder containing the HTML files
data_folder = 'data/'

# Iterate over the HTML files in the folder
for filename in os.listdir(data_folder):
    if filename.endswith('.html'):
        file_path = os.path.join(data_folder, filename)
        # Extract the position from the filename
        position = filename.split('.')[0]
        players_data = extract_player_data(file_path, position)
        all_players_data[position] = players_data

# Write the player data to a JSON file
with open('players_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(all_players_data, json_file, ensure_ascii=False, indent=2)

print("JSON file 'players_data.json' has been created.")

input_file_path = 'data/GK.html'
output_file_path = 'team_names.txt'
extract_unique_team_names(input_file_path, output_file_path)

# Example usage:
file_path = 'team_names.txt'
team_names_list = read_unique_team_names_from_file(file_path)

print(team_names_list)
