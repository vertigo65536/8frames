import tools, os, re, discord, json
from fuzzywuzzy import fuzz

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfv")
punct = "!@#$%^&*()[]{};:,./<>?\|`~-=_"
replacePunct = " "
game = "sfv"
headers = {
    'moveName': 'Name',
    'plnCmd': 'Input',
    'startup': 'Startup',
    'active': 'Active',
    'recovery': 'Recovery',
    'total': 'Total Frames',
    'onHit': 'On Hit',
    'onBlock': 'On Block',
    'vtc1OnHit': 'Frames oH VT1 Cancel',
    'vtc1OnBlock': 'Frames oB VT1 Cancel',
    'vtc2OnHit': 'Frames oH VT2 Cancel',
    'vtc2OnBlock': 'Frames oB VT2 Cancel',
    'stun': 'Stun',
    'attackLevel': 'Attack Level',
    'damage': 'Damage',
    'cancelsTo': 'Cancels To',
    'extraInfo': 'Extra Info'
    }


def getPath():
    return path

def getGame():
    return game

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
    search = translateMoveAcronym(search)
    types = [vtrigger, 'normal']
    for i in range(len(types)):
        dataRaw = []
        punctuation = [punct, replacePunct]
        scorer = fuzz.ratio
        dataRaw.append(tools.searchMove(search, characterFile, 'plnCmd', punct, scorer, ['moves', types[i]], types[i]+":"))
        dataRaw.append(tools.searchMove(tools.formatAsSFInput(search), characterFile, 'plnCmd', punct, scorer, ['moves', types[i]], types[i]+":"))
        dataRaw.append(tools.searchMove(search, characterFile, 'key', punct, fuzz.token_sort_ratio, ['moves', types[i]], types[i]+":"))
        invalidCounter = 0
        for j in range(len(dataRaw)):
            if dataRaw[j] == -1:
                invalidCounter += 1
        if invalidCounter < len(dataRaw)-1:
            break
    return dataRaw

def getMoveByKey(content, characterFile):
    return tools.getByKey(content, characterFile, ['moves'])

def getPunishable(f, character, punishable=0):
    array = tools.loadJsonAsDict(f)['moves']
    outputValues = {}
    try:
        limits = tools.getLimits(game)[punishable]
        minimum = limits['min']
        maximum = limits['max']
        
    except:
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

def getPunish(f, character, startupQuery):
    moveList = tools.loadJsonAsDict(f)['moves']
    moves = []
    startup = 'startup'
    for vt, moveSubList in moveList.items():
        for key, move in moveSubList.items():
            if 'Jump' in key:
                continue
            if not startup in move:
                continue
            startupVal = move[startup]
            startupVal = str(startupVal).replace("~", "[").replace("/", "[").replace("～", "[")
            startupVal = str(startupVal).split("[")
            for i in range(len(startupVal)):
                startupVal[i] = startupVal[i].rstrip().strip()
                try:
                    int(startupVal[i])
                except:
                    continue
                startupVal[i].replace("]", "")
                if int(startupVal[i]) <= startupQuery:
                    if vt == 'normal':
                        moveName = key
                    else:
                        moveName = vt + " " + key
                    moves.append([moveName, move[startup]])
                    break
    return [moves, ['Name', startup]]

def getNote(f, character, query):
    moveList = tools.loadJsonAsDict(f)['moves']
    try:
        searchQuery = tools.loadJsonAsDict('searchJsons/searchParam.json')[game][query]
    except:
        return -1
    moves = []
    header = "extraInfo"
    for vt, moveSubList in moveList.items():
        for key, move in moveSubList.items():
            if not header in move:
                continue
            for i in range(len(move[header])):
                for j in range(len(searchQuery)):
                    if searchQuery[j].lower() in move[header][i].lower():
                        if "not " + searchQuery[j].lower() in move[header][i].lower():
                            continue
                        if vt != 'normal':
                            name = vt + ": " + key
                        else:
                            name = key
                        moves.append([name, move[header][i]])
                        break
    return [moves, ['Name', header]]


def translateAlias(name):
    return name

def translateAcronym(name):
    return name

def translateMoveAcronym(search):
    if any(x in search for x in ["vs1", "vs2"]):
        search = search.replace("vs", "mpmk vs")
    elif any(x in search for x in ["vt1", "vt2"]):
        search = search.replace("vt", "hphk vt")
    return search

def getMoveEmbed(moveRow, moveName, character):
    e = discord.Embed(title=character)
    e.add_field(
        name = "Name",
        value = moveName
    )
    for key, value in moveRow.items():
        if key in ['moveName', 'numCmd', 'cmnName', 'moveMotion', 'moveButton', 'i', 'followUp', 'airmove', 'projectile', 'moveType']:
            continue
        if len(str(value)) > 1024:
            continue
        if value in ['', None]:
            value = 'n/a'
        try:
            header = headers[key]
        except:
            header = key
        e.add_field(
            name = header,
            value = value
        )
    return e

def getBadPunctuation():
   return punct
