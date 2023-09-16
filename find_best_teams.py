import sys
from player_data_analyzer import PlayersDataAnalyzer

# Create an instance of PlayersDataAnalyzer
json_file_path = 'all_players_data.json'
analyzer = PlayersDataAnalyzer(json_file_path)

def update_unique_teams(fixture_name):
    file_name = f'best_teams/{fixture_name}.txt'
    
    try:
        # Try to open the file for reading
        with open(file_name, 'r') as file:
            unique_teams = [line.strip() for line in file]
    except FileNotFoundError:
        # If the file doesn't exist, initialize with an empty list
        unique_teams = [] 

    if fixture_name == 'all':
        team, _, _ = analyzer.find_best_team_lp()
    else:
        team, _, _ = analyzer.find_best_team_lp_by_fixture(fixture_name)
    # Create a comma-separated string of player names
    team_names = ', '.join(player['name'] for player in team)

    if team_names in unique_teams:
        print('Team already in the dictionary')
    else:
        unique_teams.append(team_names)

    # Update the text file with unique teams
    with open(file_name, 'w') as file:
        file.write('\n'.join(unique_teams))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script_name.py fixture_name")
        sys.exit(1)

    fixture_name = sys.argv[1]
    update_unique_teams(fixture_name)

#     for i in {1..1000}; do
#     echo "Iteration: $i"
#     python -u "/Users/shlomi/DreamLeague/find_best_teams.py" "fixture1"
# done
