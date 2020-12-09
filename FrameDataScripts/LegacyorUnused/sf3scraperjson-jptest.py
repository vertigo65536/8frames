import requests, os, shutil, re, json, sys
import tools
from word2number import w2n
from google_trans_new import google_translator
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from fuzzy_match import match

translator = google_translator()

origin_url = "http://wiki.shoryuken.com"
character_extension = "/Street_Fighter_3:_3rd_Strike"

headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
            'charset': 'utf-8'
        }
def translateMoveName(string, button):
    translations = {
        'kick during vertical jump': 'Neutral Jump Forward',
        'punch during vertical jump': 'Neutral Jump Strong',
        'punch during diagonal jump': 'Jump Strong',
        'kick during diagonal jump': 'Jump Forward',
        'kick while crouching': 'Crouch Forward',
        'punch while crouching': 'Crouch Strong',
        'small punch': 'Jab',
        'big punch': 'Fierce',
        'small kick': 'Short',
        'big kick': 'Roundhouse',
        'vertical jump': 'Neutral Jump',
        'diagonal jump': 'Jump',
        'short-distance standing': 'Close',
        'long-distance standing': 'Far',
        'crouching': 'Crouch',
        'standing': '', 
        'kick': 'Forward',
        'punch': 'Strong'
    }
    if button == "p":
        buttons = {
            'small': 'Jab',
            'in ': 'Strong ',
            'big': 'Fierce',
            'medium': 'Strong',
            'large': 'Fierce',
            'ｅｘ': 'ex'
        }
    elif button == "k":
        buttons = {
            'small': 'Short',
            'in ': 'Forward ',
            'big': 'Roundhouse',
            'medium': 'Forward',
            'large': 'Roundhouse',
            'ｅｘ' : 'ex'
        }
    else:
        buttons = {}
    string = string.lower().rstrip().strip()
    for key, new in translations.items():
        string = string.replace(key, new)
    for key, new in buttons.items():
        string = string.replace(key, new)
    return string.rstrip().strip()

def gtTranslation(string, backward=0):
    translations = {
       'Startup':                 'Occurrence',
       'Hit':                     'Sustain',
       'Recovery':                'Rigidity',
       'Hit Advantage':           'Standing hit',
       'Crouching Hit Advantage': 'Bend hit',
       'Blocked Advantage':       'guard'
    }
    if backward == 0:
        try:
            return translations[string]
        except:
            return string
    if backward == 1:
        for key, value in translations.items():
            if value.lower() == string.lower():
                return key
    return -1

def getColName(string):
    if "num." in string.lower():
        return "Super Art"
    return string

def getTableAsDictionary(soup):
    maxCol = 0
    maxRow = 0
    for tr in soup.findChildren('tr', recursive=False):
        maxRow += 1
        cols = 0
        for td in tr.findChildren(['td', 'th'], recursive=False):
            cols += 1
        if cols > maxCol:
            maxCol = cols
    tableDict = {}
    currentRow = 0
    carriedRow = []
    for i in range(maxCol):
        carriedRow.append(None)
    for tr in soup.findChildren('tr', recursive=False):
        tableDict[currentRow] = []
        cellCounter = 0
        cells = tr.findChildren(['td', 'th'], recursive=False)
        i = 0
        while i < len(carriedRow):
            if carriedRow[i] != None:
                tableDict[currentRow].append(carriedRow[i][0])
                carriedRow[i][1] -= 1
            else:
                td = cells[cellCounter]
                tableDict[currentRow].append(translator.translate(td.getText().rstrip().strip()))
                if td.get('colspan') != None:
                    for j in range(int(td.get('colspan')) - 1):
                        tableDict[currentRow].append(translator.translate(td.getText().rstrip().strip()))
                    i = i + int(td.get('colspan')) - 1
                if td.get('rowspan') != None:
                    carriedRow[i] = [translator.translate(td.getText().rstrip().strip()), int(td.get('rowspan')) - 1]
                cellCounter += 1
            try:
                if carriedRow[i] != None:
                    carriedRow[i][1]
            except:
                for key, value in tableDict.items():
                    print(key, value)
                print(carriedRow, i)
            while len(carriedRow) < len(tableDict[currentRow]):
                carriedRow.append(None)
            #print(carriedRow, i, carriedRow[i])
            if carriedRow[i] != None and carriedRow[i][1] <= 0:
                carriedRow[i] = None
            i += 1
        currentRow += 1
    return tableDict

