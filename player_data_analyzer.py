from collections import Counter
import copy
from itertools import combinations
import math
import random
import time
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
        self.fixture_list = ["fixture1", "fixture2", "fixture3", "fixture4", "fixture5", "fixture6"]

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

    def find_best_team(self, fixture="All", key="points", sub_key="points", budget=108, min_budget=92):
        if fixture == "All":
            player_list = self.db.get_all_players()
        else:
            player_list = self.db.get_players_by_fixture(fixture)

        random.shuffle(player_list)

        # Create a linear programming problem
        prob = pulp.LpProblem("FantasyFootball", pulp.LpMaximize)

        # Define variables: binary variables for player selection
        player_vars = {player["name"]: pulp.LpVariable(player["name"], cat=pulp.LpBinary) for player in player_list}

        # Objective function: maximize total points
        prob += pulp.lpSum((player[key] * player_vars[player["name"]] + 0.5 * player[sub_key]
                           * player_vars[player["name"]]) for player in player_list)

        # Budget constraint
        prob += pulp.lpSum(player["price"] * player_vars[player["name"]] for player in player_list) <= budget
        prob += pulp.lpSum(player["price"] * player_vars[player["name"]] for player in player_list) >= min_budget

        # Position constraints
        for position, (min_count, max_count) in self.position_constraints.items():
            prob += pulp.lpSum(player_vars[player["name"]] for player in player_list if player["position"] == position) >= min_count
            prob += pulp.lpSum(player_vars[player["name"]] for player in player_list if player["position"] == position) <= max_count

        # Max 2 players from the same team constraint
        for team in set(player["team"] for player in player_list):
            prob += pulp.lpSum(player_vars[player["name"]] for player in player_list if player["team"] == team) <= self.max_players_per_team

        # Exactly 11 players constraint
        prob += pulp.lpSum(player_vars.values()) == 11

        # Solve the LP problem
        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        # Extract the selected players as objects
        best_team = [player for player in player_list if pulp.value(player_vars[player["name"]]) == 1]

        return best_team

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

    def team_sequence(self):
        budget_max = random.randint(92, 108)
        budget_min = random.randint(92, budget_max)
        team = self.find_best_team(key="stars", sub_key="stars", fixture="fixture1", budget=budget_max, min_budget=budget_min)
        team_sequence = self.find_best_sequence_of_squads(team, self.fixture_list)

        return team_sequence

    def fitness(self, teams):
        total_points = 0
        for fixture in teams:
            total_points += sum(player["points"] for player in teams[fixture])
        return total_points

    def crossover(self, team_sq, mutate=False):
        team_sq_copy = copy.deepcopy(team_sq)
        fixture = random.choice(self.fixture_list)
        index = self.fixture_list.index(fixture)
        fx_lst = self.fixture_list[index:]
        temp = copy.deepcopy(team_sq_copy[fixture])
        if mutate:
            choice = random.choice(["stars", "price", "next_points", "rand_index"])
            choice2 = random.choice(["stars", "price", "next_points", "rand_index"])
            team_sq_copy.update(self.find_best_sequence_of_squads(temp, fx_lst, key=choice, sub_key=choice2))
        else:
            team_sq_copy.update(self.find_best_sequence_of_squads(temp, fx_lst))

        return team_sq_copy

    def check_sequence(self, team_sq):
        for idx, fixture in enumerate(self.fixture_list[1:], start=1):
            temp1 = team_sq[self.fixture_list[idx - 1]]
            temp2 = team_sq[self.fixture_list[idx]]
            names_set1 = set(player["name"] for player in temp1)
            names_set2 = set(player["name"] for player in temp2)
            unique_names_set1 = names_set1.difference(names_set2)
            if len(unique_names_set1) > 3:
                return len(unique_names_set1)
        return None

    def ga(self, size, generations, muProb):
        random_sequences = [self.team_sequence() for i in range(size)]
        random_sequences.sort(key=self.fitness, reverse=True)
        print(f'Best Random Result:{self.fitness(random_sequences[0])}')

        best = random_sequences[0]

        for i in range(generations):
            random_sequences = random_sequences[:len(random_sequences)//2]
            childrens = []
            for j in range(len(random_sequences)):
                if random.random() < muProb:

                    c1 = self.crossover(random_sequences[j], True)
                else:
                    c1 = self.crossover(random_sequences[j])
                childrens.append(c1)
            random_sequences.extend(childrens)
            random_sequences.sort(key=self.fitness, reverse=True)
            print(f'Best Result in the Generation:{self.fitness(random_sequences[0])}')

            if (self.fitness(best) < self.fitness(random_sequences[0])):
                best = random_sequences[0]
                print(f'Generation: {i + 1}')
                print(f'Best Result:{self.fitness(best)}')
        return best

    def find_best_sequence_of_squads(self, starting_team, fixture_sequence, key="points", sub_key="next_points"):
        max_substitutions = 3
        selected_players_sequence = []
        result = {}
        modified_sequence = fixture_sequence.copy()
        modified_sequence.insert(0, "initial")

        for i, fixture in enumerate(fixture_sequence):
            if i == 0:
                players_data = starting_team
            else:
                players_data = self.db.get_players_by_fixture(fixture)
                random.shuffle(players_data)

            prob = pulp.LpProblem("FantasyFootball", pulp.LpMaximize)

            # Define variables: binary variables for player selection
            player_vars = {player_data["name"]: pulp.LpVariable(
                player_data["name"], cat=pulp.LpBinary) for player_data in players_data}

            prob += pulp.lpSum((player[key] * player_vars[player["name"]] + 0.5 * player[sub_key]
                               * player_vars[player["name"]]) for player in players_data)

            prob += pulp.lpSum(
                player_data["price"] * player_vars[player_data["name"]] for player_data in players_data) <= self.budget

            for position, (min_count, max_count) in self.position_constraints.items():
                prob += pulp.lpSum(
                    player_vars[player_data["name"]] for player_data in players_data if player_data["position"] == position) >= min_count
                prob += pulp.lpSum(
                    player_vars[player_data["name"]] for player_data in players_data if player_data["position"] == position) <= max_count

            teams = set(player_data["team"] for player_data in players_data)
            for team in teams:
                prob += pulp.lpSum(
                    player_vars[player_data["name"]] for player_data in players_data if player_data["team"] == team) <= self.max_players_per_team

            prob += pulp.lpSum(player_vars.values()) == 11

            # If not the first fixture, add the substitution constraint
            if i > 0:
                substitutions = pulp.lpSum(
                    player_vars[player_data["name"]] for player_data in players_data if player_data["name"] not in selected_players_sequence)
                prob += substitutions <= max_substitutions

            # Solve the LP problem
            prob.solve(pulp.PULP_CBC_CMD(msg=False))

            # Extract the selected players as objects
            best_team = [player_data for player_data in players_data if pulp.value(
                player_vars[player_data["name"]]) == 1]

            # Update selected players sequence with the new team
            selected_players_sequence = [
                player_data["name"] for player_data in best_team]

            if fixture != "initial":
                result[fixture] = best_team

        return result


db_path = "player_data.db"
analyzer = PlayersDataAnalyzer(db_path)

# best = analyzer.find_best_team(fixture="fixture6")
# analyzer.display_team(best)


best = analyzer.ga(5, 20, 0.7)

for fixture in analyzer.fixture_list:
    print(f'Team {fixture}:')
    analyzer.display_team(best[fixture])
print(analyzer.fitness(best))

fix = analyzer.check_sequence(best)
if fix is not None:
    print(fix)
else:
    print("OK!!")
