import sys
sys.path.insert(0, '../../')
from utils import *

# Adjusted Offensive +/- = off_adj_rapm.value
# Adjusted Defensive +/- = def_adj_rapm.value
# Positions = posFreqs/posConfidence

def fetch(season, tier='High'):
    season = str(int(season[:4])+1) + '-' + str(int(season[-2:])+1)
    time.sleep(2)
    count = 0
    req_headers = { 'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                   'referer': "ttps://www.sports-reference.com/cbb/schools/pepperdine/2022.html",
                   'accept-language': "en-US,en;q=0.6",
                   'accept-encoding': "gzip, deflate, br"}
    while count < 3:
        try:
            url = f"https://hoop-explorer.com/api/getLeaderboard?src=players&oppo=all&gender=Men&year={season}&tier={tier}"
            response = requests.get(url, headers=req_headers, timeout=30)
            return response.json()
        except requests.exceptions.ConnectionError:
            print("Connection error, giving it 10 and retrying")
            time.sleep(10)
            count += 1
        except requests.exceptions.TooManyRedirects:
            print("Redirect error, giving it 10 and then retrying")
            req_headers = { 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"}
            time.sleep(10)
            count += 1
    if not response:
        print('NO RESPONSE')
        return None, None
    return None