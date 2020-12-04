import requests, os, shutil, re, json
from bs4 import BeautifulSoup
from urllib.parse import urlparse


origin_url = "http://wiki.shoryuken.com"
character_extension = "/Street_Fighter_3:_3rd_Strike"

headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }

def getColName(string):
    if string == "Num.":
        return "Super Art"
    return string

def getTableAsArray(soup):
    output = []
    for tr in soup.findAll('tr'):
        row = []
        for td in tr.findAll('td'):
            row.append(td.getText())
        output.append(row)
    return output

def getPath(name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

folder = getPath("sf3-json")
if os.path.isdir(folder):
    shutil.rmtree(folder)
os.mkdir(folder)

characterLinks = {}

page = requests.get(origin_url + character_extension, headers=headers)
soup = BeautifulSoup(page.text, features='html.parser')

table = soup.find(id="Characters").parent.findNext('table')
characters = {}
for li in table.findAll('li'):
    characters[li.getText().rstrip().strip()] = origin_url + li.find('a')['href']

#characters = {"Ken": "http://wiki.shoryuken.com/Street_Fighter_3:_3rd_Strike/Ken"}

for character, url in characters.items():
    if character == "Gill":
        continue
    print("Writing " + character + " file")
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, features='html.parser')
    try:
        currentElement = soup.find(id="Move_Analysis").parent.findNext(id="Normal_Moves_2").parent.findNext('h4')
    except:
        currentElement = soup.find(id="Normal_Moves").parent.findNext('h4')

    frameData = {}

    nextHeader = currentElement.findNext('img').findNext('h1').getText()

    while currentElement.findNext('img').findNext('h1').getText() == nextHeader:
        row = {}
        moveImg = origin_url + currentElement.findNext('img')['src']
        currentElement = currentElement.findNext('img').findNext('table')
        tmpTable = getTableAsArray(currentElement)
        nameKey = 0
        columns = [1]
        sa = 0
        moveName = []
        if tmpTable[0][0].rstrip().strip() in ["Super Art", "Num."]:
            sa = 1
            nameKey = 1
            columns = [0, 3]
        for i in range(1, len(tmpTable)):
            p = re.compile("x[0-9]+")
            result = p.search(tmpTable[i][1])
            moveName.append(tmpTable[i][nameKey].rstrip().strip())
            frameData[moveName[i - 1]] = {}
            for j in range(len(columns)):
                    if result != None:
                        for k in range(int(result.group(0).replace("x", ""))):
                            frameData[moveName[i - 1]][getColName(tmpTable[0][columns[j]].rstrip().strip())] = tmpTable[i][columns[j]].rstrip().strip()
                    else:
                        frameData[moveName[i - 1]][getColName(tmpTable[0][columns[j]].rstrip().strip())] = tmpTable[i][columns[j]].rstrip().strip()
        if currentElement.findNext('p').getText().rstrip() == "Frame Data":
            currentElement = currentElement.findNext('p').findNext('table')
            tmpTable = getTableAsArray(currentElement)
            if len(moveName) < len(tmpTable) - 1:
                newMoveName = []
                for i in range(1, len(tmpTable)):
                    newMoveName.append(tmpTable[i][0].rstrip().strip())
                    if len(moveName) == 1:
                        frameData[newMoveName[i-1]] = frameData[moveName[0]]
                    elif tmpTable[0][i].rstrip().strip() not in moveName:
                        frameData[newMoveName[i-1]] = frameData[newMoveName[i-2]]

                moveName = newMoveName
            for i in range(1, len(tmpTable)):
                for j in range(0, len(tmpTable[i])):
#                    if tmpTable[0][j].rstrip().strip() in ['Moves', 'Juggle Value']:
#                        continue
                    frameData[moveName[i - 1]][tmpTable[0][j].rstrip().strip()] = tmpTable[i][j].rstrip().strip()
        if currentElement.findNext('p').getText().rstrip() == "Gauge Increase":
            currentElement = currentElement.findNext('p').findNext('table')                
        for i in range(len(moveName)):
            frameData[moveName[i]]['Image'] = moveImg
            #if sa == 1:
            #    
        if currentElement.findNext('img').findNext('h1') == None:
            break
    with open(os.path.join(folder, character + ".json"), 'w') as outfile:
        json.dump(frameData, outfile, indent=4)
