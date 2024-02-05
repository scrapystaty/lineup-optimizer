# from players import players

import requests
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd


payload = {}
headers = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
  'Accept': '*/*',
  'Accept-Language': 'en-US,en;q=0.5',
  'Accept-Encoding': 'gzip, deflate, br',
  'X-Requested-With': 'XMLHttpRequest',
  'Connection': 'keep-alive',
  'Referer': 'https://baseballsavant.mlb.com/savant-player/alek-thomas-677950?stats=statcast-r-hitting-mlb',
  'Cookie': '__cflb=02DiuJFcgbX2zpcHdRurfpjkBTD5BPySo6gPFqPfkQ556; AMCV_A65F776A5245B01B0A490D44%40AdobeOrg=1099438348%7CMCIDTS%7C19755%7CMCMID%7C08223760795725670020171971273569729942%7CMCAAMLH-1707411436%7C7%7CMCAAMB-1707411436%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1706813836s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-19762%7CvVersion%7C2.1.0; s_cc=true; s_sq=%5B%5BB%5D%5D; AMCVS_A65F776A5245B01B0A490D44%40AdobeOrg=1; s_vi=[CS]v1|32DDE6B6150B13BF-40000A6BE1F97D36[CE]; s_ecid=MCMID%7C08223760795725670020171971273569729942; _dd_s=rum=0&expire=1706807948264',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'TE': 'trailers'
}

handedness =['R', 'L']
pitcher_headerlist = []
hitter_headerlist = []
player_stats = []
pitcher_stats = []
players = [['dbacks', 'Brandon Pfaadt', 'brandon-pfaadt-694297', 'Pitcher']]

for player in players:
    if player[-1] != "Pitcher":    
        for hand in handedness:
            url = f"https://baseballsavant.mlb.com/player-services/statcast-pitches-breakdown?playerId={player[2].split('-')[-1]}&position=8&hand={hand}&pitchBreakdown=pitches&timeFrame=yearly&season=&pitchType=&count=&updatePitches=true"

            r = requests.get(url, headers=headers)

            parser = BeautifulSoup(r.content, "html.parser")
            table = parser.find(id="detailedPitches")

            headersTH = table.find_all('th')
            hitter_headerlist = [h.text.strip() for h in headersTH[:]]
            hitter_headerlist.insert(0, "Name")
            hitter_headerlist.insert(2, "Team")
            hitter_headerlist.insert(3, "Hand") 
    
            rows = table.findAll('tr')[1:]
    
            for i in range(len(rows)):
                row_cells = []
                for td in rows[i].findAll('td'):
                    row_cells.append(td.getText().strip())
                row_cells.insert(0, player[1])
                row_cells.insert(2, player[0])
                row_cells.insert(3, hand)
                player_stats.append(row_cells)
    else:
        # Proxy configuration
        PROXY = "127.0.0.1:24000"
        # Path to chromedriver executable
        PATH = "/opt/homebrew/Caskroom/chromedriver/121.0.6167.85/chromedriver-mac-arm64/chromedriver"

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % PROXY)

        timeout = 25

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        for player in players:
            url = f"https://baseballsavant.mlb.com/savant-player/{player[2]}?stats=statcast-r-pitching-mlb"
            driver.get(url)

            detailedPitches_present = EC.visibility_of_element_located((By.XPATH, r'//*[@id="detailedPitches"]/tbody/tr[1]/td[2]/span'))
            WebDriverWait(driver, timeout).until(detailedPitches_present)

            src = driver.page_source
            parser = BeautifulSoup(src, "lxml")

            pitchMovement = parser.find("table", attrs = {"id": "pitchMovement"})
            detailedPitches = parser.find("table", attrs = {"id": "detailedPitches"})
            runValues = parser.find("table", attrs = {"id": "runValues"})
            spinDirection = parser.find("table", attrs = {"id": "spinAxis"})
    
            if not pitcher_headerlist:
                pitchMovementHeaders = pitchMovement.findAll('th')
                pitchMovementHeadersList = [h.text.strip() for h in pitchMovementHeaders[:]]

                detailedPitchesHeaders = detailedPitches.findAll('th')
                detailedPitchesHeadersList = [h.text.strip() for h in detailedPitchesHeaders[:]]

                runValuesHeaders = runValues.findAll('th')
                runValuesHeadersList = [h.text.strip() for h in runValuesHeaders[:]]

                spinDirectionHeaders = spinDirection.findAll('th')
                spinDirectionHeadersList = [h.text.strip() for h in spinDirectionHeaders[:]]
    
                pitchMovementHeadersList_2 = pitchMovementHeadersList[2:]
                pitchMovementHeadersList_2[0] = 'Name'
                pitcher_headerlist.extend(pitchMovementHeadersList_2)
                pitcher_headerlist.extend(detailedPitchesHeadersList[3:])
                pitcher_headerlist.extend(runValuesHeadersList[3:])
                pitcher_headerlist.extend(spinDirectionHeadersList[3:])

            pitchMovementRows = pitchMovement.findAll('tr')[2:]
            detailedPitchesRows = detailedPitches.findAll('tr')[1:]
            runValuesRows = runValues.findAll('tr')[1:]
            spinDirectionRows = spinDirection.findAll('tr')[1:]
    
            pitcher_stats = []
            pitcher2_stats = []
            pitcher3_stats = []
            pitcher4_stats = []
            for i in range(len(pitchMovementRows)):
                row_cells = []
                for td in pitchMovementRows[i].findAll('td'):
                    row_cells.append(td.getText().strip())
                pitcher_stats.append(row_cells)

            for i in range(len(detailedPitchesRows)):
                row_cells = []
                for td in detailedPitchesRows[i].findAll('td'):
                    row_cells.append(td.getText().strip())
                pitcher2_stats.append(row_cells)

            for i in range(len(runValuesRows)):
                row_cells = []
                for td in runValuesRows[i].findAll('td'):
                    row_cells.append(td.getText().strip())
                pitcher3_stats.append(row_cells)

            for i in range(len(spinDirectionRows)):
                row_cells = []
                for td in spinDirectionRows[i].findAll('td'):
                    row_cells.append(td.getText().strip())
                pitcher4_stats.append(row_cells)

            for i in range(len(pitchMovementRows)):
                for pitch in pitcher_stats:
                    if pitch[1] == pitcher2_stats[i][1]:
                        pitch.extend(pitcher2_stats[i][3:])

            for i in range(len(pitchMovementRows)):
                for pitch in pitcher_stats:
                    if pitch[1] == pitcher3_stats[i][1]:
                        pitch.extend(pitcher3_stats[i][3:])

            for i in range(len(pitchMovementRows)):
                for pitch in pitcher_stats:
                    if pitch[1] == pitcher4_stats[i][1]:
                        pitch.extend(pitcher4_stats[i][3:])
    
            for pitch in pitcher_stats: 
                pitch.insert(0, player[1])

        driver.quit()

pitchers_df = pd.DataFrame(pitcher_stats, columns=pitcher_headerlist)
hitters_df = pd.DataFrame(player_stats, columns=hitter_headerlist)

print(pitchers_df)