import json
import sys
from data_utility import DataUtility
from player_data_analyzer import PlayersDataAnalyzer


# Create an instance of PlayersDataAnalyzer
json_file_path = "cl/cl_all_players_data.json"
analyzer = PlayersDataAnalyzer(json_file_path)
data_utility = DataUtility()


total_player = analyzer.get_total_players()
print(len(total_player))

fixture1 = [
    ["Galatasaray A.Ş.", "F.C. Copenhagen"],
    ["Real Madrid CF", "1. FC Union Berlin"],
    ["FC Bayern München", "Manchester United"],
    ["Sevilla FC", "RC Lens"],
    ["Arsenal FC", "PSV Eindhoven"],
    ["SC Braga", "SSC Napoli"],
    ["Real Sociedad", "FC Internazionale Milano"],
    ["SL Benfica", "FC Salzburg"],
]


def predict_ratings(team_objects, fixture_array):
    results = []

    for home_team, away_team in fixture_array:
        home_team_data = next(
            (team for team in team_objects if team["Team"] == home_team), None
        )
        away_team_data = next(
            (team for team in team_objects if team["Team"] == away_team), None
        )

        if home_team_data is not None and away_team_data is not None:
            home_scoring_rating = (
                int(home_team_data["Attack"])
                + int(home_team_data["Set Pieces"])
                + int(home_team_data["Squad Strength"])
                + int(home_team_data["Home"])
            ) - (
                int(away_team_data["Defense"])
                + int(away_team_data["Discipline"])
                + int(away_team_data["Squad Strength"])
                + int(away_team_data["Away"])
            )

            away_scoring_rating = (
                int(away_team_data["Attack"])
                + int(away_team_data["Set Pieces"])
                + int(away_team_data["Squad Strength"])
                + int(away_team_data["Home"])
            ) - (
                int(home_team_data["Defense"])
                + int(home_team_data["Discipline"])
                + int(home_team_data["Squad Strength"])
                + int(home_team_data["Home"])
            )

            home_defending_rating = (
                int(home_team_data["Defense"])
                + int(home_team_data["Discipline"])
                + int(home_team_data["Squad Strength"])
                + int(home_team_data["Home"])
            ) - (
                int(away_team_data["Attack"])
                + int(away_team_data["Set Pieces"])
                + int(away_team_data["Squad Strength"])
                + int(away_team_data["Home"])
            )

            away_defending_rating = (
                int(away_team_data["Defense"])
                + int(away_team_data["Discipline"])
                + int(away_team_data["Squad Strength"])
                + int(away_team_data["Home"])
            ) - (
                int(home_team_data["Attack"])
                + int(home_team_data["Set Pieces"])
                + int(home_team_data["Squad Strength"])
                + int(home_team_data["Home"])
            )

            results.append(
                {
                    "Team": home_team,
                    "Scoring Rating": home_scoring_rating,
                    "Defend Rating": home_defending_rating,
                }
            )

            results.append(
                {
                    "Team": away_team,
                    "Scoring Rating": away_scoring_rating,
                    "Defend Rating": away_defending_rating,
                }
            )
        else:
            print(
                f"Team data not found for one or more teams: {home_team}, {away_team}"
            )
    results.sort(key=lambda x: x["Scoring Rating"], reverse=True)
    top_6_scoring = results[:6]
    results.sort(key=lambda x: x["Defend Rating"], reverse=True)
    top_6_defending = results[:6]

    return top_6_scoring, top_6_defending


def get_best_players(teams, position=True):
    best_players = []
    for team in teams:
        team_name = data_utility.cl_teams_translator2.get(team["Team"])
        if position:
            team_players = analyzer.get_attackers_by_team(team_name)
        else:
            team_players = analyzer.get_defenders_by_team(team_name)
        best_players.extend(team_players)
    return best_players


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


def find_unique_teams(fixture_name, players_data=None):
    file_name = f"best_teams/{fixture_name}.json"
    existing_unique_teams = load_existing_teams(file_name)

    if fixture_name == "all":
        team, _, _ = analyzer.find_best_team_lp()
    elif fixture_name == "cl":
        team, _, _, _ = analyzer.find_best_team_stars(players_data)
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
        # Load the JSON data from the file
    with open("cl/cl_ratings.json", "r") as file:
        team_objects = json.load(file)

    # fixture_array = [("Arsenal FC", "Club Atlético de Madrid")]
    top_attack, top_defend = predict_ratings(team_objects, fixture1)
    best_players = get_best_players(top_attack)
    best_players.extend(get_best_players(top_defend, False))
    print(len(best_players))

    best_team, best_points, total_cost, total_stars = analyzer.find_best_team_stars(
        best_players
    )

    print("Best Team:")
    for player in best_team:
        print(
            f"{player['name']} ({player['position']}) - {player['team']} - Price: {player['price']} - Points: {player['points']} - Stars: {player['stars']}"
        )

    # Calculate the totals
    total_points = sum(player["points"] for player in best_team)
    total_cost = sum(player["price"] for player in best_team)
    total_stars = sum(player["stars"] for player in best_team)

    print(f"Total Points: {total_points}")
    print(f"Total Cost: {total_cost}")
    print(f"Total Stars: {total_stars}")

    fixture_name = sys.argv[1]
    find_unique_teams(fixture_name, best_team)