RESET = '\033[0m'
def get_color_escape(r, g, b, background=False):
    return '\033[{};2;{};{};{}m'.format(48 if background else 38, r, g, b)

def convertNumberNotation(string, button):
    string = string.lower().rstrip().strip()
    if button == None:
        button = ""
    if string == "gokusatu":
        return "LP LP F LK HP"
    originalString = string
    numValues = {
        '1': 'db',
        '2': 'd',
        '3': 'df',
        '4': 'b',
        '5': '',
        '6': 'f',
        '7': 'ub',
        '8': 'u',
        '9': 'uf'
    }
    inputTranslation = {
        '63214': 'HCB',
        '41236': 'HCF',
        '236': 'QCF',
        '214': 'QCB'
    }
    if string == "2p":
        return "720+" + button
    elif string in ["1p", "1k"]:
        return "360+" + button
    elif string in ['p', 'k']:
        return "(Mash) " + button
    if 'p' in string:
        if not any(x in string for x in ['lp', 'mp', 'hp', 'pp', 'ppp', "pa"]):
            string = string.replace('p', "+" + button)
    elif 'k' in string:
        if not any(x in string for x in ['lk', 'mk', 'hk', 'kk', 'kkk']):
            string = string.replace('k', "+" + button)
    elif 'n' in string:
        string = string.replace('n', 'LP+LK')
    elif 'pa' in string:
        string = string.replace('pa', 'HP+HK')
    for key, values in inputTranslation.items():
        string = string.replace(key,values)
    for key, values in numValues.items():
        string = string.replace(key, values)
    #print(originalString, string, button)
    return string

def translateButtonStrength(string, button):
    buttons = {
        'fierce':     'HP',
        'strong':     'MP',
        'jab':        'LP',
        'roundhouse': 'HK',
        'ex':         'EX',
        'short':      'LK',
        'forward':    'MK'
    }
    string = string.lower()
    string = string.replace("short swing blow", "")
    for key, value in buttons.items():
        if key in string.lower():
            if key == 'ex':
                if button == 'p':
                    return 'PP'
                if button == 'k':
                    return 'KK'
                else:
                    return value
            else:
                return value

def stripInputPunct(string):
    return tools.removePunctuation(string).lower().replace("hold", "").rstrip().strip()

def findMoveByInput(moveDict, moveInput, button):
    keyList = []
    keyIdList = {}
    for key, values in moveDict.items():
        if 'Motion' not in values:
            continue
        keyList.append(stripInputPunct(values['Motion']))
        keyIdList[stripInputPunct(values['Motion'])] = key
    matchResult = match.extractOne(stripInputPunct(convertNumberNotation(moveInput, button)), keyList)
    return [keyIdList[matchResult[0]], matchResult[1]]

def findMoveByName(moveDict, moveName):
    keyList = []
    for key, value in moveDict.items():
        keyList.append(key)
    matchResult = match.extractOne(moveName, keyList)
    return matchResult

def getMoveName(name, moveDict, moveInput, prefix = ""):
    counter = 0
    testWords = ['medium', 'large', 'small']
    for i in range(len(testWords)):
        if testWords[i] in prefix.lower():
            counter += 1
    if counter > 1:
        prefixAll = prefix.replace(",", "").replace("/", "").split(" ")
    else:
        prefixAll = [prefix]
    resultArray = []
    for prefix in prefixAll:
        button = getMoveButton(moveInput)
        moveName = prefix + " " + name
        searchOutput = []
        moveKey = translateMoveName(moveName, button)
        matches = []
        matches.append(findMoveByName(moveDict, moveKey))
        if moveInput != "" and 'ducking' not in moveKey:
            matches.append(findMoveByInput(moveDict, moveInput, translateButtonStrength(moveKey, button)))
        selected = matches[0]
        for i in range(len(matches)):
            if selected[1] < matches[i][1]:
                selected = matches[i]
        resultsCheck = checkMatchStrongEnough(selected, moveName)
        if resultsCheck == -1:
           resultArray.append(moveKey)
        else:
            resultArray.append(resultsCheck)
    return resultArray

