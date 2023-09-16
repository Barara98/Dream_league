from itertools import combinations
import json
import random
import pulp


class PlayersDataAnalyzer:
    def __init__(self, json_file_path):
        """
        Initialize the PlayersDataAnalyzer with JSON data from a file.

        Args:
            json_file_path (str): The path to the JSON file containing player data.
        """
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            self.players_data = json.load(json_file)
        self.budget = 108  # Define the budget attribute
        self.position_constraints = {
            "GK": (1, 1),  # Exactly 1 goalkeeper
            "CB": (3, 5),  # 3 to 5 center-backs
            "MD": (3, 5),  # 3 to 5 midfielders
            "FW": (1, 3),  # 1 to 3 forwards
        }
        self.max_players_per_team = 2

    def get_total_players(self, points=0, min_price=3, max_price=15, min=True):
        if min:
            qualifying_players = [
                player
                for position_data in self.players_data.values()
                for player in position_data
                if player["points"] >= points
                and player["price"] >= min_price
                and player["price"] <= max_price
            ]
        else:
            qualifying_players = [
                player
                for position_data in self.players_data.values()
                for player in position_data
                if player["points"] == points
                and player["price"] >= min_price
                and player["price"] <= max_price
            ]

        # Return the count of qualifying players
        return qualifying_players

    def get_total_players_by_fixture(self, fixture="all"):
        if fixture == "all":
            return self.get_total_players()
        else:
            qualifying_players = []
            for position_data in self.players_data.values():
                for player in position_data:
                    if fixture in player["fixtures"]:
                        fixture_data = player["fixtures"][fixture]
                        if (
                            fixture_data.get("events")
                            .get("Minutes Played")
                            .get("Quantity")
                            > 0
                        ):
                            qualifying_players.append(player)
            return qualifying_players

    def get_total_points_by_position(self):
        total_points_by_position = {}
        for position, position_data in self.players_data.items():
            total_points = sum(player["points"] for player in position_data)
            total_points_by_position[position] = total_points
        return total_points_by_position

    def build_random_team(self):
        print("Building random team")
        budget = 108  # Initial budget in millions
        team = {"GK": [], "CB": [], "MD": [], "FW": []}
        selected_teams = {}  # Use a dictionary to track selected teams and their counts

        gk_players = self.players_data["GK"]
        random.shuffle(gk_players)
        # Append the selected goalkeeper to the list
        team["GK"].append(gk_players[0])
        # Use [0] to access the first (and only) element
        budget -= team["GK"][0]["price"]
        # Initialize the count for the selected team
        selected_teams[team["GK"][0]["team"]] = 1

        # Randomly select 3 CB players
        budget = self._randomly_select_players("CB", 3, team, selected_teams, budget)

        # Randomly select 3 MD players
        budget = self._randomly_select_players("MD", 3, team, selected_teams, budget)

        # Randomly select 1 FW player
        budget = self._randomly_select_players("FW", 1, team, selected_teams, budget)

        # Randomly select the remaining positions to complete the team
        budget = self._randomly_select_remaining_players(team, selected_teams, budget)

        # Display the random team
        self.display_team(team)
        print(f"Remaining Budget: {budget}M")

        return team, budget

    def _randomly_select_players(self, position, count, team, selected_teams, budget):
        for _ in range(count):
            players = self.players_data[position]
            random.shuffle(players)
            player = players[0]

            # Check if the player's team has already been selected twice
            team_count = selected_teams.get(player["team"], 0)
            if team_count < 2 and budget >= player["price"]:
                team[position].append(player)
                budget -= player["price"]
                selected_teams[player["team"]] = team_count + 1

        return budget  # Return the updated budget

    def _randomly_select_remaining_players(self, team, selected_teams, budget):
        while len(team["CB"]) + len(team["MD"]) + len(team["FW"]) < 10:
            # Randomly select a position to fill (CB, MD, or FW)
            check_position = False
            while not check_position:
                position = random.choice(["CB", "MD", "FW"])
                if (
                    (position == "CB" and len(team["CB"]) < 5)
                    or (position == "MD" and len(team["MD"]) < 5)
                    or (position == "FW" and len(team["FW"]) < 3)
                ):
                    check_position = True

            budget = self._randomly_select_players(
                position, 1, team, selected_teams, budget
            )
        return budget

    def display_team(self, team):
        for position, players in team.items():
            print(f"{position}s:")
            for player in players:
                print(f"- {player['name']} ({player['team']})")

    def find_best_team_lp(self):
        # Create a linear programming problem
        prob = pulp.LpProblem("FantasyFootball", pulp.LpMaximize)

        # Define variables: binary variables for player selection
        player_vars = {
            player["name"]: pulp.LpVariable(player["name"], cat=pulp.LpBinary)
            for position_players in self.players_data.values()
            for player in position_players
        }

        # Objective function: maximize total points

        prob += pulp.lpSum(
            player["points"] * player_vars[player["name"]]
            for position_players in self.players_data.values()
            for player in position_players
        )

        # Budget constraint
        prob += (
            pulp.lpSum(
                player["price"] * player_vars[player["name"]]
                for position_players in self.players_data.values()
                for player in position_players
            )
            <= self.budget
        )

        # Position constraints
        for position, (min_count, max_count) in self.position_constraints.items():
            prob += (
                pulp.lpSum(
                    player_vars[player["name"]]
                    for player in self.players_data[position]
                )
                >= min_count
            )
            prob += (
                pulp.lpSum(
                    player_vars[player["name"]]
                    for player in self.players_data[position]
                )
                <= max_count
            )

        # Max 2 players from the same team constraint
        for team in set(
            player["team"]
            for position_players in self.players_data.values()
            for player in position_players
        ):
            prob += (
                pulp.lpSum(
                    player_vars[player["name"]]
                    for position_players in self.players_data.values()
                    for player in position_players
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
            for position_players in self.players_data.values()
            for player in position_players
            if pulp.value(player_vars[player["name"]]) == 1
        ]

        # Calculate total points
        total_points = pulp.value(prob.objective)
        total_cost = sum(player["price"] for player in best_team)

        return best_team, total_points, total_cost

    def find_best_team_lp_by_fixture(self, fixture="fixture1"):
        player_list = self.get_total_players_by_fixture(fixture)
        # Create a linear programming problem
        prob = pulp.LpProblem("FantasyFootball", pulp.LpMaximize)

        # Define variables: binary variables for player selection
        player_vars = {
            player["name"]: pulp.LpVariable(player["name"], cat=pulp.LpBinary)
            for player in player_list
        }

        # Objective function: maximize total points
        prob += pulp.lpSum(
            player["fixtures"][fixture]["Points"] * player_vars[player["name"]]
            for player in player_list
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

        # Update points to fixture points
        for player in best_team:
            player["points"] = player["fixtures"][fixture]["Points"]

        return best_team, total_points, total_cost


# Create an instance of PlayersDataAnalyzer
# json_file_path = 'all_players_data.json'  # Replace with your JSON file path
# analyzer = PlayersDataAnalyzer(json_file_path)

# # Test the get_total_players method
# total_players = analyzer.get_total_players()
# print(f'Total Players: {len(total_players)}')

# total_players = analyzer.get_total_players_by_fixture('fixture1')
# print(f'Total Players in fixture 1: {len(total_players)}')
# for player in total_players:
#     print(player['name'])


# # Test the get_total_points_by_position method
# total_points_by_position = analyzer.get_total_points_by_position()
# print('Total Points by Position:')
# for position, total_points in total_points_by_position.items():
#     print(f'{position}: {total_points}')


# # Test the build_random_team method
# random_team, remaining_budget = analyzer.build_random_team()
# print('Random Team:')
# analyzer.display_team(random_team)
# print(f'Remaining Budget: {remaining_budget}M')


# Use the find_best_team function to find the best team.
# best_team, best_points, total_cost = analyzer.find_best_team_lp()
# print("Best Team:")
# for player in best_team:
#     print(f"{player['name']} ({player['position']}) - {player['team']} - Price: {player['price']} - Points: {player['points']}")
# print(f"Total Points: {best_points}")
# print(f"Total Cost: {total_cost}")

# fixture = 'fixture2'
# best_team, best_points, total_cost = analyzer.find_best_team_lp_by_fixture(fixture)
# print("Best Team:")
# for player in best_team:
#     print(f"{player['name']} ({player['position']}) - {player['team']} - Price: {player['price']} - Points: {player['points']}")
# print(f"Total Points: {best_points}")
# print(f"Total Cost: {total_cost}")
