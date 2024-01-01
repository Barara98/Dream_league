import sqlite3


class PlayerDataDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        # Create Teams table
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Teams (
            team_name VARCHAR(255) PRIMARY KEY,
            overall FLOAT,
            attack FLOAT,
            defend FLOAT
        )
        """
        )

        # Create Players table
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Players (
            name VARCHAR(255) PRIMARY KEY,
            position VARCHAR(50),
            team_name VARCHAR(255),
            price DECIMAL(5,2),
            points INTEGER,
            stars INTEGER,
            injury BOOLEAN,
            FOREIGN KEY (team_name) REFERENCES Teams (team_name)
        )
        """
        )

        # Create Fixtures table
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Fixtures (
            fixture_id INTEGER PRIMARY KEY,
            player_name VARCHAR(255),
            fixture_name VARCHAR(50),
            fixture_points INTEGER,
            team_name VARCHAR(255),
            FOREIGN KEY (player_name) REFERENCES Players (name),
            FOREIGN KEY (team_name) REFERENCES Teams (team_name)

        )
        """
        )

        # Create Events table
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Events (
            event_id INTEGER PRIMARY KEY,
            fixture_id INTEGER,
            event_name VARCHAR(50),
            event_quantity INTEGER,
            event_points INTEGER,
            FOREIGN KEY (fixture_id) REFERENCES Fixtures (fixture_id)
        )
        """
        )

        self.conn.commit()

    def insert_team(self, team_name, overall, attack, defend):
        # Check if the team already exists in the database
        existing_team = self.get_team_by_name(team_name)

        if existing_team is None:
            # Team does not exist, so insert it into the database
            self.cursor.execute(
                """
                INSERT INTO Teams (team_name, overall, attack, defend)
                VALUES (?, ?, ?, ?)
                """,
                (team_name, overall, attack, defend),
            )
            self.conn.commit()
            return self.cursor.lastrowid
        else:
            # Team already exists, do not insert again
            return None

    def insert_player(self, name, position, team, price, points, injury=False):
        # Check if the player already exists in the database
        existing_player = self.get_player_by_name(name)

        if existing_player is None:
            # Player does not exist, so insert them into the database
            self.cursor.execute(
                """
                INSERT INTO Players (name, position, team_name, price, points, stars, injury)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, position, team, price, points, 0, injury),
            )
            self.conn.commit()
            return self.cursor.lastrowid
        else:
            # Player already exists, do not insert again
            return None

    def insert_fixture(self, player_name, fixture_name, fixture_points, team):
        # Check if the fixture already exists for the player
        self.cursor.execute(
            """
            SELECT fixture_id
            FROM Fixtures
            WHERE player_name=? AND fixture_name=?
            """,
            (player_name, fixture_name),
        )
        existing_fixture = self.cursor.fetchone()

        if not existing_fixture:
            # The fixture does not exist, so insert it
            self.cursor.execute(
                """
                INSERT INTO Fixtures (player_name, fixture_name, fixture_points, team_name)
                VALUES (?, ?, ?, ?)
                """,
                (player_name, fixture_name, fixture_points, team),
            )
            self.conn.commit()
            return self.cursor.lastrowid
        else:
            # The fixture already exists, so return its ID
            return existing_fixture[0]

    def insert_event(self, fixture_id, event_name, event_quantity, event_points):
        # Check if the event already exists for the fixture
        existing_event = self.get_event_by_fixture_and_name(
            fixture_id, event_name)

        if not existing_event:
            # Event does not exist, insert it
            self.cursor.execute(
                """
                INSERT INTO Events (fixture_id, event_name, event_quantity, event_points)
                VALUES (?, ?, ?, ?)
                """,
                (fixture_id, event_name, event_quantity, event_points),
            )
            self.conn.commit()
            return self.cursor.lastrowid
        else:
            # Event already exists, do nothing
            return None

    def get_player_by_name(self, name):
        self.cursor.execute("SELECT * FROM Players WHERE name=?", (name,))
        result = self.cursor.fetchone()
        if result is not None:
            player_dict = {
                "name": result[0],
                "position": result[1],
                "team": result[2],
                "price": result[3],
                "points": result[4],
                "stars": result[5],
            }
            return player_dict
        else:
            return None

    def get_fixtures_by_player_name(self, name):
        self.cursor.execute(
            """
            SELECT Fixtures.fixture_id, Fixtures.fixture_name, Fixtures.fixture_points
            FROM Players
            INNER JOIN Fixtures ON Players.name = Fixtures.player_name
            WHERE Players.name=?
        """,
            (name,),
        )
        results = self.cursor.fetchall()
        fixtures_list = []
        for row in results:
            fixture_dict = {
                "fixture_id": row[0],
                "fixture_name": row[1],
                "fixture_points": row[2],
            }
            fixtures_list.append(fixture_dict)
        return fixtures_list

    def get_events_by_fixture_id(self, fixture_id):
        self.cursor.execute(
            """
        SELECT Events.event_name, Events.event_quantity, Events.event_points
        FROM Events
        WHERE Events.fixture_id=?
        """,
            (fixture_id,),
        )
        result = self.cursor.fetchone()
        if result is not None:
            event_dict = {
                "event_id": result[0],
                "fixture_id": result[1],
                "event_name": result[2],
                "event_quantity": result[3],
                "event_points": result[4],
            }
            return event_dict
        else:
            return None

    def get_event_by_fixture_and_name(self, fixture_id, event_name):
        self.cursor.execute(
            """
            SELECT * FROM Events
            WHERE fixture_id=? AND event_name=?
            """,
            (fixture_id, event_name),
        )
        result = self.cursor.fetchone()
        if result is not None:
            event_dict = {
                "event_id": result[0],
                "fixture_id": result[1],
                "event_name": result[2],
                "event_quantity": result[3],
                "event_points": result[4],
            }
            return event_dict
        else:
            return None

    def get_all_players(self):
        self.cursor.execute("SELECT * FROM Players")
        results = self.cursor.fetchall()
        player_list = []
        for result in results:
            player_dict = {
                "name": result[0],
                "position": result[1],
                "team": result[2],
                "price": result[3],
                "points": result[4],
                "stars": result[5],
            }
            player_list.append(player_dict)
        return player_list

    def get_players_min_points(self, points):
        self.cursor.execute("SELECT * FROM Players")
        results = self.cursor.fetchall()
        player_list = []
        for result in results:
            player_dict = {
                "name": result[0],
                "position": result[1],
                "team": result[2],
                "price": result[3],
                "points": result[4],
                "stars": result[5],
            }
            if player_dict["points"] > points:
                player_list.append(player_dict)
        return player_list

    def get_players_by_fixture(self, fixture_name):
        self.cursor.execute(
            """
            SELECT Players.name, Players.position, Players.team_name, Players.price, Fixtures.fixture_points, Players.stars
            FROM Players
            INNER JOIN Fixtures ON Players.name = Fixtures.player_name
            WHERE Fixtures.fixture_name = ?
            """,
            (fixture_name,),
        )
        results = self.cursor.fetchall()
        player_list = []
        for result in results:
            player_dict = {
                "name": result[0],
                "position": result[1],
                "team": result[2],
                "price": result[3],
                "points": result[4],
                "stars": result[5],
            }
            player_list.append(player_dict)
        return player_list

    def get_all_players_with_points(self, fixtures_list):
        self.cursor.execute("SELECT * FROM Players")
        results = self.cursor.fetchall()
        players_list = []

        for result in results:
            player_dict = {
                "name": result[0],
                "position": result[1],
                "team": result[2],
                # Convert price to float if it's stored as DECIMAL
                "price": int(result[3]),
                "points": {},
            }

            # Get fixture-specific points for the player
            existing_fixtures = self.get_fixtures_by_player_name(
                player_dict["name"])
            existing_fixture_names = {
                fixture["fixture_name"]: fixture for fixture in existing_fixtures}

            for fixture_name in fixtures_list:
                if fixture_name not in existing_fixture_names:
                    # Fixture is missing for the player, add it with 0 points
                    player_dict["points"][fixture_name] = 0
                else:
                    # Fixture exists for the player, retrieve its points
                    fixture_data = existing_fixture_names[fixture_name]
                    fixture_points = fixture_data["fixture_points"]
                    player_dict["points"][fixture_name] = fixture_points

            players_list.append(player_dict)

        return players_list

    def get_all_players_with_total_events(self, events_list):
        all_players = self.get_all_players()
        players_with_events = []

        for player_info in all_players:
            player_name = player_info['name']
            player_points = player_info['points']

            # Initialize a dictionary with the player's name
            player_data = {'name': player_name}

            # Get the list of fixtures for the player
            fixtures_list = self.get_fixtures_by_player_name(player_name)
            game_played = len(fixtures_list)

            # Initialize a dictionary to store the total event quantities
            total_event_quantities = {}

            # Iterate through the fixtures and accumulate event quantities
            for fixture in fixtures_list:
                fixture_id = fixture['fixture_id']

                for event in events_list:
                    # If the event exists in the database, add its quantity to the total_event_quantities
                    event_data = self.get_event_by_fixture_and_name(
                        fixture_id, event)
                    if event_data is not None:
                        total_event_quantities[event] = total_event_quantities.get(
                            event, 0) + event_data['event_quantity']

            # Add the player's total event quantities to the player_data dictionary
            for event, total_quantity in total_event_quantities.items():
                player_data[event] = total_quantity

            # Add the player's price to the player_data
            player_data['Price'] = player_info['price']
            player_data['game_played'] = game_played
            player_data['points'] = player_points
            player_data['team'] = player_info['team']

            players_with_events.append(player_data)

        return players_with_events

    def get_all_teams(self):
        self.cursor.execute("SELECT * FROM Teams")
        results = self.cursor.fetchall()
        team_list = []
        for result in results:
            team_dict = {
                "name": result[0],
                "overall": result[1],
                "attack": result[2],
                "defend": result[3],
            }
            team_list.append(team_dict)
        return team_list

    def get_team_by_name(self, team_name):
        self.cursor.execute(
            """
            SELECT * FROM Teams
            WHERE team_name=?
            """,
            (team_name,),
        )
        result = self.cursor.fetchone()
        if result is not None:
            team_dict = {
                "team_name": result[0],
                "overall": result[1],
                "attack": result[2],
                "defend": result[3],
            }
            return team_dict
        else:
            return None

    def get_defenders_by_team_name(self, team_name):
        self.cursor.execute(
            """
            SELECT * FROM Players
            WHERE team_name=? AND (position='CB' OR position='GK') AND injury = 0
            """,
            (team_name,),
        )
        results = self.cursor.fetchall()
        defenders_list = []
        for result in results:
            defender_dict = {
                "name": result[0],
                "position": result[1],
                "team": result[2],
                "price": result[3],
                "points": result[4],
                "stars": result[5],
            }
            defenders_list.append(defender_dict)
        return defenders_list

    def get_attackers_by_team_name(self, team_name):
        self.cursor.execute(
            """
            SELECT * FROM Players
            WHERE team_name=? AND (position='MD' OR position='FW') AND injury = 0
            """,
            (team_name,),
        )
        results = self.cursor.fetchall()
        attackers_list = []
        for result in results:
            attacker_dict = {
                "name": result[0],
                "position": result[1],
                "team": result[2],
                "price": result[3],
                "points": result[4],
                "stars": result[5],
            }
            attackers_list.append(attacker_dict)
        return attackers_list

    def update_player(self, name, team, points, injury):
        # Check if the player exists in the database
        existing_player = self.get_player_by_name(name)

        if existing_player is not None:
            # Player exists, update their points and injury status
            self.cursor.execute(
                """
                UPDATE Players
                SET points = ?,
                    team_name = ?,
                    injury = ?
                WHERE name = ?
                """,
                (points, team, injury, name),
            )
            self.conn.commit()
            return True  # Return True to indicate successful update
        else:
            # Player does not exist, return False to indicate failure
            return False

    def update_player_stars(self, player_scores):
        for player_name, player_data in player_scores.items():
            # Default to 1 star if not provided
            rating = player_data.get("Rating", 1)
            # Update the star rating for the player in the database
            self.cursor.execute(
                """
                UPDATE Players
                SET stars = ?
                WHERE name = ?
                """,
                (rating, player_name),
            )
            self.conn.commit()

    def close(self):
        self.conn.close()
