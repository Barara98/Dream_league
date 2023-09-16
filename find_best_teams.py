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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py fixture_name")
        sys.exit(1)

    fixture_name = sys.argv[1]
    find_unique_teams(fixture_name)


#     for i in {1..1000}; do
#     echo "Iteration: $i"
#     python -u "/Users/shlomi/DreamLeague/find_best_teams.py" "fixture2"
#     python -u "/Users/shlomi/DreamLeague/find_best_teams.py" "all"
# done