def checkMatchStrongEnough(matchResult, name):
    if matchResult[1] >= 0.6:
        checkList = ['short swing blow']
        if any(x in matchResult[0].lower() for x in checkList):
            buttons = ['fierce', 'strong', 'jab', 'roundhouse', 'forward', 'short', 'ex']
            for button in buttons:
                for check in checkList:
                    if (button in matchResult[0].lower().replace(check, "")) ^ (button in translateMoveName(name.lower().replace(check, ""), "").strip()):
                        print(get_color_escape(255, 0, 0) + "Could not match " + name + RESET)
                        return -1
        print(get_color_escape(0, 255, 0) + "Matched " + name + " and " + matchResult[0] + "!" + RESET)
        return matchResult[0]
    else:
        print(get_color_escape(255, 0, 0) + "Could not match " + name + RESET)
        return -1


def getMoveTableAsDictionary(soup, name, existingMoves, moveInput):
    button = getMoveButton(moveInput)
    tableDict = getTableAsDictionary(soup)
    outputDict = {}
    valueHeaders = []
    if tableDict[0][0].rstrip().strip() == 'input':
        for i in range(len(tableDict[0])):
            counter = 0
            while tableDict[counter][0] == tableDict[0][0]:
                counter += 1
            counter = counter - 1
            valueHeaders.append(gtTranslation(tableDict[counter][i].rstrip().strip(), 1))
        for key, value in tableDict.items():
            if key == 0 or value[0] == tableDict[0][0]:
                continue
            if value[0].lower().rstrip().strip() in ['supplement', 'make up']:
                break
            nameSearch = getMoveName(name.rstrip().strip(), existingMoves, moveInput, value[0].rstrip().strip())
            for i in range(len(nameSearch)):
                outputDict[nameSearch[i]] = {}
            for i in range(1, len(value)):
                try:
                    rowValue = w2n.word_to_num(value[i].rstrip().strip())
                except:
                    rowValue = value[i].rstrip().strip()
                for j in range(len(nameSearch)):
                    if nameSearch != -1:
                        moveName = nameSearch[j]
                    else:
                        return -1
                    outputDict[moveName][valueHeaders[i]] = str(rowValue)
    else:
        nameSearch = getMoveName(name.rstrip().strip(), existingMoves, moveInput)
        for i in range(len(nameSearch)):
            outputDict[nameSearch[i]] = {}
        for i in range(len(tableDict)):
            for j in range(len(tableDict[i])):
                if tableDict[i][j].rstrip().strip() in ['Occurrence', 'Sustain', 'Rigidity', 'Standing hit', 'Bend hit', 'guard']:
                    counter = 1
                    while tableDict[i + counter][j] == tableDict[i][j]:
                        counter += 1
                    try:
                        value = w2n.word_to_num(tableDict[i+counter][j].rstrip().strip())
                    except:
                        value = tableDict[i+counter][j]
                    for k in range(len(nameSearch)):
                        if nameSearch != -1:
                            moveName = nameSearch[k]
                        else:
                            return -1
                        outputDict[moveName][gtTranslation(tableDict[i][j].rstrip().strip(), 1)] = str(value)
    return outputDict


def newGetTableAsArray(soup):
    tableDict = getTableAsDictionary(soup)
    tableArray = []
    counter = 0
    for row in tableDict.values():
        tableArray.append([])
        for col in row:
            tableArray[counter].append(col)
        counter += 1
    return tableArray
                
    
