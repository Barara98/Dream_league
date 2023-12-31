import tkinter as tk
from tkinter import ttk, filedialog
from player_data_analyzer import PlayersDataAnalyzer
from players_data_extract import process_player_folders


class MainPage(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.analyzer = PlayersDataAnalyzer("player_data.db")

        # Create and configure the notebook
        self.notebook = ttk.Notebook(self)
        self.page_analyze = AnalyzePage(self.notebook, controller=self)
        self.page_update = UpdatePage(self.notebook, controller=self)
        self.page_database = DatabasePage(self.notebook, controller=self)

        # Add pages to the notebook
        self.notebook.add(self.page_analyze, text="Analyze Team")
        self.notebook.add(self.page_update, text="Update Data")
        self.notebook.add(self.page_database, text="Database")

        # Pack the notebook
        self.notebook.pack(expand=True, fill="both")


class AnalyzePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Create widgets for the Analyze page
        self.fixture_options = ["All", "fixture1",
                                "fixture2", "fixture3", "fixture4", "fixture5"]
        self.fixture_label = ttk.Label(self, text="Fixture:")
        self.fixture_combobox = ttk.Combobox(self, values=self.fixture_options)
        self.fixture_combobox.set("All")
        self.analyze_button = ttk.Button(
            self, text="Find Best Team", command=self.analyze_team)
        self.result_text = tk.Text(self, wrap=tk.WORD, height=15, width=60)

        # Grid layout
        self.fixture_label.grid(row=0, column=0, sticky=tk.W)
        self.fixture_combobox.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.analyze_button.grid(row=1, column=0, columnspan=2, pady=10)
        self.result_text.grid(row=2, column=0, columnspan=2)

    def analyze_team(self):
        fixture = self.fixture_combobox.get()
        team, total_points, total_cost = self.controller.analyzer.find_best_team(
            fixture)
        self.display_team(team, total_points, total_cost)

    def display_team(self, team, total_points, total_cost):
        self.result_text.delete(1.0, tk.END)  # Clear previous text
        for player in team:
            player_info = f"{player['name']} ({player['position']}) - {player['team']} - Price: {player['price']} - Points: {player['points']}\n"
            self.result_text.insert(tk.END, player_info)
        self.result_text.insert(tk.END, f"Total Points: {total_points}\n")
        self.result_text.insert(tk.END, f"Total Cost: {total_cost}")


class UpdatePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Create widgets for the Update page
        self.process_data_button = ttk.Button(
            self, text="Process Player Data", command=self.process_player_data)

        # Grid layout
        self.process_data_button.grid(row=0, column=0, pady=10)

    def process_player_data(self):
        root_directory = filedialog.askdirectory(
            title="Select Root Directory for Player Data")
        if root_directory:
            process_player_folders(root_directory)
            print("Player data processed successfully.")
        else:
            print("Please select a root directory for player data.")


class DatabasePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Create a notebook for different tabs
        self.notebook = ttk.Notebook(self)

        # Create tabs
        self.total_tab = ttk.Frame(self.notebook)
        self.by_fixture_tab = ttk.Frame(self.notebook)
        self.teams_tab = ttk.Frame(self.notebook)

        # Add tabs to the notebook
        self.notebook.add(self.total_tab, text="Total")
        self.notebook.add(self.by_fixture_tab, text="By Fixture")
        self.notebook.add(self.teams_tab, text="Teams")

        # Create widgets for each tab
        self.create_total_tab()
        self.create_by_fixture_tab()
        self.create_teams_tab()

        # Grid layout
        self.notebook.grid(row=3, column=0, pady=5)

    def top25_table(self, fixture="All"):
        # Determine the target tab based on the fixture value
        target_tab = self.total_tab if fixture == "All" else self.by_fixture_tab

        top_players_label = ttk.Label(target_tab, text="Top 25 Players:")
        top_players_label.pack(expand=True, fill="both")

        # Create a Treeview widget
        tree = ttk.Treeview(target_tab, columns=(
            "Rank", "Name", "Position", "Team", "Price", "Points", "Stars"))

        # Set the column headings and adjust widths
        tree.heading("Rank", text="Rank", anchor="e")
        tree.heading("Name", text="שם", anchor="e")
        tree.heading("Position", text="תפקיד", anchor="e")
        tree.heading("Team", text="קבוצה", anchor="e")
        tree.heading("Price", text="מחיר", anchor="e")
        tree.heading("Points", text="נקודות", anchor="e")
        tree.heading("Stars", text="כוכבים", anchor="e")

        # Adjust column widths
        tree.column("Rank", width=50, anchor="e")
        tree.column("Name", width=150, anchor="e")
        tree.column("Position", width=100, anchor="e")
        tree.column("Team", width=100, anchor="e")
        tree.column("Price", width=75, anchor="e")
        tree.column("Points", width=75, anchor="e")
        tree.column("Stars", width=75, anchor="e")

        # Create a Combobox for selecting the sorting key
        sorting_label = ttk.Label(target_tab, text="Sort by:")
        sorting_combobox = ttk.Combobox(target_tab, values=[
            "name", "position", "team", "price", "points", "stars"])
        sorting_combobox.set("points")  # Set default sorting by Points

        # Create a button to apply sorting
        sort_button = ttk.Button(
            target_tab, text="Sort", command=lambda: self.sort_players(tree, sorting_combobox.get(), fixture))

        # Pack the sorting widgets
        sorting_label.pack(side="top")
        sorting_combobox.pack(side="top")
        sort_button.pack(side="top")

        # Pack the Treeview
        tree.pack(expand=True, fill="both")

    def create_total_tab(self):
        # Create widgets for the Total tab
        self.top25_table()

    def sort_players(self, tree, key, fixture):
        # Get top 25 players by points
        if fixture == "All":
            top_players = self.controller.analyzer.db.get_all_players()
        else:
            top_players = self.controller.analyzer.db.get_players_by_fixture(
                fixture)
        top_players.sort(
            key=lambda player: player[key] if key != "Rank" else player["points"], reverse=True)

        # Clear the Treeview
        tree.delete(*tree.get_children())

        # Insert data into the Treeview
        for rank, player_data in enumerate(top_players[:25], start=1):
            tree.insert("", "end", values=(rank, player_data['name'], player_data['position'],
                        player_data['team'], player_data['price'], player_data['points'], player_data['stars']))

    def create_by_fixture_tab(self):
        # Create a Combobox for selecting the fixture
        fixture_label = ttk.Label(self.by_fixture_tab, text="Select Fixture:")
        fixture_combobox = ttk.Combobox(self.by_fixture_tab, values=[
            "fixture1", "fixture2", "fixture3", "fixture4", "fixture5"])
        fixture_combobox.set("fixture1")  # Set default fixture

        # Create a button to display top 25 players for the selected fixture
        display_button = ttk.Button(
            self.by_fixture_tab, text="Display Top 25", command=lambda: self.top25_table(fixture_combobox.get()))

        # Pack the Combobox and button
        fixture_label.pack(side="top")
        fixture_combobox.pack(side="top")
        display_button.pack(side="top")

    def create_teams_tab(self):
        # Create widgets for the Teams tab
        label = ttk.Label(self.teams_tab, text="Teams logic goes here.")
        label.pack(expand=True, fill="both")

    def display_result_text(self, text):
        # Display text in the currently selected tab
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab == "Total":
            self.total_tab.winfo_children()[0].config(text=text)
        elif current_tab == "By Fixture":
            self.by_fixture_tab.winfo_children()[0].config(text=text)
        elif current_tab == "Teams":
            self.teams_tab.winfo_children()[0].config(text=text)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fantasy Football Team Analyzer")
    app = MainPage(root)
    app.pack(expand=True, fill="both")
    root.mainloop()
