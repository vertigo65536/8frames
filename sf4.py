import tools
import os, discord, string, re, json
from fuzzy_match import match, algorithims
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
    if character.lower() == "gen":
        return "Use GenMantis or GenCrane"
    content = translateAcronym(tools.getMessageContent(command)).replace(" ", "")
    files = os.listdir(path)

    fuzzyMatch  = match.extractOne(character + ".json", files)
    if fuzzyMatch[1] < 0.6:
        return "Could not find character '" + character + "'"
    file = path + "/" + fuzzyMatch[0]
    character = fuzzyMatch[0].replace(".json", "")
    if content.lower() == "punishable":
        return getPunishable(file, character, 1)
    if content.lower() == "loseturn":
        return getPunishable(file, character, 0)
    searchOutput = []
    if "genei" not in content:
        searchOutput.append(getMoveByValue(content, file, "Input"))
    searchOutput.append(getMoveByName(content, file))
    searchOutput.append(getMoveByValue(content, file, "Nickname"))
    outputValue = searchOutput[0]
    for i in range(len(searchOutput)):
        if searchOutput[i][2] > outputValue[2]:
            outputValue = searchOutput[i]
    return getMoveEmbed(outputValue[0], outputValue[1], character)

def getMoveByName(query, f):
    try:
        with open(f) as json_file:
            moveList = json.load(json_file)
            keyList = {}
            keyArray = []
            for key, row in moveList.items():
                if "genei" not in query.lower() and "genei" in key.lower():
                    continue
                keyArray.append(tools.removePunctuation(key))
                keyList[tools.removePunctuation(key)] = key
            fuzzyMatch  = match.extractOne(query, keyArray)
            return [moveList[keyList[fuzzyMatch[0]]], keyList[fuzzyMatch[0]], fuzzyMatch[1]]
    except:
        return -1
   

def getMoveByValue(query, f, moveId):
    try:
        with open(f) as json_file:
            moveList = json.load(json_file)
            keyList = {}
            keyArray = []
            for key, row in moveList.items():
                if "genei" not in query.lower() and "genei" in key.lower():
                    continue
                keyArray.append(tools.removePunctuation(row[moveId]))
                keyList[tools.removePunctuation(row[moveId])] = key
            fuzzyMatch  = match.extractOne(query, keyArray)
            return [moveList[keyList[fuzzyMatch[0]]], keyList[fuzzyMatch[0]], fuzzyMatch[1]]
    except:
        return -1

def getMoveEmbed(moveRow, moveName, character):
    e = discord.Embed(title=character)
    e.add_field(name = "Name", value = moveName)
    for title, value in moveRow.items():
        e.add_field(
            name = title,
            value = value
        )
    return e

def getPunishable(f, character, punishable = 0):
    with open(f) as json_file:
        moveList = json.load(json_file)
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
        oBHeader = 'Adv OnGuard'
        for key, move in moveList.items():
            oB = move[oBHeader]
            oB = oB.split("[")
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
    return text.translate(str.maketrans('', '', string.punctuation)).rstrip().replace("+", "").lower().replace(" ", "")
