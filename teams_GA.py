from itertools import combinations


from player_data_analyzer import PlayersDataAnalyzer
from data_utility import DataUtility


def random_team_creator(players, formation, budget):
    players = analyzer.db.get_all_players()
    goalkeepers = [
        player for player in players if player["position"] == "GK"]
    defenders = [
        player for player in players if player["position"] == "CB"]
    midfielders = [
        player for player in players if player["position"] == "MD"]
    forwards = [
        player for player in players if player["position"] == "FW"]

    budget_left = budget
    random_team = []
    players_count = {"GK": 0, "CB": 0, "MD": 0, "FW": 0}
    team_count = {}


data_utility = DataUtility()
db_path = "player_data.db"
analyzer = PlayersDataAnalyzer(db_path)

players = analyzer.db.get_all_players()
random_teams = [random_team_creator(players) for i in range(10)]
