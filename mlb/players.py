from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Proxy configuration
PROXY = "127.0.0.1:24000"
# Path to chromedriver executable
PATH = "/opt/homebrew/Caskroom/chromedriver/121.0.6167.85/chromedriver-mac-arm64/chromedriver"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=%s' % PROXY)

# Initialize Chrome WebDriver with the specified path and options
service = Service(PATH)

timeout = 25
teams = ["dbacks", "braves", "orioles", "redsox", "cubs", "whitesox", "reds", "guardians", "rockies", "tigers", "astros", "royals", "angels", "dodgers", "marlins", "brewers", "twins", "mets", "yankees", "athletics", "phillies", "rays", "rangers", "bluejays", "rangers", "nationals"]
teams = ["dbacks"]

players = []
position = ''

# Setting up WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

for team in teams:
    # Accessing the URL
    url = f"https://www.mlb.com/{team}/roster"
    driver.get(url)

    # Getting the page source
    src = driver.page_source
    parser = BeautifulSoup(src, "lxml")

    # Finding the table containing players
    table = parser.find("div", attrs = {"class": "players"})

    # Getting all 'tr' elements, excluding the first one 
    rows = table.findAll('tr')
    
    # Extracting player information
    for row in rows:
        players_position = row.find('td', attrs = {"colspan": '2'})
        if players_position:
            position = players_position.get_text()
            position = position[:len(position)-1]

        player_info = []
        for a in row.find_all('a'):
            name = a.getText().strip()
            id = a.attrs.get('href', 'Not found').split("/")[-1]

            player_info.append(team)
            player_info.append(name)
            
            if len(id.split("-")) > 1:
                player_info.append(id)
            else:    
                name_and_id = name.lower() + " " + id
                player_info.append("-".join(name_and_id.split()))

            player_info.append(position)
        
        if player_info !=  []:
            players.append(player_info)

print(players)

driver.quit()