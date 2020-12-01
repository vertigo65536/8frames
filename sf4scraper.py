import requests, os, shutil
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
    for key, item in buttons.items():
        string = string.replace(key, item)
    string = string.replace(" ", "")
    return string

def getPath(name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

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

def newFindMoveCommand(string, soup, specialStrength = False):
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
        nextTd = parseTableEntry(td.findNext("td").findNext("td"))
        if any(substring in nextTd for substring in ["-", "*"]) or nextTd == "":
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
    print("Writing " + character + " file")
    page = requests.get(link, headers=headers)
    soup = BeautifulSoup(page.text, features='html.parser')
    counter = 0
    keyDict = {}

    table = soup.find("h2", text="Frame Data (At A Glance)").findNext("table")
    tableRaw = convertHtmlTableToArray(table)
    #headers = getTableHeader(table)
    tableArrays = {}
    if character in characterException.keys():
        cut = 0
        for i in range(len(tableRaw)):
            if i != 0 and tableRaw[i][0] == "Close LP":
                cut = i
                break
        print(cut)
        tableArrays[character+characterException[character][0]] = tableRaw[:cut]
        tableArrays[character+characterException[character][1]] = tableRaw[cut-len(tableRaw):]
    else:
        tableArrays[character] = tableRaw
    for key, tableArray in tableArrays.items():
        try:
            buttons = ['LP', 'MP', 'HP', 'LK', 'MK', 'HK']
            with open(os.path.join(folder, key + ".csv"), 'a') as csv_file:
                for i in range(len(tableArray)):
                    if tableArray[i][0] == "":
                        tableArray[i][0] = tableArray[i-1][1]
                    if "Super Combo" in tableArray[i][1]:
                        moveName = removeButton(tableArray[i][0])[0]
                    else:
                        moveName = tableArray[i][0]
                    specialButton = ''
                    if not any(x in moveName for x in buttons):
                        specialButton = removeButton(tableArray[i][1])[1]
                    command = str(newFindMoveCommand(moveName.replace("EX ", ""), soup, specialButton))
                    if command == "Unknown Command":
                        print(command + " - " + moveName)
                    tableArray[i].insert(0, command)
                    csv_file.write('`'.join(tableArray[i]) + "\n")
        except:
            print("Failed to open " + os.path.join(folder, key + ".csv"))
