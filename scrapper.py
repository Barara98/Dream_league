import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


# Initialize ChromeOptions
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument('--headless')  # Add this line if you want to run in headless mode (without a visible browser window)
# Replace with the actual path to your Chrome binary if needed
chrome_options.binary_location = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)

# Create the WebDriver instance
driver = webdriver.Chrome(options=chrome_options)

try:
    # Now you can navigate to a webpage and interact with it using driver
    driver.get("https://dreamteam.sport5.co.il/my-team")

    # Find the anchor element with href="/login" by its XPath
    login_link = driver.find_element(By.XPATH, '//a[contains(@href, "/login")]')

    # Click the login link
    login_link.click()

    # Sleep for a few seconds to allow the page to load
    time.sleep(2)

    # Find the "כניסה באמצעות אימייל" (Login with Email) button by its text
    login_with_email_button = driver.find_element(
        By.XPATH, '//button[contains(text(), "כניסה באמצעות אימייל")]'
    )

    # Click the "כניסה באמצעות אימייל" button
    login_with_email_button.click()

    # Sleep for a few seconds to allow the login page to load
    time.sleep(1)

    # Find the email and password input fields by their names and enter your credentials
    email_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")

    # Enter your email and password
    email_input.send_keys(os.environ.get("USERNAME"))
    password_input.send_keys(os.environ.get("PASSWORD"))

    # Find the "התחבר" (Login) button by its text and click it
    login_button = driver.find_element(By.XPATH, '//button[contains(text(), "התחבר")]')
    login_button.click()

    # Sleep for a few seconds to allow the login process to complete
    time.sleep(3)

    # Find the "הוסף שחקן" (Add Player) button by its class name
    add_player_button = driver.find_element(By.CLASS_NAME, "btn-add")

    # Click the "הוסף שחקן" button
    add_player_button.click()

    # Sleep for a few seconds to allow the page to load
    time.sleep(0.5)

    # Find the "הכל" (All) button by its label text
    all_button = driver.find_element(By.XPATH, '//label[contains(text(), "הכל")]')

    # Click the "הכל" button
    all_button.click()

    modal = driver.find_element(By.CLASS_NAME, "modal-dialog-scrollable")

    # Find the table within the modal by its class name
    modal_table = modal.find_element(By.CLASS_NAME, "table")

    # Get all the rows in the table
    rows = modal_table.find_elements(By.TAG_NAME, "tr")
    print(len(rows))

    # Iterate through each row and extract player information
    for row in rows[150:152]:  # Skip the header row
        buttons = row.find_elements(By.TAG_NAME, "button")

        # Click the first button in the row
        if buttons:
            buttons[0].click()

        # Sleep for a few seconds to allow the modal to open
        time.sleep(0.6)

        modals = driver.find_elements(By.CLASS_NAME, "modal-dialog-scrollable")

        # Get the HTML content of the modal body
        modal_body_html = modals[1].get_attribute("outerHTML")

        # Save the modal body HTML to a file with a unique name (e.g., player1.html, player2.html, etc.)
        player_index = rows.index(row)  # Get the index of the player's row
        print(player_index)
        player_dir = f"players_fixture5/Player{player_index}"

        if not os.path.exists(player_dir):
            os.makedirs(player_dir)

        filename = f"{player_dir}/profile.html"

        with open(filename, "w", encoding="utf-8") as file:
            file.write(modal_body_html)

        try:
            table = modals[1].find_element(By.TAG_NAME, "table")
        except NoSuchElementException:
            # Handle the case when the table is not found, for example, by printing an error message
            print("Table not found in modal.")
            close_button = modals[1].find_element(By.CLASS_NAME, "btn-close")
            close_button.click()
            continue
        if table:
            rows_stats = table.find_elements(By.TAG_NAME, "tr")
            for row in rows_stats:
                fixture_text = row.find_elements(By.TAG_NAME, "td")[0].text
                if fixture_text == "מחזור 5":
                    fixture_number = (
                        re.search(r"\d+", fixture_text).group()
                        if re.search(r"\d+", fixture_text)
                        else None
                    )
                    fixture_dir = os.path.join(player_dir, "fixture")
                    if not os.path.exists(fixture_dir):
                        os.makedirs(fixture_dir)

                    button_in_table = row.find_element(By.TAG_NAME, "button")
                    button_in_table.click()
                    time.sleep(1)
                    table_stats = table.find_elements(
                        By.CSS_SELECTOR, "tr.bg-white.bg-opacity-10"
                    )

                    # Define the filename for the fixture HTML file
                    fixture_filename = os.path.join(
                        fixture_dir, f"fixture{fixture_number}.html"
                    )

                    # Create an HTML string to represent the table with all 'tr' elements
                    table_stats_html = "<table>"
                    for table_stat in table_stats:
                        table_stats_html += table_stat.get_attribute("outerHTML")
                    table_stats_html += "</table>"

                    # Write the table stats HTML to the fixture HTML file
                    with open(fixture_filename, "w", encoding="utf-8") as fixture_file:
                        fixture_file.write(table_stats_html)

                    button_in_table.click()
                    time.sleep(0.5)

        # Find and click the close button for the modal
        close_button = modals[1].find_element(By.CLASS_NAME, "btn-close")
        close_button.click()

finally:
    driver.quit()
