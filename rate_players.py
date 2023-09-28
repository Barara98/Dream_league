from data_utility import DataUtility
from player_data_analyzer import PlayersDataAnalyzer
from playerDB import PlayerDataDB
import sys
import numpy as np


def rate_players(
    player_data,
    events_list,
    event_weights,
    games_played_weight=0.2,
    points_weight=1,
    price_weight=0.3,
):
    print("Starting calculate")
    # Calculate performance scores for each player
    player_scores = {}
    overall_scores = []

    for player in player_data:
        games_played = player.get("game_played", 0)
        points = player.get("points", 0)
        player_price = player.get("Price", 0)

        # Calculate performance score only if the player has played at least one game
        if games_played > 0:
            performance_score = sum(
                player[event] * event_weights.get(event, 0) for event in events_list
            )

            # Calculate an adjusted performance score that includes points and price
            adjusted_performance_score = (
                performance_score
                + (games_played * games_played_weight)
                + (points * points_weight)
                + (player_price * price_weight)
            )

            overall_scores.append(adjusted_performance_score)

            # Assign a star rating based on overall score
            player_scores[player["name"]] = {
                "Performance Score": performance_score,
                "Points Score": points,
                "Overall Score": adjusted_performance_score,
            }
        else:
            # Player didn't play any games, assign a 1-star rating
            player_scores[player["name"]] = {
                "Performance Score": 0,
                "Points Score": points,
                "Overall Score": 0,
            }

    # Calculate percentiles and determine ratings
    percentiles = np.percentile(overall_scores, [95, 85, 55, 25])
    print("Percentiles:", percentiles)

    for player_name, player_data in player_scores.items():
        overall_score = player_data["Overall Score"]

        if overall_score >= percentiles[0]:
            rating = 5
        elif overall_score >= percentiles[1]:
            rating = 4
        elif overall_score >= percentiles[2]:
            rating = 3
        elif overall_score >= percentiles[3]:
            rating = 2
        else:
            rating = 1

        player_scores[player_name]["Rating"] = rating

    print("Finished")
    return player_scores


def print_players_by_rating_to_file(rated_players, file_path):
    # Organize players by rating
    players_by_rating = {}
    for player_name, player_data in rated_players.items():
        rating = player_data["Rating"]
        if rating not in players_by_rating:
            players_by_rating[rating] = []
        players_by_rating[rating].append((player_name, player_data))

    # Open the specified file for writing
    with open(file_path, "w") as file:
        # Redirect sys.stdout to the file
        sys.stdout = file

        # Print players by rating and count for each rating
        for rating in sorted(players_by_rating.keys(), reverse=True):
            print(
                f"\nRating {rating} (Total Players: {len(players_by_rating[rating])}):"
            )
            for player_name, player_data in players_by_rating[rating]:
                overall_score = player_data["Overall Score"]
                points_score = player_data["Points Score"]

                # Format the overall score with one digit after the decimal point
                formatted_overall_score = f"{overall_score:.1f}"

                print(
                    f"Player: {player_name}, Rating: {rating}, Overall Score: {formatted_overall_score}, Points Score: {points_score}"
                )

    # Reset sys.stdout to its default value after printing
    sys.stdout = sys.__stdout__


db = PlayerDataDB("player_data.db")
json_file_path = "data/all_players_data.json"
analyzer = PlayersDataAnalyzer(json_file_path)
data_utility = DataUtility()


all_players = db.get_all_players_with_total_events(data_utility.events_list)

rated_players = rate_players(
    all_players, data_utility.events_list, data_utility.event_weights
)
output_file_path = "player_ratings.txt"
print_players_by_rating_to_file(rated_players, output_file_path)

db.update_player_stars(rated_players)