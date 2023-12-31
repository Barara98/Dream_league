import pulp

from playerDB import PlayerDataDB

db = PlayerDataDB("player_data.db")


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

    def display_team(self, team):
        for player in team:
            print(
                f"{player['name']} ({player['position']}) - {player['team']} - Price: {player['price']} - Points: {player['points']}")
        print(f"Total Points: {best_points}")
        print(f"Total Cost: {total_cost}")

    def find_best_team_lp_by_fixture(self, fixture="fixture1"):
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
            player["points"] * player_vars[player["name"]] for player in player_list
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

    def find_best_team_lp(self):
        players_data = self.db.get_all_players()
        # Create a linear programming problem
        prob = pulp.LpProblem("FantasyFootball", pulp.LpMaximize)

        # Define variables: binary variables for player selection
        player_vars = {
            player_data["name"]: pulp.LpVariable(
                player_data["name"], cat=pulp.LpBinary)
            for player_data in players_data
        }

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
            <= self.budget
        )

        # Position constraints
        for position, (min_count, max_count) in self.position_constraints.items():
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
                <= self.max_players_per_team
            )

        # Exactly 11 players constraint
        prob += pulp.lpSum(player_vars.values()) == 11

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

        return best_team, total_points, total_cost

    def find_best_team_stars(self, players_data):
        # Create a linear programming problem
        prob = pulp.LpProblem("FantasyFootball", pulp.LpMaximize)

        # Define variables: binary variables for player selection
        player_vars = {
            player_data["name"]: pulp.LpVariable(
                player_data["name"], cat=pulp.LpBinary)
            for player_data in players_data
        }

        # Objective function: maximize total points
        prob += pulp.lpSum(
            player_data["stars"] * player_vars[player_data["name"]]
            for player_data in players_data
        )

        # Budget constraint
        prob += (
            pulp.lpSum(
                player_data["price"] * player_vars[player_data["name"]]
                for player_data in players_data
            )
            <= self.budget
        )

        # Position constraints
        for position, (min_count, max_count) in self.position_constraints.items():
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
                <= self.max_players_per_team
            )

        # Exactly 11 players constraint
        prob += pulp.lpSum(player_vars.values()) == 11

        # Solve the LP problem
        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        # Extract the selected players as objects
        best_team = [
            player_data
            for player_data in players_data
            if pulp.value(player_vars[player_data["name"]]) == 1
        ]

        # Calculate total points and total cost
        total_points = sum(player_data["points"] for player_data in best_team)
        total_cost = sum(player_data["price"] for player_data in best_team)
        total_stars = sum(player_data["stars"] for player_data in best_team)

        return best_team, total_points, total_cost, total_stars


# Create an instance of PlayersDataAnalyzer
# db_path = "player_data.db"  # Replace with your JSON file path
# analyzer = PlayersDataAnalyzer(db_path)

# # Use the find_best_team function to find the best team.
# best_team, best_points, total_cost = analyzer.find_best_team_lp()
# print("Best Team:")
# analyzer.display_team(best_team)


# fixture = 'fixture2'
# best_team, best_points, total_cost = analyzer.find_best_team_lp_by_fixture(
#     fixture)
# print("Best Team:")
# analyzer.display_team(best_team)
