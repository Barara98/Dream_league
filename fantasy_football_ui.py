import tkinter as tk
from tkinter import ttk

from player_data_analyzer import PlayersDataAnalyzer


class PlayersDataAnalyzerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fantasy Football Team Analyzer")

        # Create and configure the main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Create widgets
        # Replace with your actual fixture options
        self.fixture_options = ["All", "fixture1",
                                "fixture2", "fixture3", "fixture4", "fixture5"]
        self.fixture_label = ttk.Label(self.main_frame, text="Fixture:")
        self.fixture_combobox = ttk.Combobox(
            self.main_frame, values=self.fixture_options)
        self.fixture_combobox.set("All")
        self.analyze_button = ttk.Button(
            self.main_frame, text="Find best Team", command=self.analyze_team)
        self.result_text = tk.Text(
            self.main_frame, wrap=tk.WORD, height=15, width=60)

        # Grid layout
        self.fixture_label.grid(row=0, column=0, sticky=tk.W)
        self.fixture_combobox.grid(row=0, column=1, sticky=(
            tk.W, tk.E))  # Fix the reference here
        self.analyze_button.grid(row=1, column=0, columnspan=2, pady=10)
        self.result_text.grid(row=2, column=0, columnspan=2)

    def analyze_team(self):
        fixture = self.fixture_combobox.get()  # Fix the reference here
        team, total_points, total_cost = analyzer.find_best_team(fixture)
        self.display_team(team, total_points, total_cost)

    def display_team(self, team, total_points, total_cost):
        self.result_text.delete(1.0, tk.END)  # Clear previous text
        for player in team:
            player_info = f"{player['name']} ({player['position']}) - {player['team']} - Price: {player['price']} - Points: {player['points']}\n"
            self.result_text.insert(tk.END, player_info)
        self.result_text.insert(tk.END, f"Total Points: {total_points}\n")
        self.result_text.insert(tk.END, f"Total Cost: {total_cost}")


if __name__ == "__main__":
    root = tk.Tk()
    analyzer = PlayersDataAnalyzer("player_data.db")
    app = PlayersDataAnalyzerUI(root)
    root.mainloop()
