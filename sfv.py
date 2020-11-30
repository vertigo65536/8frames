import tools
import os, discord, json, string
from fuzzy_match import match, algorithims
from tabulate import tabulate

sfvFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fatsfvframedatajson/sfv.json")

def getFrameDataArray():
    jsonFile = open(sfvFile, 'r')
    return json.loads(jsonFile.read())

def parseCommand(command):
    character = tools.getMessagePrefix(command)
    content = tools.getMessageContent(command)
    frameData = getFrameDataArray()
    character = fuzzyDict(character, frameData)
    if character == -1:
        return "Could not find character"
    dataType = 'moves'
    if content.lower() == "punishable":
        return getMinusMovesEmbed(character, 1)
    if content.lower() == "lose turn":
        return getMinusMovesEmbed(character, 0)
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
    dataKey = findByPlnCmd(search, frameData[character][dataType][vtrigger])
    if dataKey == -1:
        dataKey = findByPlnCmd(search, frameData[character][dataType]['normal'])
        if dataKey == -1:
            return "Could not find move"
        else:
            vtrigger = "normal"
    return createMoveEmbed(frameData[character][dataType][vtrigger][dataKey], character, vtrigger)

def fuzzyDict(search, d):
    keyArray = []
    keyDict = {}
    for key in d.keys():
       keyArray.append(removePunctuation(key))
       keyDict[removePunctuation(key)] = key
    selectedKey = match.extractOne(search, keyArray)
    if selectedKey[1] >= 0.7:
        return keyDict[selectedKey[0]]
    else:
        return -1

def findByPlnCmd(search, d):
    search = removePunctuation(search).replace("st", "").replace("dp", "fddf")
    #if search in ["vs1", "vs2"]:
    if any(x in search for x in ["vs1", "vs2"]):
        search = search.replace("vs", "mpmk vs")
    elif any(x in search for x in ["vt1", "vt2"]):
        search = search.replace("vt", "hphk vt")
    plnArray = []
    keyDict = {}
    for key in d.keys():
        plnArray.append(removePunctuation(d[key]['plnCmd']))
        keyDict[removePunctuation(d[key]['plnCmd'])] = key
    selectedKey = match.extractOne(search, plnArray)
    if selectedKey[1] >= 0.7:
        return keyDict[selectedKey[0]]
    else:
        return -1

def getMinusMoves(character, punishable=0):
    array = getFrameDataArray()[character]['moves']
    outputValues = {}
    if punishable == 1:
        minimum = -3
        maximum = -2000
    else:
        minimum = -1
        maximum = -2
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
                if int(block[i]) <= minimum and int(block[i]) >= maximum:
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
    return outputValues

def getMinusMovesEmbed(character, punishable=0):
    d = getMinusMoves(character, punishable)
    e = discord.Embed(title=character)
    headers = ["Move", "On Block", "VTC On Block"]
    string = []
    counter = 0
    for key, items in d.items():
        valuesArray = []
        for i in range(len(items)):
            try:
                valuesArray.append([items[i]['move'], items[i]['onBlock'], items[i]['vtcOnBlock']])
            except:
                valuesArray.append([items[i]['move'], items[i]['onBlock'], ""])
        if valuesArray != []:
            string.append("**" + key + "**\n" + "```" + tabulate(valuesArray, headers=headers) + "```")
    return string

def createMoveEmbed(dictionary, title, description):
    e = discord.Embed(title=title.title(), description=description.title())
    for key, value in dictionary.items():
        if len(str(value)) > 1024:
            continue
        e.add_field(
            name = key,
            value = value
        )
    return e

def removePunctuation(s):
   return s.translate(str.maketrans('', '', string.punctuation)).lower().replace(" ", "")
