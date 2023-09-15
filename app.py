import streamlit as st
import pandas as pd
from player_data_analyzer import PlayersDataAnalyzer
from data_utility import DataUtility

data_utility = DataUtility()

def sort_players(player_data, sort_option):
    if sort_option == 'name':
        return sorted(player_data, key=lambda x: x['name'])
    elif sort_option == 'position':
        return sorted(player_data, key=lambda x: x['position'])
    elif sort_option == 'team':
        return sorted(player_data, key=lambda x: x['team'])
    elif sort_option == 'price':
        return sorted(player_data, key=lambda x: x['price'], reverse=True)
    elif sort_option == 'points':
        return sorted(player_data, key=lambda x: x['points'], reverse=True)
    else:
        return player_data


# Create an instance of PlayersDataAnalyzer
json_file_path = 'all_players_data.json'
analyzer = PlayersDataAnalyzer(json_file_path)

# Streamlit app
st.title('Israel Dream League')

# Sidebar with options
option = st.sidebar.selectbox('Select an option:', [
    'Total Players', 'Random Team', 'Best Team'
])

if option == 'Total Players':
    st.sidebar.header('Options')
    type_option = st.sidebar.selectbox('Type by:', ['Minimum', 'Equal'])

    # Get player data from the Analyzer class based on type_option
    if type_option == 'Minimum':
        points_input = st.sidebar.number_input(
            'Filter by Minimum Points:', min_value=0, step=1)
        price_input_min = st.sidebar.number_input(
            'Filter by Minimum Price:', min_value=3, max_value=15, step=1)
        price_input_max = st.sidebar.number_input(
            'Filter by Maximum Price:', min_value=3, max_value=15, step=1, value=15)
        player_data = analyzer.get_total_players(
            points_input, price_input_min, price_input_max, True)
    else:
        points_input = st.sidebar.number_input(
            'Filter by Equal Points:', min_value=0, step=1)
        price_input_min = st.sidebar.number_input(
            'Filter by Minimum Price:', min_value=3, max_value=15, step=1)
        price_input_max = st.sidebar.number_input(
            'Filter by Maximum Price:', min_value=3, max_value=15, step=1, value=15)
        player_data = analyzer.get_total_players(
            points_input, price_input_min, price_input_max, False)

    sort_option = st.sidebar.selectbox(
        'Sort by:', ['points', 'position', 'team', 'price', 'name'])

    # Create checkboxes for positions
    selected_positions = st.sidebar.multiselect(
        'Select Positions:', ['GK', 'CB', 'MD', 'FW'], default=['GK', 'CB', 'MD', 'FW'])

    selected_teams = st.sidebar.multiselect(
        'Select Teams:', data_utility.full_team_name_list, default = data_utility.full_team_name_list)

    # Filter player data based on selected positions and teams
    filtered_data = [
        player for player in player_data if player['position'] in selected_positions and player['team'] in selected_teams]

    num_players_to_display = len(filtered_data)
    print(num_players_to_display)

    col1, col2, col3 = st.sidebar.columns(3)

    # Check if the "Top 10" button is clicked
    if col1.button('Top 10') and len(filtered_data) >= 10:
        num_players_to_display = 10

    # Check if the "Top 50" button is clicked
    if col2.button('Top 50') and len(filtered_data) >= 50:
        num_players_to_display = 50

    # Check if the "Top 100" button is clicked
    if col3.button('Top 100') and len(filtered_data) >= 100:
        num_players_to_display = 100

    # Check if there are players to display
    if num_players_to_display > 0:
        # Create the slider for the number of players to display
        num_players_to_display = st.sidebar.slider(
            'Number of Players to Display', min_value=1, max_value=len(filtered_data), value=num_players_to_display, step=1)

        # Sort player data based on user selection
        sorted_data = sort_players(filtered_data, sort_option)

        # Display the filtered and sorted data in a table
        if type_option == 'Minimum':
            st.write(
                f'Total Players with {points_input} Points or more in selected positions and teams: {len(sorted_data)}')
        else:
            st.write(
                f'Total Players with {points_input} Points in selected positions and teams: {len(sorted_data)}')

        # Limit the displayed data based on the user's selection
        num_players_to_display = min(num_players_to_display, len(sorted_data))
        df = pd.DataFrame(sorted_data[:num_players_to_display])
        df.index = range(1, len(df) + 1)
        st.table(df[['name', 'position', 'team', 'price', 'points']])
    else:
        st.write("No players match the selected criteria.")


elif option == 'Random Team':
    st.write('Random Team:')
    total_points = 0
    total_budget = 0
    if st.button('Generate New Random Team'):
        random_team, budget = analyzer.build_random_team()
        for position in random_team:
            df = pd.DataFrame(random_team[position])
            df.index = range(1, len(df) + 1)
            st.table(df[['name', 'position', 'team', 'price', 'points']])
            total_points += df['points'].sum()
        st.write(
            f'remaining Budget is {budget}M and Total points:{total_points}')

elif option == 'Best Team':
    st.write('Best Team:')

    best_team, total_points, total_cost = analyzer.find_best_team_lp()

    # Create a list to store player data in the best team
    best_team_data = []

    for player in best_team:
        best_team_data.append(player)  # Append player data to the list

    # Create a DataFrame with all players in the best team
    df = pd.DataFrame(best_team_data)

    # Define the order of positions for sorting
    position_order = ['GK', 'CB', 'MD', 'FW']

    # Sort the DataFrame by position
    df['position'] = pd.Categorical(
        df['position'], categories=position_order, ordered=True)
    df = df.sort_values(by='position')

    df = df.reset_index(drop=True)
    df.index = range(1, len(df) + 1)

    st.table(df[['name', 'position', 'team', 'price', 'points']])

    st.write(
        f'Total Cost is {total_cost}M and Total Points: {total_points}')


# To run the Streamlit app, use the following command:
# streamlit run your_app_name.py
