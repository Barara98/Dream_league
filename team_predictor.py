import json
import sys
from playerDB import PlayerDataDB
from data_utility import DataUtility
from player_data_analyzer import PlayersDataAnalyzer

# Create an instance of PlayersDataAnalyzer
json_file_path = "data/all_players_data.json"
analyzer = PlayersDataAnalyzer(json_file_path)

data_utility = DataUtility()
db = PlayerDataDB("player_data.db")


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


def predict_best_team(fixture_name, players_data):
    file_name = f"best_teams/{fixture_name}.json"
    existing_unique_teams = load_existing_teams(file_name)

    team, _, _, _ = analyzer.find_best_team_stars(players_data)

    if is_team_unique(existing_unique_teams, team):
        existing_unique_teams.append(team)
        save_teams_to_json(file_name, existing_unique_teams)
    else:
        print("Team is already exists")


def update_team_attributes(teams, fixtures, fixture_name):
    fixture = fixtures.get(fixture_name)
    if fixture:
        for home_team, away_team in fixture:
            # print(f"Home Team: {home_team}")
            # print(f"Away Team: {away_team}")

            # Find the dictionaries corresponding to home_team and away_team
            home_team_attributes = next(
                (item for item in teams if item["name"] == home_team), None
            )
            away_team_attributes = next(
                (item for item in teams if item["name"] == away_team), None
            )

            # Check if both home_team and away_team were found
            if home_team_attributes and away_team_attributes:
                # Update home team's attack and defense
                home_team_attributes["attack"] += (
                    home_team_attributes["attack"]
                    - away_team_attributes["defend"]
                    + 1
                    + home_team_attributes["overall"] // 2
                )
                home_team_attributes["defend"] += (
                    home_team_attributes["defend"]
                    - away_team_attributes["attack"]
                    + 1
                    + home_team_attributes["overall"] // 2
                )

                # Update away team's attack and defense
                away_team_attributes["attack"] += (
                    away_team_attributes["attack"]
                    - home_team_attributes["defend"]
                    - 1
                    + away_team_attributes["overall"] // 2
                )
                away_team_attributes["defend"] += (
                    away_team_attributes["defend"]
                    - home_team_attributes["attack"]
                    - 1
                    + away_team_attributes["overall"] // 2
                )

    return teams


def get_top_teams(teams_dict):
    # Sort teams by attack and defend values
    sorted_teams_attack = sorted(teams_dict, key=lambda x: x["attack"], reverse=True)
    sorted_teams_defend = sorted(teams_dict, key=lambda x: x["defend"], reverse=True)

    # Get the top 6 teams for attack and defend
    top_attack_teams = [team["name"] for team in sorted_teams_attack[:7]]
    top_defend_teams = [team["name"] for team in sorted_teams_defend[:7]]

    return top_attack_teams, top_defend_teams


def combine_players_for_top_teams(teams_dict, db):
    top_attack_teams, top_defend_teams = get_top_teams(teams_dict)
    all_players = []

    for team_name in top_attack_teams:
        attackers = db.get_attackers_by_team_name(team_name)
        all_players.extend(attackers)

    for team_name in top_defend_teams:
        defenders = db.get_defenders_by_team_name(team_name)
        all_players.extend(defenders)

    return all_players


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python team_predictor.py fixture_name")
        sys.exit(1)

    fixture_name = sys.argv[1]
    teams = update_team_attributes(
        db.get_all_teams(), data_utility.fixtures_table, fixture_name
    )
    all_top_players = combine_players_for_top_teams(teams, db)

    predict_best_team(fixture_name, all_top_players)

#     for i in {1..1000}; do
#     echo "Iteration: $i"
#     python -u "/Users/shlomi/DreamLeague/team_predictor.py" "fixture6"
# done
