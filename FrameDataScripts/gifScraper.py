import requests, os, shutil, re, json
import tools
from fuzzywuzzy import process, fuzz
from bs4 import BeautifulSoup
from urllib.parse import urlparse

origin_url = "https://gfycat.com"
character_select_url = "/@OffInBed/collections/"
headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }

characterLinks = {}

#page = requests.get(origin_url + character_select_url, headers=headers)
#soup = BeautifulSoup(page.text, features='html.parser')
#
#for div in soup.findAll('div', {'class': 'grid-album-item'}):
#    for link in div.findAll('a'):
#        charLink = origin_url + link['href']
#        break
#    for nameDiv in div.findAll('div', {'class': 'grid-album-item__bottom'}):
#        characterLinks[nameDiv.getText()] = charLink
#        break

r = requests.get('https://api.gfycat.com/v1/users/offinbed/collections?count=100', headers=headers, timeout=10)
for i in range(len(r.json()['gfyCollections'])):
    characterLinks[r.json()['gfyCollections'][i]['folderName']] = origin_url + character_select_url + r.json()['gfyCollections'][i]['folderId'] + "/1"

for key, value in characterLinks.items():
    print("Processing " + key)
    page = requests.get(value, headers=headers)
    soup = BeautifulSoup(page.text, features='html.parser')

    moveGif = []

    requestLink = value.replace("https://gfycat.com/@", "https://api.gfycat.com/v1/users/")
    requestSplit = requestLink.split("/")
    requestSplit[len(requestSplit) - 1] = 'gfycats'
    requestLink = "/".join(requestSplit) + "?count=100"

    webtoken_header = {
        "Host": "weblogin.gfycat.com",
        "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": value,
        "Content-Type": "text/plain;charset=UTF-8",
        "Origin": "https://gfycat.com",
        "Content-Length": "73",
        "Connection": "keep-alive"
        }

    r = requests.post(
        url = "https://weblogin.gfycat.com/oauth/webtoken",
        json = {
            "access_key":"Anr96uuqt9EdamSCwK4txKPjMsf2M95Rfa5FLLhPFucu8H5HTzeutyAa"
            },
        headers = webtoken_header,
        timeout = 10
    )

    token = r.json()['token_type'].capitalize() + " " + r.json()['access_token']

    headers = {
        "Host": "api.gfycat.com",
        "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.5",
        "authorization": token,
        "Accept-Encoding": "gzip, deflate, br",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "authorization",
        "Referer": value,
        "Origin": "https://gfycat.com"
    }
    r = requests.get(
        url = requestLink,
        headers = headers,
        timeout = 10
    )
    try:
        gifArray = r.json()['gfycats']
        while len(gifArray) < r.json()['totalCount']:
            r = requests.get(
                url = requestLink + "&cursor=" + r.json()['cursor'],
                headers = headers,
                timeout = 10
            )
            gifArray = gifArray + r.json()['gfycats']
    except:
        print(requestLink)
    gifDict = {}
    for i in range(len(gifArray)):
        try:
            gifDict[gifArray[i]['title']] = gifArray[i]['gifUrl']
        except:
            continue

    gamedir = 't7'
    files = os.listdir(gamedir)
    fuzzyMatch  = process.extractOne(key + ".json", files, scorer=fuzz.ratio)
    if fuzzyMatch[1] < 60:
        continue
    characterFile = [gamedir + "/" + fuzzyMatch[0], fuzzyMatch[0].replace(".json", "")]
    punct = "!@#$%^&*()[]{};:,./<>?\|`~-=_ "
    replacePunct = ""

    moveDict = tools.loadJsonAsDict(characterFile[0])
    for moveName, url in gifDict.items():
        files = os.listdir(gamedir)
        fuzzyMatch  = process.extractOne(key + ".json", files, scorer=fuzz.ratio)
        if fuzzyMatch[1] < 60:
            continue
        characterFile = [gamedir + "/" + fuzzyMatch[0], fuzzyMatch[0].replace(".json", "")]

        search = tools.searchMove(moveName, characterFile[0], "key", [punct, replacePunct], fuzz.ratio)[0]
        moveDict[search[1]]['webm'] = url

    with open(characterFile[0], 'w') as json_file:
        json.dump(moveDict, json_file, indent=4)


