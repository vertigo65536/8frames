import tools
import os, discord, string, re, json
from fuzzywuzzy import process, fuzz
from tabulate import tabulate

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sf4")

titles = [
    'Input',
    'Move Name',
    'Nickname',
    'Damage',
    'Stun',
    'Meter Gain',
    'Hit Level',
    'Cancel Ability',
    'Startup',
    'Active',
    'Recovery',
    'On Block',
    'On Hit'
]

def getButton(string):
    buttons = {
        ' Jab': "LP",
        ' Strong': "MP",
        ' Fierce': "HP",
        ' Short': "LK",
        ' Forward': "MK",
        ' Roundhouse': "HK",
        ' EX': "EX"}
    for key, value in buttons.items():
        string = string.replace(value + " Ex", value)
        if any(x in string for x in [key, value]):
            return value
    return None

def parseCommand(command):
    character = tools.getMessagePrefix(command)
    content = translateAcronym(tools.getMessageContent(command)).replace(" ", "")
    files = os.listdir(path)

    fuzzyMatch  = process.extractOne(character, files, scorer=fuzz.partial_ratio)
    if fuzzyMatch[1] < 60:
        return "Could not find character '" + character + "'"
    file = path + "/" + fuzzyMatch[0]
    character = fuzzyMatch[0].replace(".json", "")
    if content.lower() == "punishable":
        return getPunishable(file, character, 1)
    if content.lower() == "loseturn":
        return getPunishable(file, character, 0)
    searchOutput = []
    searchOutput.append(getMoveByValue(content, file, "input"))
    searchOutput.append(getMoveByValue(content, file, "moveType"))
    searchOutput.append(getMoveByName(content, file))
    outputValue = searchOutput[0]
    for i in range(len(searchOutput)):
        if searchOutput[i] == -1:
            continue
        if searchOutput[i][2] > outputValue[2]:
            outputValue = searchOutput[i]
    return getMoveEmbed(outputValue[0], outputValue[1], character)

def getMoveByName(query, f):
    query = removePunctuation(query)
    try:
        with open(f) as json_file:
            moveList = json.load(json_file)
            keyList = {}
            keyArray = []
            for key, row in moveList['moves'].items():
                keyArray.append(removePunctuation(key))
                keyList[removePunctuation(key)] = key
            fuzzyMatch  = process.extractOne(query, keyArray, scorer=fuzz.token_sort_ratio)
            return [moveList['moves'][keyList[fuzzyMatch[0]]], keyList[fuzzyMatch[0]], fuzzyMatch[1]]
    except:
        return -1
   

def getMoveByValue(query, f, moveId):
    query = removePunctuation(query)
    try:
        with open(f) as json_file:
            moveList = json.load(json_file)
            keyList = {}
            keyArray = []
            for key, row in moveList['moves'].items():
                if moveId not in row:
                    continue
                keyArray.append(removePunctuation(row[moveId]))
                keyList[removePunctuation(row[moveId])] = key
            fuzzyMatch  = process.extractOne(query, keyArray, scorer=fuzz.token_sort_ratio)
            return [moveList['moves'][keyList[fuzzyMatch[0]]], keyList[fuzzyMatch[0]], fuzzyMatch[1]]
    except:
        return -1

def getMoveEmbed(moveRow, moveName, character):
    e = discord.Embed(title=character)
    e.add_field(name = "Name", value = moveName)
    for title, value in moveRow.items():
        e.add_field(
            name = title,
            value = str(value).replace("*", "•")
        )
    return e

def getPunishable(f, character, punishable = 0):
    with open(f) as json_file:
        moveList = json.load(json_file)['moves']
        moves = []
        minimum = 0
        maximum = 0
        if punishable == 0:
            minimum = -1
            maximum = -2
        elif punishable == 1:
            minimum = -3
            maximum = -200
        else:
           return -1
        oBHeader = 'onBlock'
        for key, move in moveList.items():
            oB = move[oBHeader]
            oB = str(oB).split("[")
            for i in range(len(oB)):
                try:
                    int(oB[i])
                except:
                    continue
                oB[i].replace("]", "")
                if int(oB[i]) <= minimum and int(oB[i]) >= maximum:
                    moves.append([key, move[oBHeader]])
                    break
    e = discord.Embed(title=character)
    headers = ['Name', oBHeader]
    embedArray = []
    offset = 0
    finished = 0
    listSize = 41
    while(True):
        stringArray = []
        for i in range(offset, offset + listSize):
            if i >= len(moves):
                finished = 1
                break
            stringArray.append([moves[i][0], moves[i][1]])
        embedArray.append("```" + tabulate(stringArray, headers=headers) + "```")
        offset += listSize
        if finished == 1:
            break
    return embedArray
 
def translateAcronym(text):
    text = str(text).lower()
    if re.match(r"tc[0-9]+", text):
        text = text.replace("tc", "target combo ")
    if re.search(r"rekka [0-9]+", text) or  re.search(r"rekkaken [0-9]+", text):
        text = text.replace("rekka", "rekka part")
        text = text.replace("rekkaken", "rekkaken part")
        text = text.replace("part 1", "")
    return text

def removePunctuation(text):
    return re.sub('['+string.punctuation.replace(">", "")+']', '', text).lower()
