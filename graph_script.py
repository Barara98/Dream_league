from collections import Counter
from player_data_analyzer import PlayersDataAnalyzer
import networkx as nx

fixture_list = ["fixture1", "fixture2", "fixture3", "fixture4", "fixture5"]


def create_team_graph(valid_squads):
    team_graph = nx.MultiGraph()

    for i, squad in enumerate(valid_squads, 1):
        team_name = f'Team {i}'
        team_data = tuple(squad)
        total_points = sum(player['points'] for player in squad)

        team_graph.add_node(team_name, team_data=team_data,
                            total_points=total_points)

    return team_graph


def create_edges_based_on_similarity(team_graph):
    teams = list(team_graph.nodes)
    prog = 0
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            prog += 1
            # print(prog)
            team1 = teams[i]
            team2 = teams[j]

            squad1 = team_graph.nodes[team1]['team_data']
            squad2 = team_graph.nodes[team2]['team_data']

            # Check if there are common players in both squads
            common_players = [player1 for player1 in squad1 if any(
                player1['name'] == player2['name'] for player2 in squad2)]

            # If there are common players, consider teams to be similar
            if len(common_players) >= 3:
                team_graph.add_edge(
                    team1, team2, common_players=common_players)


def are_squads_unique(all_squads):
    seen_squads = set()

    for i, squad in enumerate(all_squads, 1):
        squad_tuple = tuple(tuple(player.items()) for player in squad)
        if squad_tuple in seen_squads:
            print(f"Duplicate squad found at index {i}")
            return False
        seen_squads.add(squad_tuple)

        # print(f"Progress: {i}/{len(all_squads)} squads processed")

    return True


def get_valid_teams(teams, budget_limit, max_players_per_team):
    valid_teams = []
    invalid_count = 0

    for i, team in enumerate(teams, 1):
        total_budget = sum(player["price"] for player in team)

        # Check budget constraint
        if total_budget > budget_limit:
            # print(f"Team {i}: Budget constraint violated")
            invalid_count += 1
            continue

        # Check team constraint using Counter
        team_counts = Counter(player["team"] for player in team)
        if any(count > max_players_per_team for count in team_counts.values()):
            # print(f"Team {i}: Team constraint violated")
            invalid_count += 1
            continue

        # Check positions constraint (customize based on your needs)
        positions_counts = Counter(player["position"] for player in team)

        # Adjust the position constraints based on your requirements
        if positions_counts["GK"] != 1 or positions_counts["CB"] != 4 or positions_counts["MD"] != 4 or positions_counts["FW"] != 2:
            # print(f"Team {i}: Positions constraint violated")
            invalid_count += 1
            continue

        # Team is valid, append to the list
        valid_teams.append(team)

        # Print progress
        # print(f"Progress: {i}/{len(teams)} teams processed")

    return valid_teams, invalid_count


db_path = "player_data.db"
analyzer = PlayersDataAnalyzer(db_path)

for fixture in fixture_list:
    valid_squads = analyzer.generate_valid_squads(19)
    print(len(valid_squads))
# print(valid_squads[0])

if are_squads_unique(valid_squads):
    print("All squads are unique.")
else:
    print("Duplicate squads found.")

valid_teams, invalid_count = get_valid_teams(valid_squads, 108, 2)
print(f"Number of invalid teams: {invalid_count}")
print(f"Valid teams: {len(valid_teams)}")

team_graph = create_team_graph(valid_squads)
create_edges_based_on_similarity(team_graph)


node_name = 'Team 2'
retrieved_team_data = team_graph.nodes[node_name]['team_data']
retrieved_total_points = team_graph.nodes[node_name]['total_points']

# print("Retrieved Team Data:", retrieved_team_data)
print("Retrieved Total Points:", retrieved_total_points)

edges_of_node = list(team_graph.neighbors(node_name))
print(len(edges_of_node))
