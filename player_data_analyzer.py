from itertools import combinations
import math
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

    def generate_valid_squads(self, points, num_defenders=4, num_midfielders=4, num_forwards=2):
        valid_squads = []
        all_players = list(self.db.get_players_min_points(points))

        print(f"Total number of players: {len(all_players)}")

        goalkeepers = [
            player for player in all_players if player["position"] == "GK"]
        defenders = [
            player for player in all_players if player["position"] == "CB"]
        midfielders = [
            player for player in all_players if player["position"] == "MD"]
        forwards = [
            player for player in all_players if player["position"] == "FW"]

        fw_comb = math.comb(len(forwards), num_forwards)
        cb_comb = math.comb(len(defenders), num_defenders)
        md_comb = math.comb(len(midfielders), num_midfielders)
        print(f"Forward combinations: {fw_comb}")
        print(f"Defender combinations: {cb_comb}")
        print(f"Midfielder combinations: {md_comb}")

        # Calculate total combinations
        total_combinations = (cb_comb * md_comb * fw_comb * len(goalkeepers))
        print(f"Number of total combinations: {total_combinations}")

        past_defenders = defenders
        past_forwards = forwards
        position_update_teams = set()
        progress = 0
        # Generate combinations for each position
        for gk in goalkeepers:
            for midfielder_combination in combinations(midfielders, num_midfielders):
                defenders = past_defenders
                forwards = past_forwards
                squad_combination = (midfielder_combination + (gk,))
                valid_team, position_update_teams = self.check_team_constraints(
                    squad_combination)
                if not valid_team:
                    progress += fw_comb * cb_comb
                    continue
                if position_update_teams:
                    forwards = self.remove_players_from_list(
                        forwards, position_update_teams)
                    defenders = self.remove_players_from_list(
                        defenders, position_update_teams)

                for defender_combination in combinations(defenders, num_defenders):
                    forwards = past_forwards
                    squad_combination = (
                        defender_combination + midfielder_combination + (gk,))
                    valid_team, position_update_teams = self.check_team_constraints(
                        squad_combination)
                    if not valid_team:
                        progress += fw_comb
                        continue
                    if position_update_teams:
                        forwards = self.remove_players_from_list(
                            forwards, position_update_teams)

                    for forward_combination in combinations(forwards, num_forwards):
                        progress += 1
                        squad_combination = (
                            defender_combination + midfielder_combination +
                            forward_combination + (gk,)
                        )

                        # Check budget constraint
                        total_budget = sum(player["price"]
                                           for player in squad_combination)
                        if total_budget <= self.budget and self.check_team_constraints(squad_combination):
                            # Check team constraint
                            # print(progress)
                            valid_squads.append(squad_combination)
        return valid_squads

    def check_team_constraints(self, squad_combination):
        team_counts = {}
        checker = []
        for player in squad_combination:
            team_name = player["team"]
            team_counts[team_name] = team_counts.get(team_name, 0) + 1
            if team_counts[team_name] > self.max_players_per_team:
                return False, checker
            if team_counts[team_name] == self.max_players_per_team and team_name not in checker:
                checker.append(team_name)
        return True, checker

    def remove_players_from_list(self, player_list, checker):
        updated_player_list = [
            player for player in player_list if player["team"] not in checker]
        return updated_player_list


# Create an instance of PlayersDataAnalyzer
db_path = "player_data.db"
analyzer = PlayersDataAnalyzer(db_path)

# # # Use the find_best_team function to find the best team.
# best_team, best_points, total_cost = analyzer.find_best_team()
# print("Best Team:")
# analyzer.display_team(best_team, best_points, total_cost)


# fixture = 'fixture2'
# best_team, best_points, total_cost = analyzer.find_best_team_lp_by_fixture(
#     fixture)
# print("Best Team:")
# analyzer.display_team(best_team, best_points, total_cost)

# valid_squads = analyzer.generate_valid_squads(16)

# print(len(valid_squads))
# print(valid_squads[0])
