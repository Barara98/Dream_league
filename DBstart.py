import json
from playerDB import PlayerDataDB
from player_data_analyzer import PlayersDataAnalyzer


db = PlayerDataDB("player_data.db")
db.create_tables()


def insert_all_teams(teams):
    for team_name, team_data in teams.items():
        overall = team_data['overall']
        attack = team_data['attack']
        defend = team_data['defend']
        db.insert_team(team_name, overall, attack, defend)
        print("Added team: " + team_name)


def insert_all_players(players):
    for player in players:
        name = player["name"]
        position = player["position"]
        team = player["team"]
        price = player["price"]
        points = player["points"]
        # injury = player["injury"]
        db.insert_player(name, position, team, price, points)
        print("Added player" + name)


def insert_all_fixtures(players):
    for positions in players:
        for player in positions:
            player_info = db.get_player_by_name(player["name"])
            if player_info:
                player_name = player_info['name']
                player_team = player_info['team']
                for fixture_name, fixture_data in player["fixtures"].items():
                    fixture_points = fixture_data["Points"]
                    db.insert_fixture(player_name, fixture_name,
                                    fixture_points, player_team)
            print(f"Added {player['name']} all fixtures")


def insert_all_events(players):
    for positions in players:
        for player in positions:
            player_fixtures = db.get_fixtures_by_player_name(player['name'])
            for fixture in player_fixtures:
                events_dict = player['fixtures'][fixture['fixture_name']]['events']
                for event_key, event_data in events_dict.items():
                    db.insert_event(
                        fixture['fixture_id'], event_key, event_data["Quantity"], event_data["Points"])
            print(f"Added {player['name']} all events")


def insert_all_events_by_fixture(players, fixutre_name):
    for positions in players:
        for player in positions:
            player_fixtures = db.get_fixtures_by_player_name(player['name'])
            for fixture in player_fixtures:
                if fixutre_name == fixture['fixture_name']:
                    events_dict = player['fixtures'][fixture['fixture_name']]['events']
                    for event_key, event_data in events_dict.items():
                        db.insert_event(
                            fixture['fixture_id'], event_key, event_data["Quantity"], event_data["Points"])
                print(f"Added {player['name']} all events")


def insert_DB():
    json_file_path = "all_players_data.json"
    analyzer = PlayersDataAnalyzer(json_file_path)
    # insert all players first time to the DB
    total_players = analyzer.get_total_players("All", -10)
    teams = {'מכבי פתח תקווה': {'overall': 3.0, 'attack': 3.0, 'defend': 3.0}, 'הפועל חיפה': {'overall': 3.0, 'attack': 4.0, 'defend': 3.0}, 'מכבי נתניה': {'overall': 3.0, 'attack': 4.0, 'defend': 3.0}, 'הפועל ירושלים': {'overall': 4.0, 'attack': 4.0, 'defend': 3.0}, 'בני סכנין': {'overall': 2.0, 'attack': 3.0, 'defend': 2.0}, 'מכבי חיפה': {'overall': 5.0, 'attack': 5.0, 'defend': 5.0}, 'מכבי בני ריינה': {'overall': 1.0, 'attack': 2.0, 'defend': 2.0},
             'מכבי תל אביב': {'overall': 5.0, 'attack': 5.0, 'defend': 5.0}, 'בית"ר ירושלים': {'overall': 4.0, 'attack': 4.0, 'defend': 3.0}, 'מ.ס. אשדוד': {'overall': 2.0, 'attack': 3.0, 'defend': 1.0}, 'הפועל חדרה': {'overall': 1.0, 'attack': 1.0, 'defend': 2.0}, 'הפועל תל אביב': {'overall': 3.0, 'attack': 3.0, 'defend': 3.0}, 'הפועל פתח תקווה': {'overall': 1.0, 'attack': 1.0, 'defend': 3.0}, 'הפועל באר שבע': {'overall': 4.0, 'attack': 4.0, 'defend': 4.0}}
    insert_all_teams(teams)
    insert_all_players(total_players)
    insert_all_fixtures(total_players)
    insert_all_events(total_players)
    print(len(db.get_all_players()))


def update_player_data(players_data):
    # Iterate through the player data and update the database
    for position in players_data:
        for player_info in position:
            name = player_info["name"]
            team = player_info['team']
            points = player_info["points"]
            injury = player_info["injury"]

            # Update player information in the database
            updated = db.update_player(name, team, points, injury)
            if updated:
                print(f"Updated player {name}'s information.")
            else:
                print(f"Player {name} not found in the database.")
                name = player_info["name"]
                position = player_info["position"]
                team = player_info["team"]
                price = player_info["price"]
                points = player_info["points"]
                db.insert_player(name, position, team, price, points, injury)
                print("Added player" + name)


def get_fixture_players(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        players_data = json.load(json_file)
    players = players_data.values()
    return players


def update_DB():
    fixture_name = "fixture5"
    json_file_path = f"data/all_players_data_{fixture_name}.json"
    print("Updating DB:")
    total_players = get_fixture_players(json_file_path)
    update_player_data(total_players)
    insert_all_fixtures(total_players)
    insert_all_events_by_fixture(total_players, fixture_name)


update_DB()
# players = get_fixture_players("data/all_players_data_fixture5.json")
# print(len(players))