def getTableAsArray(soup):
    output = []
    for tr in soup.findAll('tr'):
        row = []
        for td in tr.findAll('td'):
            if td.getText() not in ["", " ", None]:
                row.append(translator.translate(td.getText().rstrip().strip(), lang_src='jp', lang_tgt='en'))
            else:
                row.append(" ")
        if row != []:
            output.append(row)
    return output

def getPath(name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

def getMoveInput(soup):
    try:
        img = soup.find('img')
        filename = img['src']
        filename = filename.split("/")
        filename = filename[len(filename) - 1].split(".")[0]
        if 'jumping' in translator.translate(img.parent.getText()).lower():
            filename = "(Air) " + filename
        return filename
    except:
        return ""

def getMoveButton(string):
    if "p" in string:
        return "p"
    elif "k" in string:
        return "k"
    else:
        return ""

def getSaName(string, frameData):
    numeral = {
        'I': '1',
        'II': '2',
        'III': '3'
    }
    for key, value in frameData.items():
        if 'Super Art' in value:
            if numeral[value['Super Art']] == string:
                return key

def checkAgainstRestaurant(char, frameData):
    if char == 'akuma':
        char = 'gouki'
    baseUrl = "http://gr.qee.jp/01_3rd/kouryaku/"
    page = requests.get(baseUrl + char, headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, features='html.parser')
    linkTable = soup.find(id='menu')
    links = []
    for li in linkTable.findAll('li'):
        for subLi in li.findAll('li'):
            for a in subLi.findAll('a'):
                links.append(a['href'])
#    links = ["dudley_h5.html"]
    keys = []
    for key, values in frameData.items():
        keys.append(key)
    for i in range(len(links)):
        if '_tc' in links[i]:
            continue
        url = baseUrl + char + "/" + links[i]
        page = requests.get(url, headers=headers)
        page.encoding = 'utf-8'
        soup = BeautifulSoup(page.text, features='html.parser')
        counter = 0
        for titleTable in soup.findAll('table', {'class': 'summary50p1'}):
            counter += 1
            if counter % 2 == 0:
                continue
            if "_leap" in links[i]:
                name = "Universal Overhead"
            elif "_pa" in links[i]:
                name = "Taunt"
            elif "_sa" in links[i]:
                continue
                name = getSaName(links[i].replace(char + "_sa", "").replace(".html", ""), frameData)
            else:
                name = getTableAsArray(titleTable)[1][0].rstrip().strip()
            moveInput = getMoveInput(titleTable)
            classes = ['summary07p1', 'summary09p1', 'summary12p1', 'summary10p1']
            for j in range(len(classes)):
                table = titleTable.findNext('table', {'class': classes[j]})
                if table != None:
                    tmpTable = getMoveTableAsDictionary(table, name, frameData, moveInput)
                    if tmpTable == -1:
                        continue
                    for key, value in tmpTable.items():
                        if key != -1 and key not in frameData:
                            frameData[key] = {}
                            frameData[key]['Motion'] = convertNumberNotation(moveInput, translateButtonStrength(key, getMoveButton(moveInput)))
                        for key2, value2 in value.items():
                            if key != -1:
                                frameData[key][key2] = value2
    return frameData


#with open('/home/david/dev/8frames/frame-data/sf3/Oro.json') as json_file:
#    data = json.load(json_file)
#    checkAgainstRestaurant('oro', data)
#sys.exit()

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

#characters = {"Hugo": "http://wiki.shoryuken.com/Street_Fighter_3:_3rd_Strike/Hugo"}

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
                    frameData[moveName[i - 1]][tmpTable[0][j].rstrip().strip()] = tmpTable[i][j].rstrip().strip()
        if currentElement.findNext('p').getText().rstrip() == "Gauge Increase":
            currentElement = currentElement.findNext('p').findNext('table')                
        for i in range(len(moveName)):
            frameData[moveName[i]]['Image'] = moveImg
        if currentElement.findNext('img').findNext('h1') == None:
            break
    frameData = checkAgainstRestaurant(character.lower().replace("-", ""), frameData)
    with open(os.path.join(folder, character + ".json"), 'w') as outfile:
        json.dump(frameData, outfile, indent=4)
