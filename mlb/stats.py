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
players = [['dbacks', 'Miguel Castro', 'miguel-castro-612434', 'Pitcher']]

# Proxy configuration
PROXY = "127.0.0.1:24000"
# Path to chromedriver executable
PATH = "/opt/homebrew/Caskroom/chromedriver/121.0.6167.85/chromedriver-mac-arm64/chromedriver"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=%s' % PROXY)

timeout = 25

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# pitcher function
def missing_stats(pitches_less, pitches_more, pitches_less_stats):  
    pitches_needed = []
    for row in pitches_more:
        yearPitch = row.findAll('td')[0].getText().strip() + row.findAll('td')[1].getText().strip()
        pitches_needed.append(yearPitch)
    
    pitches_got = []
    for row in pitches_less:
        yearPitch = row.findAll('td')[0].getText().strip() + row.findAll('td')[1].getText().strip()
        pitches_got.append(yearPitch)

    missing_pitch = []
    for pitch in pitches_needed:
        if pitch not in pitches_got:
            missing_pitch.append(pitch)

    missing_pitch_arr = []
    for pitch in missing_pitch:
        missing_pitch_arr.append(pitch[:4])
        missing_pitch_arr.append(pitch[4:])   

    for stat in pitches_less[2:]:
        missing_pitch_arr.append('') # appends empty string for value to keep the correct amount of cols
    
    for pitch in missing_pitch_arr:
        pitches_less_stats.append(pitch) # appends missing pitch

def largest_pitch_count():
    pitch_count = []
    pitch_count.append(pitchMovementRows)
    pitch_count.append(pitchTrackingRows)
    pitch_count.append(runValuesRows)
    pitch_count.append(spinDirectionRows)
    return max(pitch_count, key=len)


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
        

        url = f"https://baseballsavant.mlb.com/savant-player/{player[2]}?stats=statcast-r-pitching-mlb"
        driver.get(url)

        detailedPitches_present = EC.visibility_of_element_located((By.XPATH, r'//*[@id="detailedPitches"]/tbody/tr[1]/td[2]/span'))
        WebDriverWait(driver, timeout).until(detailedPitches_present)

        src = driver.page_source
        parser = BeautifulSoup(src, "lxml")

        pitchMovement = parser.find("table", attrs = {"id": "pitchMovement"})
        pitchTracking = parser.find("table", attrs = {"id": "detailedPitches"})
        runValues = parser.find("table", attrs = {"id": "runValues"})
        spinDirection = parser.find("table", attrs = {"id": "spinAxis"})
    
        if not pitcher_headerlist:
            pitchMovementHeaders = pitchMovement.findAll('th')
            pitchMovementHeadersList = [h.text.strip() for h in pitchMovementHeaders[:]]

            pitchTrackingHeaders = pitchTracking.findAll('th')
            pitchTrackingHeadersList = [h.text.strip() for h in pitchTrackingHeaders[:]]

            runValuesHeaders = runValues.findAll('th')
            runValuesHeadersList = [h.text.strip() for h in runValuesHeaders[:]]

            spinDirectionHeaders = spinDirection.findAll('th')
            spinDirectionHeadersList = [h.text.strip() for h in spinDirectionHeaders[:]]
    
            pitchMovementHeadersList_2 = pitchMovementHeadersList[2:]
            pitchMovementHeadersList_2[0] = 'Name'
            pitcher_headerlist.extend(pitchMovementHeadersList_2)
            pitcher_headerlist.extend(pitchTrackingHeadersList[3:])
            pitcher_headerlist.extend(runValuesHeadersList[3:])
            pitcher_headerlist.extend(spinDirectionHeadersList[3:])

        pitchMovementRows = pitchMovement.findAll('tr')[2:]
        pitchTrackingRows = pitchTracking.findAll('tr')[1:]
        runValuesRows = runValues.findAll('tr')[1:]
        spinDirectionRows = spinDirection.findAll('tr')[1:]
    
        pitchMovement_stats = []
        pitchTracking_stats = []
        runValues_stats = []
        spinDirection_stats = []

        for i in range(len(pitchMovementRows)):
            row_cells = []
            for td in pitchMovementRows[i].findAll('td'):
                row_cells.append(td.getText().strip())
            pitchMovement_stats.append(row_cells)

        for i in range(len(pitchTrackingRows)):
            row_cells = []
            for td in pitchTrackingRows[i].findAll('td'):
                row_cells.append(td.getText().strip())
            pitchTracking_stats.append(row_cells)

        for i in range(len(runValuesRows)):
            row_cells = []
            for td in runValuesRows[i].findAll('td'):
                row_cells.append(td.getText().strip())
            runValues_stats.append(row_cells)

        for i in range(len(spinDirectionRows)):
            row_cells = []
            for td in spinDirectionRows[i].findAll('td'):
                row_cells.append(td.getText().strip())
            spinDirection_stats.append(row_cells)

        if (len(largest_pitch_count()) > len(spinDirectionRows)):
            missing_stats(spinDirectionRows, largest_pitch_count(), spinDirection_stats)
        if (len(largest_pitch_count()) > len(pitchTrackingRows)):
            missing_stats(pitchTrackingRows, largest_pitch_count(), pitchTracking_stats)   
        if (len(largest_pitch_count()) > len(runValuesRows)):
            missing_stats(runValuesRows, largest_pitch_count(), runValues_stats)
        if (len(largest_pitch_count()) > len(pitchMovementRows)):
            missing_stats(pitchMovementRows, largest_pitch_count(), pitchMovement_stats) 
            

        for i in range(len(pitchMovement_stats)):
            for pitch in pitchMovement_stats:
                if pitch[1] == pitchTracking_stats[i][1] and pitch[0] == pitchTracking_stats[i][0]:
                    pitch.extend(pitchTracking_stats[i][3:])

        for i in range(len(pitchMovement_stats)):
            for pitch in pitchMovement_stats:
                if pitch[1] == runValues_stats[i][1] and pitch[0] == runValues_stats[i][0]:
                    pitch.extend(runValues_stats[i][3:])

        for i in range(len(pitchMovement_stats)):
            for pitch in pitchMovement_stats:
                if pitch[1] == spinDirection_stats[i][1] and pitch[0] == spinDirection_stats[i][0]:
                    pitch.extend(spinDirection_stats[i][3:])
    
        for pitch in pitchMovement_stats: 
            pitch.insert(0, player[1])
            pitcher_stats.append(pitch)

driver.quit()

pitchers_df = pd.DataFrame(pitcher_stats, columns=pitcher_headerlist)
hitters_df = pd.DataFrame(player_stats, columns=hitter_headerlist)

print(pitchers_df)
print(hitters_df)