import pulp

from playerDB import PlayerDataDB


class PlayersDataAnalyzer:
    def __init__(self, db_file):
        self.db = PlayerDataDB(db_file)
        self.budget = 108  # Define the budget attribute
        self.position_constraints = {
            "GK": (1, 1),  # Exactly 1 goalkeeper
            "CB": (3, 5),  # 3 to 5 center-backs
            "MD": (3, 5),  # 3 to 5 midfielders
            "FW": (1, 3),  # 1 to 3 forwards
        }
        self.max_players_per_team = 2

    def display_team(self, team, points, cost):
        for player in team:
            print(
                f"{player['name']} ({player['position']}) - {player['team']} - Price: {player['price']} - Points: {player['points']}")
        print(f"Total Points: {points}")
        print(f"Total Cost: {cost}")

    def find_best_team(self, fixture="All", key="points"):
        if fixture == "All":
            player_list = self.db.get_all_players()
        else:
            player_list = self.db.get_players_by_fixture(fixture)
        # Create a linear programming problem
        prob = pulp.LpProblem("FantasyFootball", pulp.LpMaximize)

        # Define variables: binary variables for player selection
        player_vars = {
            player["name"]: pulp.LpVariable(player["name"], cat=pulp.LpBinary)
            for player in player_list
        }

        # Objective function: maximize total points
        prob += pulp.lpSum(
            player[key] * player_vars[player["name"]] for player in player_list
        )

        # Budget constraint
        prob += (
            pulp.lpSum(
                player["price"] * player_vars[player["name"]] for player in player_list
            )
            <= self.budget
        )

        # Position constraints
        for position, (min_count, max_count) in self.position_constraints.items():
            prob += (
                pulp.lpSum(
                    player_vars[player["name"]]
                    for player in player_list
                    if player["position"] == position
                )
                >= min_count
            )
            prob += (
                pulp.lpSum(
                    player_vars[player["name"]]
                    for player in player_list
                    if player["position"] == position
                )
                <= max_count
            )

        # Max 2 players from the same team constraint
        for team in set(player["team"] for player in player_list):
            prob += (
                pulp.lpSum(
                    player_vars[player["name"]]
                    for player in player_list
                    if player["team"] == team
                )
                <= self.max_players_per_team
            )

        # Exactly 11 players constraint
        prob += pulp.lpSum(player_vars.values()) == 11

        # Solve the LP problem
        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        # Extract the selected players as objects
        best_team = [
            player
            for player in player_list
            if pulp.value(player_vars[player["name"]]) == 1
        ]

        # Calculate total points
        total_points = pulp.value(prob.objective)
        total_cost = sum(player["price"] for player in best_team)

        return best_team, total_points, total_cost


# Create an instance of PlayersDataAnalyzer
# db_path = "player_data.db"  # Replace with your JSON file path
# analyzer = PlayersDataAnalyzer(db_path)

# # # Use the find_best_team function to find the best team.
# best_team, best_points, total_cost = analyzer.find_best_team()
# print("Best Team:")
# analyzer.display_team(best_team, best_points, total_cost)


# fixture = 'fixture2'
# best_team, best_points, total_cost = analyzer.find_best_team_lp_by_fixture(
#     fixture)
# print("Best Team:")
# analyzer.display_team(best_team, best_points, total_cost)
