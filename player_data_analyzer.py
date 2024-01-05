from collections import Counter
import copy
from itertools import combinations
import math
import random
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

    def display_team(self, team):
        total_points = sum(player["points"] for player in team)
        total_cost = sum(player["price"] for player in team)

        # Sort the team by position order: GK, CB, MD, FW
        sorted_team = sorted(team, key=lambda x: (
            x["position"] != "GK", x["position"] != "CB", x["position"] != "MD", x["position"] != "FW"))

        for player in sorted_team:
            print(
                f"{player['name']} ({player['position']}) - {player['team']} - Price: {player['price']} - Points: {player['points']}"
            )

        print(f"Total Points: {total_points}")
        print(f"Total Cost: {total_cost}")

    def display_subs(self, subs_out, subs_in):
        print("Subs Out:")
        for player in subs_out:
            print(
                f"{player['name']} ({player['position']}) - {player['team']} - Price: {player['price']} - Points: {player['points']}"
            )
        print("Subs In:")
        for player in subs_in:
            print(
                f"{player['name']} ({player['position']}) - {player['team']} - Price: {player['price']} - Points: {player['points']}"
            )

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

    def build_random_team(self):
        available_players = self.db.get_all_players()
        random.shuffle(available_players)  # Shuffle the players list randomly

        budget_left = self.budget
        selected_players = []
        players_count = {"GK": 0, "CB": 0, "MD": 0, "FW": 0}
        team_count = {}

        for player in available_players:
            if self.add_player_to_team(player, players_count, team_count, budget_left, self.position_constraints, self.max_players_per_team):
                selected_players.append(player)

            # Check if we have exactly 11 players
            if len(selected_players) == 11:
                # Check if minimum constraints are met
                if (
                    players_count["GK"] == 1
                    and players_count["CB"] >= self.position_constraints["CB"][0]
                    and players_count["CB"] <= self.position_constraints["CB"][1]
                    and players_count["MD"] >= self.position_constraints["MD"][0]
                    and players_count["MD"] <= self.position_constraints["MD"][1]
                    and players_count["FW"] >= self.position_constraints["FW"][0]
                    and players_count["FW"] <= self.position_constraints["FW"][1]
                ):
                    return selected_players

        # If loop completes and constraints are not met, try again
        return self.build_random_team()

    def random_subs(self, team, mutate=False):
        available_players = self.db.get_all_players()
        remaining_players = [
            player for player in available_players if player not in team]
        if mutate:
            random.shuffle(remaining_players)
        else:
            remaining_players.sort(key=lambda x: x["points"], reverse=True)

        num_of_subs = random.randint(1, 3)
        subs_out = random.sample(team, num_of_subs)
        new_team = [player for player in team if player not in subs_out]
        names_set = set(player["name"] for player in new_team)
        subs_in = []

        players_count = {"GK": 0, "CB": 0, "MD": 0, "FW": 0}
        team_count = {}
        for player in new_team:
            players_count[player["position"]] += 1
            team_count[player["team"]] = team_count.get(player["team"], 0) + 1

        remaining_budget = self.budget - \
            sum(player["price"] for player in team)

        if players_count["GK"] == 0:
            gk_reamined = [
                player for player in remaining_players if player["position"] == "GK"]
            selecting = True
            while selecting:
                gk = random.choice(gk_reamined)
                if gk["name"] in names_set:
                    continue
                if self.add_player_to_team(gk, players_count, team_count, remaining_budget, self.position_constraints, self.max_players_per_team):
                    subs_in.append(gk)
                    new_team.append(gk)
                    selecting = False

        for player in remaining_players:
            if player["name"] in names_set:
                continue
            if self.add_player_to_team(player, players_count, team_count, remaining_budget, self.position_constraints, self.max_players_per_team):
                subs_in.append(player)
                new_team.append(player)

                # Check if we have exactly 11 players
                if len(new_team) == 11:
                    # Check if minimum constraints are met
                    if (
                        players_count["GK"] == 1
                        and players_count["CB"] >= self.position_constraints["CB"][0]
                        and players_count["CB"] <= self.position_constraints["CB"][1]
                        and players_count["MD"] >= self.position_constraints["MD"][0]
                        and players_count["MD"] <= self.position_constraints["MD"][1]
                        and players_count["FW"] >= self.position_constraints["FW"][0]
                        and players_count["FW"] <= self.position_constraints["FW"][1]
                    ):
                        return new_team, subs_out, subs_in
        return self.random_subs(team)

    def get_valid_teams(self, teams):
        valid_teams = []

        for team in teams:
            if self.check_team_constraints(team):
                valid_teams.append(team)

        return valid_teams

    def check_team_constraints(self, team):
        total_budget = sum(player["price"] for player in team)

        # Check budget constraint
        if total_budget > self.budget:
            print(f"Team Budget constraint violated")
            return False

        # Check team constraint using Counter
        team_counts = Counter(player["team"] for player in team)
        if any(count > self.max_players_per_team for count in team_counts.values()):
            print(f"Team constraint violated")
            return False

        # Check positions constraint (customize based on your needs)
        positions_counts = Counter(player["position"] for player in team)

        # Adjust the position constraints based on your requirements
        if (
            positions_counts["GK"] != 1
            or positions_counts["CB"] > 5
            or positions_counts["CB"] < 3
            or positions_counts["MD"] > 5
            or positions_counts["MD"] < 3
            or positions_counts["FW"] > 3
            or positions_counts["FW"] < 1
        ):
            print(f"Team Positions constraint violated")
            return False

        # All constraints are met
        return True

    def add_player_to_team(self, player, players_count, team_count, remaining_budget, position_constraints, max_players_per_team):
        if (
            players_count[player["position"]
                          ] < position_constraints[player["position"]][1]
            and team_count.get(player["team"], 0) < max_players_per_team
            and remaining_budget >= player["price"]
        ):
            players_count[player["position"]] += 1
            team_count[player["team"]] = team_count.get(player["team"], 0) + 1
            remaining_budget -= player["price"]
            return True
        return False

    def team_sequence(self, fixtures):
        team_sequence = {}
        team_sequence[fixtures[0]] = self.build_random_team()
        for player in team_sequence[fixtures[0]]:
            player["points"] = self.db.get_player_points_in_fixture(player["name"], fixtures[0])

        for idx, fixture in enumerate(fixtures[1:], start=1):
            temp = copy.deepcopy(team_sequence[fixtures[idx - 1]])
            team_sequence[fixture], subs_in, subs_out = self.random_subs(temp)
            for player in team_sequence[fixture]:
                player["points"] = self.db.get_player_points_in_fixture(player["name"], fixture)

        return team_sequence

    def fitness(self, teams):
        total_points = 0
        for fixture in teams:
            total_points += sum(player["points"] for player in teams[fixture])
        return total_points


# Create an instance of PlayersDataAnalyzer
db_path = "player_data.db"
analyzer = PlayersDataAnalyzer(db_path)

# # # Use the find_best_team function to find the best team.
# best_team, best_points, total_cost = analyzer.find_best_team()
# print("Best Team:")
# analyzer.display_team(best_team)


# fixture = 'fixture2'
# best_team, best_points, total_cost = analyzer.find_best_team_lp_by_fixture(
#     fixture)
# print("Best Team:")
# analyzer.display_team(best_team, best_points, total_cost)

# valid_squads = analyzer.generate_valid_squads(16)

# print(len(valid_squads))
# print(valid_squads[0])

# random_teams = [analyzer.build_random_team() for i in range(1000)]
# print(len(random_teams))


fixture_list = ["fixture1", "fixture2", "fixture3", "fixture4", "fixture5"]
random_sequences = [analyzer.team_sequence(fixture_list) for i in range(500)]
random_sequences.sort(key=analyzer.fitness, reverse=True)
for i in range(len(random_sequences[0])):
    print(f'Team {i + 1}')
    analyzer.display_team(random_sequences[0][fixture_list[i]])

print(analyzer.fitness(random_sequences[0]))
