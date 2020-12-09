import shutil, os, json, requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

url = "https://rbnorway.org/t7-frame-data/"
headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }

def getPath(name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

folder = getPath("t7")
if os.path.isdir(folder):
    shutil.rmtree(folder)
os.mkdir(folder)

characterLinks = {}

page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.text, features='html.parser')
for div in soup.findAll("div", {"class": ["entry", "clearfix"]}):
    for imageDiv in div.findAll("div", {"class": "image-block"}):
        for characterLink in imageDiv.findAll('a'): 
            characterLinks[characterLink['href']] = characterLink['href']

for characterLink in characterLinks:
    if not urlparse(characterLink).netloc:
        characterLink = "https://rbnorway.org/" + characterLink

    page = requests.get(characterLink, headers=headers)
    soup = BeautifulSoup(page.text, features='html.parser')

    for title in soup.findAll('h2'):
        characterName = title.getText().replace(" T7 Frames", "")
        break

    print("Writing " + characterName + " file")

    moveDict = {}
    for table in soup.findAll("table"):
        colHeaders = []
        for header in table.find('thead').findAll('th'):
            colHeaders.append(header.getText().strip().rstrip())
        for tr in table.find('tbody').findAll("tr"):
            tmpArray = []
            counter = 0
            for td in tr.findAll("td"):
                if counter >= len(colHeaders):
                    continue
                tmpArray.append(td.getText().strip().rstrip())
                counter += 1
            moveDict[tmpArray[0]] = {}
            #print(tmpArray, colHeaders)
            for i in range(1, len(tmpArray)):
                moveDict[tmpArray[0]][colHeaders[i]] = tmpArray[i]

    with open(os.path.join(folder, characterName + ".json"), 'w') as outfile:
        json.dump(moveDict, outfile, indent=4)
print("Complete!")
