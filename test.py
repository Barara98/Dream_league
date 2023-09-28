import pulp
from player_data_analyzer import PlayersDataAnalyzer
from playerDB import PlayerDataDB

db = PlayerDataDB("player_data.db")


def find_best_sequence_of_squads(analyzer, fixture_names):
    num_fixtures = len(fixture_names)
    max_substitutions = 3

    # Initialize a list to store the results for each fixture
    fixture_results = []

    # Initialize a variable to count substitutions
    num_substitutions = 0

    # Initialize a list to keep track of the selected players for the entire sequence
    selected_players_sequence = []

    # Initialize a variable to track the total points over all fixtures
    total_points_over_sequence = 0

    for i in range(num_fixtures):
        current_fixture_name = fixture_names[i]
        players_data = db.get_players_by_fixture(current_fixture_name)

        # Create a linear programming problem
        prob = pulp.LpProblem("FantasyFootball", pulp.LpMaximize)

        # Define variables: binary variables for player selection
        player_vars = {}
        for player_data in players_data:
            player_vars[player_data["name"]] = pulp.LpVariable(
                player_data["name"], cat=pulp.LpBinary
            )

        # Objective function: maximize total points
        prob += pulp.lpSum(
            player_data["points"] * player_vars[player_data["name"]]
            for player_data in players_data
        )

        # Budget constraint
        prob += (
            pulp.lpSum(
                player_data["price"] * player_vars[player_data["name"]]
                for player_data in players_data
            )
            <= analyzer.budget
        )

        # Position constraints
        for position, (min_count, max_count) in analyzer.position_constraints.items():
            prob += (
                pulp.lpSum(
                    player_vars[player_data["name"]]
                    for player_data in players_data
                    if player_data["position"] == position
                )
                >= min_count
            )
            prob += (
                pulp.lpSum(
                    player_vars[player_data["name"]]
                    for player_data in players_data
                    if player_data["position"] == position
                )
                <= max_count
            )

        # Max 2 players from the same team constraint
        teams = set(player_data["team"] for player_data in players_data)
        for team in teams:
            prob += (
                pulp.lpSum(
                    player_vars[player_data["name"]]
                    for player_data in players_data
                    if player_data["team"] == team
                )
                <= analyzer.max_players_per_team
            )

        # Exactly 11 players constraint
        prob += pulp.lpSum(player_vars.values()) == 11

        # If not the first fixture, add the substitution constraint
        if i > 0:
            substitutions = pulp.lpSum(
                player_vars[player_data["name"]]
                for player_data in players_data
                if player_data["name"] not in selected_players_sequence
            )
            prob += substitutions <= max_substitutions

        # Solve the LP problem
        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        # Extract the selected players as objects
        best_team = [
            player_data
            for player_data in players_data
            if pulp.value(player_vars[player_data["name"]]) == 1
        ]

        # Calculate total points and total cost
        total_points = pulp.value(prob.objective)
        total_cost = sum(player_data["price"] for player_data in best_team)

        # Update the number of substitutions and the selected players sequence
        if i > 0:
            num_substitutions += pulp.value(substitutions)

        # Find substitutions in and out
        substitutions_in = [
            player_data["name"]
            for player_data in players_data
            if player_data["name"] not in selected_players_sequence
            and pulp.value(player_vars[player_data["name"]]) == 1
        ]
        substitutions_out = [
            player_name
            for player_name in selected_players_sequence
            if player_name not in [player["name"] for player in best_team]
        ]

        selected_players_sequence = [player["name"] for player in best_team]

        # Update the total points over the entire sequence
        total_points_over_sequence += total_points

        # Append the results for this fixture to the list
        fixture_results.append(
            {
                "fixture_name": current_fixture_name,
                "best_team": best_team,
                "total_points": total_points,
                "total_cost": total_cost,
                "substitutions_in": substitutions_in,
                "substitutions_out": substitutions_out,
                "total_points_over_sequence": total_points_over_sequence,
            }
        )

    return fixture_results


def get_user_team():
    players_name = [
        "תומר צרפתי",
        "מיגל ויטור",
        "שגיב יחזקאל",
        "איבן מאסון",
        "איברהים ג`באר",
        "תומר יוספי",
        "מתן חוזז",
        "מאוויס צ`יבוטה",
        "סטניסלב בילנקי",
        "ערן זהבי",
        "עידן טוקלומטי",
    ]
    found_players = []
    player_list = db.get_players_by_fixture("fixture1")
    for player in player_list:
        if player['name'] in players_name:
            found_players.append(player)

    return found_players



players = get_user_team()
print(len(players))


# # Example usage
# analyzer = PlayersDataAnalyzer("data/all_players_data.json")
# fixture_names = ["fixture2", "fixture3"]  # Replace with your fixture names
# results = find_best_sequence_of_squads(analyzer, fixture_names)
# print(results)

# for result in results:
#     print(f"Fixture: {result['fixture_name']}")
#     print(f"Total Points: {result['total_points']}")
#     print(f"Total Cost: {result['total_cost']}")
#     print("Selected Team:")
#     for player in result["best_team"]:
#         print(
#             f"Name: {player['name']}, Position: {player['position']}, Team: {player['team']}, Price: {player['price']}, Points: {player['points']}"
#         )
#     print("Substitutions In:")
#     for player_name in result["substitutions_in"]:
#         print(f"Name: {player_name}")
#     print("Substitutions Out:")
#     for player_name in result["substitutions_out"]:
#         print(f"Name: {player_name}")
#     print("=" * 30)
# print(f"Total Points: {result['total_points_over_sequence']}")
