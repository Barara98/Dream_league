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
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            self.players_data = json.load(json_file)
        self.budget = 108  # Define the budget attribute
        self.position_constraints = {
            'GK': (1, 1),  # Exactly 1 goalkeeper
            'CB': (3, 5),  # 3 to 5 center-backs
            'MD': (3, 5),  # 3 to 5 midfielders
            'FW': (1, 3)   # 1 to 3 forwards
        }
        self.max_players_per_team = 2

    def get_total_players(self, points=0, min_price = 3, max_price = 15, min = True):
        if min:
            qualifying_players = [player for position_data in self.players_data.values()
                            for player in position_data if player['points'] >= points and player['price'] >= min_price and player['price'] <= max_price]
        else:
            qualifying_players = [player for position_data in self.players_data.values()
                            for player in position_data if player['points'] == points and player['price'] >= min_price and player['price'] <= max_price]
        
        # Return the count of qualifying players
        return qualifying_players

    def get_total_points_by_position(self):
        total_points_by_position = {}
        for position, position_data in self.players_data.items():
            total_points = sum(player['points'] for player in position_data)
            total_points_by_position[position] = total_points
        return total_points_by_position

    def build_random_team(self):
        print("Building random team")
        budget = 108  # Initial budget in millions
        team = {'GK': [], 'CB': [], 'MD': [], 'FW': []}
        selected_teams = {}  # Use a dictionary to track selected teams and their counts

        gk_players = self.players_data['GK']
        random.shuffle(gk_players)
        # Append the selected goalkeeper to the list
        team['GK'].append(gk_players[0])
        # Use [0] to access the first (and only) element
        budget -= team['GK'][0]['price']
        # Initialize the count for the selected team
        selected_teams[team['GK'][0]['team']] = 1

        # Randomly select 3 CB players
        budget = self._randomly_select_players(
            'CB', 3, team, selected_teams, budget)

        # Randomly select 3 MD players
        budget = self._randomly_select_players(
            'MD', 3, team, selected_teams, budget)

        # Randomly select 1 FW player
        budget = self._randomly_select_players(
            'FW', 1, team, selected_teams, budget)

        # Randomly select the remaining positions to complete the team
        budget = self._randomly_select_remaining_players(
            team, selected_teams, budget)

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
            team_count = selected_teams.get(player['team'], 0)
            if team_count < 2 and budget >= player['price']:
                team[position].append(player)
                budget -= player['price']
                selected_teams[player['team']] = team_count + 1

        return budget  # Return the updated budget

    def _randomly_select_remaining_players(self, team, selected_teams, budget):
        while len(team['CB']) + len(team['MD']) + len(team['FW']) < 10:
            # Randomly select a position to fill (CB, MD, or FW)
            check_position = False
            while not check_position:
                position = random.choice(['CB', 'MD', 'FW'])
                if (
                    (position == 'CB' and len(team['CB']) < 5) or
                    (position == 'MD' and len(team['MD']) < 5) or
                    (position == 'FW' and len(team['FW']) < 3)
                ):
                    check_position = True

            budget = self._randomly_select_players(
                position, 1, team, selected_teams, budget)
        return budget

    def display_team(self, team):
        for position, players in team.items():
            print(f"{position}s:")
            for player in players:
                print(f"- {player['name']} ({player['team']})")

    def find_best_team(self, max_players_per_team=2):
        #lpsum is the sum of the values in the array, the object inside are 0 or 1, because of this we multyply the points and price and just sum the num of players and positions.
        # Create a linear programming problem
        model = pulp.LpProblem("Fantasy_Football_Team_Selection", pulp.LpMaximize)

        # Create a dictionary to store player variables
        player_vars = {}
        # Define decision variables (binary variables for player selection)
        for position, players in self.players_data.items():
            for i, player in enumerate(players):
                player_vars[(position, i)] = pulp.LpVariable(f"Player_{position}_{i}", cat=pulp.LpBinary)
        
        # Objective function: Maximize total points
        model += pulp.lpSum(player["points"] * player_vars[(position, i)] for position, players in self.players_data.items() for i, player in enumerate(players)), "Total_Points"

        # Budget constraint
        model += pulp.lpSum(player["price"] * player_vars[(position, i)] for position, players in self.players_data.items() for i, player in enumerate(players)) <= self.budget, "Budget_Constraint"

        # Position constraints
        for position, (min_count, max_count) in self.position_constraints.items():
            model += pulp.lpSum(player_vars[(position, i)] for i in range(len(self.players_data[position]))) >= min_count, f"{position}_Min_Constraint"
            model += pulp.lpSum(player_vars[(position, i)] for i in range(len(self.players_data[position]))) <= max_count, f"{position}_Max_Constraint"

        # Additional constraint: Select exactly 11 players
        model += pulp.lpSum(player_vars[(position, i)] for position in self.players_data for i in range(len(self.players_data[position]))) == 11, "Select_11_Players"

        # Additional constraint: Maximum 2 players from the same team
        team_counts = {}
        for position, players in self.players_data.items():
            for i, player in enumerate(players):
                team = player["team"]
                if team in team_counts:
                    team_counts[team].append(player_vars[(position, i)])
                else:
                    team_counts[team] = [player_vars[(position, i)]]

        # team vars is the players inside the team
        for team, team_vars in team_counts.items():
            model += pulp.lpSum(team_vars) <= max_players_per_team, f"Max_Players_Team_{team}"

        # Solve the optimization problem
        model.solve()

        # Extract the selected team
        selected_team = [(player, player_vars[(position, i)]) for position, players in self.players_data.items() for i, player in enumerate(players) if pulp.value(player_vars[(position, i)]) == 1]

        # Calculate total points and total cost
        total_points = sum(player["points"] for player, _ in selected_team)
        total_cost = sum(player["price"] for player, _ in selected_team)

        return selected_team, total_points, total_cost

# Create an instance of PlayersDataAnalyzer
json_file_path = 'players_data.json'  # Replace with your JSON file path
analyzer = PlayersDataAnalyzer(json_file_path)

# # Test the get_total_players method
# total_players = analyzer.get_total_players()
# print(f'Total Players: {total_players}')

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
best_team, total_points, total_cost = analyzer.find_best_team()

# Print the selected team and its details.
print("Selected Team:")
for player, _ in best_team:
    print(f"{player['name']} ({player['position']} - {player['team']}): {player['points']} points")


print(f"Total Points: {total_points}")
print(f"Total Cost: {total_cost}M")
