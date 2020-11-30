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
            tempArray.append(td.getText().rstrip())
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
    try:
        with open(os.path.join(folder, character + ".csv"), 'a') as csv_file:
            for i in range(len(tableArray)):
                csv_file.write('`'.join(tableArray[i]) + "\n")
    except:
        print("Failed to open " + os.path.join(folder, character + ".csv"))
