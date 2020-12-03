import requests, os, shutil, re
from bs4 import BeautifulSoup
from urllib.parse import urlparse


origin_url = "http://wiki.shoryuken.com"
character_extension = "/Street_Fighter_3:_3rd_Strike"

headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }

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

folder = getPath("sf3")
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

characters = {"Ken": "http://wiki.shoryuken.com/Street_Fighter_3:_3rd_Strike/Ken"}

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

    frameData = []

    nextHeader = currentElement.findNext('img').findNext('h1').getText()

    while currentElement.findNext('img').findNext('h1').getText() == nextHeader:
        row = []
        moveImg = origin_url + currentElement.findNext('img')['src']
        currentElement = currentElement.findNext('img').findNext('table')
        tmpTable = getTableAsArray(currentElement)
        columns = [1, 0]
        if tmpTable[0][0].rstrip().strip() == "Super Art":
            columns = [3, 1]
        for i in range(1, len(tmpTable)):
            p = re.compile("x[0-9]+")
            result = p.search(tmpTable[i][1])
            if result != None:
                for j in range(int(result.group(0).replace("x", ""))):
                    row.append([tmpTable[i][columns[0]].rstrip().strip(), tmpTable[i][columns[1]].rstrip().strip()])
            else:
                row.append([tmpTable[i][columns[0]].rstrip().strip(), tmpTable[i][columns[1]].rstrip().strip()])
        if currentElement.findNext('p').getText().rstrip() == "Frame Data":
            currentElement = currentElement.findNext('p').findNext('table')
            tmpTable = getTableAsArray(currentElement)
            for i in range(1, len(tmpTable)):
                try:
                    row[i-1]
                except:
                    row.append(["", ""])
                for j in range(0, len(tmpTable[i])):
                    if tmpTable[0][j].rstrip().strip() in ['Moves', 'Juggle Value']:
                        continue
                    row[i-1].append(tmpTable[i][j].rstrip())
        if currentElement.findNext('p').getText().rstrip() == "Gauge Increase":
            currentElement = currentElement.findNext('p').findNext('table')
        row.append(row[0])
        del row[0]
        for i in range(len(row)):
            row[i].append(moveImg)
            if len(row[i]) > 11:
                del row[i][1]
            frameData.append(row[i])
        if currentElement.findNext('img').findNext('h1') == None:
            break
    try:
        with open(os.path.join(folder, character + ".csv"), 'a') as csv_file:
            counter = 0
            for i in range(len(frameData)):
                if len(frameData) < 9:
                    continue
                csv_file.write("`".join(frameData[i]) + "\n")
                counter += 1
        print("Wrote " + str(counter) + " lines")
    except:
        print("Failed to open " + os.path.join(folder, character + ".csv"))
