from players import players

import requests
from bs4 import BeautifulSoup
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
player_stats = []

for player in players:
    if player[-1] != "Pitcher":    
        for hand in handedness:
            url = f"https://baseballsavant.mlb.com/player-services/statcast-pitches-breakdown?playerId={player[2].split('-')[-1]}&position=8&hand={hand}&pitchBreakdown=pitches&timeFrame=yearly&season=&pitchType=&count=&updatePitches=true"

            r = requests.get(url, headers=headers)

            parser = BeautifulSoup(r.content, "html.parser")
            table = parser.find(id="detailedPitches")

            headersTH = table.find_all('th')
            headerlist = [h.text.strip() for h in headersTH[:]]
            headerlist.insert(0, "Name")
            headerlist.insert(2, "Team")
            headerlist.insert(3, "Hand") 
    
            rows = table.findAll('tr')[1:]
    
            for i in range(len(rows)):
                row_cells = []
                for td in rows[i].findAll('td'):
                    row_cells.append(td.getText().strip())
                row_cells.insert(0, player[1])
                row_cells.insert(2, player[0])
                row_cells.insert(3, hand)
                player_stats.append(row_cells)

df = pd.DataFrame(player_stats, columns=headerlist)

print(df)