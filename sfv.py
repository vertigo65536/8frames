import tools, os, re, discord, json
from fuzzywuzzy import fuzz

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfv")
punct = "!@#$%^&*()[]{};:,./<>?\|`~-=_"
replacePunct = " "

def getPath():
    return path

def getPossibleMoves(content, characterFile, extraLevels=[]):
    vtTest = content.split(":")
    vtrigger = 'normal'
    if len(vtTest) == 1 or vtTest[0].lower() == 'normal':
        vtrigger = 'normal'
        if len(vtTest) == 1:
            search = vtTest[0]
        else:
            search = vtTest[1]
    elif vtTest[0].lower() in ['vt1', 'vtone', 1]:
        vtrigger = 'vtOne'
        search = vtTest[1]
    elif vtTest[0].lower() in ['vt2', 'vttwo', 2]:
        vtrigger = 'vtTwo'
        search = vtTest[1]
    else:
        return "Invalid vtrigger activation. Try vt1:<command> or remove colon"
    types = [vtrigger, 'normal']
    for i in range(len(types)):
        dataRaw = []
        punctuation = [punct, replacePunct]
        scorer = fuzz.token_sort_ratio
        dataRaw.append(tools.searchMove(search, characterFile, 'plnCmd', punct, scorer, ['moves', types[i]]))
        dataRaw.append(tools.searchMove(search, characterFile, 'key', punct, scorer, ['moves', types[i]]))
        invalidCounter = 0
        for j in range(len(dataRaw)):
            if dataRaw[j] == -1:
                invalidCounter += 1
        if invalidCounter < len(dataRaw)-1:
            break
    dataKey = dataRaw[0]
    for i in range(len(dataRaw)):
        if dataRaw[i][2] > dataKey[2]:
            dataKey = dataRaw[i]
    if dataKey == -1 or dataKey[2] < 25:
        return "Could not find move"
    else:
        vtrigger = 'normal'
    return dataRaw

def getPunishable(f, character, punishable=0):
    with open(f) as json_file:
        array = json.load(json_file)['moves']
        outputValues = {}
        if punishable == 1:
            minimum = -200
            maximum = -3
        elif punishable == 0:
            minimum = -2
            maximum = -1
        elif punishable == 2:
            minimum = -2
            maximum = 200
        elif punishable == 3:
            minimum = 1
            maximum = 200
        else:
            return -1
        for vt, moves in array.items():
            outputValues[vt] = []
            for key, move in moves.items():
                try:
                    block = move['onBlock']
                    block = str(block).replace("/", "(").split("(")
                    if not isinstance(block, list):
                        block = [block]
                except:
                    continue
                for i in range(len(block)):
                    block[i] = block[i].replace(")", "")
                    try:
                        int(block[i])
                    except:
                        continue
                    if int(block[i]) >= minimum and int(block[i]) <= maximum:
                        try:
                            outputValues[vt].append({
                                'move': key,
                                'onBlock': move['onBlock'],
                                'vtcOnBlock': move['vtcOnBlock']
                            })
                        except:
                            outputValues[vt].append({
                                'move': key,
                                'onBlock': move['onBlock']
                            })

                        break
    outputArray = []
    for key, value in outputValues.items():
        if value == []:
            continue
        for i in range(len(value)):
            tmpRow = []
            for subKey, subValue in value[i].items():
                if subKey == 'move' and key != 'normal':
                    subValue = key + " " + subValue
                tmpRow.append(subValue)
            outputArray.append(tmpRow)
    return [outputArray, ['Name', 'oB', 'Vtc oB']]


def translateAlias(name):
    return name

def translateAcronym(search):
    if any(x in search for x in ["vs1", "vs2"]):
        search = search.replace("vs", "mpmk vs")
    elif any(x in search for x in ["vt1", "vt2"]):
        search = search.replace("vt", "hphk vt")
    return search

def getMoveEmbed(moveRow, moveName, character):
    e = discord.Embed(title=character)
    e.add_field(
        name = "Move",
        value = moveName
    )
    for key, value in moveRow.items():
        if value in ['', None]:
            value = 'n/a'
        e.add_field(
            name = key,
            value = value
        )
    return e

def getBadPunctuation():
   return punct
