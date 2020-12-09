import requests, os, shutil, json, re
import tools
from bs4 import BeautifulSoup
from urllib.parse import urlparse

baseUrl = "http://wiki.shoryuken.com"
url = baseUrl + "/Ultra_Street_Fighter_IV"
headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }

characterException = {'Gen': ['Mantis', 'Crane']}

def normalTranslator(string):
    string = string.lower()
    buttons = {
        'jab': "lp",
        'strong': "mp",
        'fierce': "hp",
        'short': "lk",
        'forward': "mk",
        'roundhouse': "hk",
        'ex': "ex",
        '3p': "3p",
        '3k': "3k",
        'close': 'cl.',
        'd +': 'cr.',
        'far': '',
        'u +': 'jump.',
        'ub / uf +': 'forwardjump.'
    }
    string = string.replace("(charge)", "")
    for key, item in buttons.items():
        string = string.replace(key, item)
    string = string.replace(" ", "")
    return string

def getPath(name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

def getTableHeaders(soup):
    array = []
    for tr in soup.findAll("tr"):
        for th in th.findAll("th"):
            array.append(tools.removePunctuation(th.getText()))
    return array

def convertHtmlTableToArray(soup):
    array = []
    for tr in soup.findAll("tr"):
        tempArray = []
        for td in tr.findAll("td"):
            if 'colspan' in td.attrs:
                break
            tempArray.append(parseTableEntry(td))
        if tempArray == []:
            continue
        array.append(tempArray)
    return array

def getTableHeader(soup):
    for tr in soup.findAll("tr"):
        array = []
        for th in tr.findAll("th"):
            array.append(th.getText())
        return array

def parseTableEntry(soup):
    for a in soup.findAll("a"):
        link = a['href'].split("/")
        link = link[len(link) - 1].split(":")
        link = link[len(link) - 1].split(".")
        link = link[0]
        a.contents[0].replaceWith(link)
    return soup.getText().rstrip()

def removeButton(string):
    string = string.replace(" Armorbreak", "")
    string = string.replace("P Ex", "P")
    string = string.replace("K Ex", "K")
    buttons = {
        ' Jab': "Lp",
        ' Strong': "Mp",
        ' Fierce': "Hp",
        ' Short': "Lk",
        ' Forward': "Mk",
        ' Roundhouse': "Hk",
        ' EX': "Ex",
        ' 3p': "ppp",
        ' 3k': "kkk"}
    for key, value in buttons.items():
        string = string.replace(value + " Ex", value)
        if key in string:
            if key in [' 3p', ' 3k']:
                return [string.replace(key, value), key]
            return [string.replace(key, ""), value]
    return [string, ""]

def getMoveType(string, soup):
    td = soup.find("td", text=string)
    td = td.findNext("td")
    move = parseTableEntry(td).lower()
    if any(substring in move for substring in ['jab', 'strong', 'fierce']):
        return 'P'
    elif any(substring in move for substring in ['short', 'forward', 'roundhouse']):
        return 'K'
    return -1

def findMoveCommand(string, soup, specialStrength = False):
    if "Target Combo" in string:
        specialStrength = ""
    string = string.replace("Angled", "Diagonal")
    if "Red Focus" in string:
        return "Lp+Mp+Mk"
    for td in soup.findAll("td"):
        if string.lower() not in  td.getText().lower().rstrip() or 'colspan' in td.attrs:
            continue
        try:
            td.find('b').findNext('p').find('b')
        except:
            continue
        #print(string + " - >>" + td.getText().lower().rstrip().strip() + "<<" + td.findNext('td').findNext('td').getText()
        nextTd = parseTableEntry(td.findNext("td").findNext("td"))
        #if any(substring in nextTd for substring in ["-", "*"]) or nextTd == "":
        if nextTd in ['-', "*", ""]:
            continue
        try:
            int(nextTd)
            continue
        except:
            pass
        if string.lower() in nextTd:
            continue
        moveInput = removeButton(nextTd)[0]
        if specialStrength != '':
            if specialStrength == "Ex":
                moveInput = moveInput.replace("+ K", "+ KK")
                moveInput = moveInput.replace("+ P", "+ PP")
            else:
                moveInput = moveInput.replace("+ K", "+ " + specialStrength)
                moveInput = moveInput.replace("+ P", "+ " + specialStrength)
        return normalTranslator(moveInput)
    return "Unknown Command"


characterLinks = {}
folder = getPath("sf4")
if os.path.isdir(folder):
    shutil.rmtree(folder)
os.mkdir(folder)

page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.text, features='html.parser')
for tbody in soup.findAll("table"):
    for a in tbody.findAll("a"):
        try:
            a['title']
        except:
            pass
        else:
            if a.getText() != '':
                characterLinks[a.getText()] = baseUrl + a['href']

