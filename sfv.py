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
    #print(frameData['Alex']['moves']['normal']['Stand LP'])
    character = fuzzyDict(character, frameData)
    dataType = 'moves'
    vtTest = content.split(":")
    vtrigger = 'normal'
    if len(vtTest) == 1 or vtTest[0].lower() == 'normal':
        vtrigger = 'normal'
        if len(vtTest) == 1:
            search = vtTest
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
    for key in d.keys():
       keyArray.append(key)
    selectedKey = match.extractOne(search, keyArray)
    if selectedKey[1] >= 0.7:
        return selectedKey[0]
    else:
        return -1

def findByPlnCmd(search, d):
    plnArray = []
    keyDict = {}
    for key in d.keys():
        plnArray.append(d[key]['plnCmd'].translate(str.maketrans('', '', string.punctuation)).lower())
        keyDict[d[key]['plnCmd'].translate(str.maketrans('', '', string.punctuation)).lower()] = key
    selectedKey = match.extractOne(search, plnArray)
    if selectedKey[1] >= 0.7:
        return keyDict[selectedKey[0]]
    else:
        return -1

def createMoveEmbed(dictionary, title, description):
    e = discord.Embed(title=title.title(), description=description.title())
    for key, value in dictionary.items():
        e.add_field(
            name = key,
            value = value
        )
    return e
