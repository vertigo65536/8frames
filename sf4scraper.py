import requests, os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

baseUrl = "http://wiki.shoryuken.com"
url = baseUrl + "/Ultra_Street_Fighter_IV"
headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }

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
        ' 3p': "3p",
        ' 3k': "3k"}
    for key, value in buttons.items():
        string = string.replace(value + " Ex", value)
        if key in string:
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

def findSpecialCommand(string, soup):
    buttonParse = removeButton(string)
    string = buttonParse[0]
    button = buttonParse[1]
    for td in soup.findAll("td", text=string):
        nextTd = td.findNext("td")
        #print(">" + nextTd.getText().lower().rstrip() + "<")
        if nextTd.getText().lower().rstrip() == string.lower().rstrip():
            nextTd = nextTd.findNext("td")
        elif nextTd.getText().lower().rstrip() == "-":
            nextTd = nextTd.findNext("td")
        else:
            try:
                int(nextTd.getText().lower().rstrip())
                continue
            except:
                pass
            if string.lower().rstrip() in nextTd.getText().lower().rstrip():
                continue
        moveInput = removeButton(parseTableEntry(nextTd))[0]
        if button == "Ex":
            moveInput = moveInput.replace("+ K", "+ 2K")
            moveInput = moveInput.replace("+ P", "+ 2P")
        else:
            moveInput = moveInput.replace("+ K", "+ " + button)
            moveInput = moveInput.replace("+ P", "+ " + button)
        return moveInput
    return "couldn't find move"

def findMoveCommand(string, soup):
    string = string.replace("Ultra Combo 1", "Ultra Combo I")
    string = string.replace("Ultra Combo 2", "Ultra Combo II")
    string = string.replace("Angled", "Diagonal")
    string = string + "\n"
    if "Red Focus" in string:
        return "Lp + Mp + Mk"
    for td in soup.findAll("td", text=string):
        nextTd = td.findNext("td")
        if nextTd.getText().lower().rstrip() == string.lower().rstrip():
            nextTd = nextTd.findNext("td")
        else:
            try:
                int(nextTd.getText().lower().rstrip())
                continue
            except:
                pass
        return parseTableEntry(nextTd).replace(" Armorbreak", "")
    return findSpecialCommand(string, soup)

characterLinks = {}
folder = getPath("sf4")
if not os.path.isdir(folder):
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

for character, link in characterLinks.items():
    print("Writing " + character + " file")
    page = requests.get(link, headers=headers)
    soup = BeautifulSoup(page.text, features='html.parser')
    counter = 0
    keyDict = {}
    #for tbody in soup.findAll("table", {"class": "wikitable"}):
    #    #try:
    #    data = convertHtmlTableToArray(tbody)
    #    if len(data) < 1 or len(data[0]) < 4:
    #        continue
    #    if data[0][1].replace("\n", "") == "Name":
    #        if data[0][3].replace("\n", "") == "Command":
    #            print(data)
    #            for i in range(1, len(data) - 1):
    #                #print(data[i])
    #                keyDict[data[i][1]] = data[i][3]
    #    #except:
    #    #    pass
    #    #break
    #print(keyDict)
    #break

    table = soup.find("h2", text="Frame Data (At A Glance)").findNext("table")
    tableArray = convertHtmlTableToArray(table)
    #headers = getTableHeader(table)
    #try:
    with open(os.path.join(folder, character + ".csv"), 'a') as csv_file:
        for i in range(len(tableArray)):
            print(tableArray[i][1] + " _ " + str(findMoveCommand(tableArray[i][1], soup)))
            csv_file.write('`'.join(tableArray[i]) + "\n")
    #except:
    #    print("Failed to open " + os.path.join(folder, character + ".csv"))
    break