#characterLinks = {'Gen': 'http://wiki.shoryuken.com/Ultra_Street_Fighter_IV/Gen'}

for character, link in characterLinks.items():
    page = requests.get(link, headers=headers)
    soup = BeautifulSoup(page.text, features='html.parser')
    counter = 0
    keyDict = {}
    table = soup.find("h2", text="Frame Data (At A Glance)").findNext("table")
    tableRaw = convertHtmlTableToArray(table)
    tableArrays = {}

    if character in characterException.keys():
        cut = 0
        for i in range(len(tableRaw)):
            if i != 0 and tableRaw[i][0] == "Close LP":
                cut = i
                break
        tableArrays[character+characterException[character][0]] = tableRaw[:cut]
        tableArrays[character+characterException[character][1]] = tableRaw[cut-len(tableRaw):]
    else:
        tableArrays[character] = tableRaw

    tableHeaders = getTableHeader(table)
    lastCommand = "Unknown Command"
    for key, tableRaw in tableArrays.items():
        print("Writing " + key + " file")
        frameDataDict = {}
        for i in range(len(tableRaw)):
            row = {}
            specialButton = ''
            buttons = ['LP', 'MP', 'HP', 'LK', 'MK', 'HK']
            if "EX" not in tableRaw[i][0] and "Tourouzan" in tableRaw[i][0]:
                tableRaw[i][0] = "Tourouzan"
            if tableRaw[i][0]  == "":
                tableRaw[i][0] = tableRaw[i-1][0]

                #Fix some rekkas
                p = re.compile("[0-9]+ hit")
                result = p.search(tableRaw[i][1])
                if result:
                    tableRaw[i][0] = re.sub(" Part [0-9]+", "", tableRaw[i][0]) + " Part " + result.group(0).replace(" hit", "")
            rowName = tableRaw[i][0].rstrip().strip()
            if "Super Combo" in tableRaw[i][1]:
                moveName = removeButton(tableRaw[i][0])[0]
            else:
                moveName = tableRaw[i][0] 
            if not any(x in moveName for x in buttons):
                specialButton = removeButton(tableRaw[i][1])[1]
                if not any(x in rowName for x in ["EX", "Target Combo"]):
                    rowName = (specialButton + " " + rowName).rstrip().strip()
            for j in range(1, len(tableRaw[i])):
                row[tableHeaders[j].rstrip().strip()] = tableRaw[i][j].rstrip().strip()
            row['Input'] = str(findMoveCommand(tableRaw[i][0].replace("EX ", "").replace(" (Genei Jin)", ""), soup, specialButton))
            if row['Input'] == "Unknown Command":
                if tableRaw[i][0] in tableRaw[i-1][0]:
                    row['Input'] = lastCommand
                else:
                    print(rowName + " command not found")
            lastCommand = row['Input']
            frameDataDict[rowName] = row
        with open(os.path.join(folder, key + ".json"), 'w') as outfile:
            json.dump(frameDataDict, outfile, indent=4)
