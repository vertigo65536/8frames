import tools
import os, discord, string, re, json
from fuzzywuzzy import process, fuzz
from tabulate import tabulate

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sf3")

def parseCommand(command):
    character = tools.getMessagePrefix(command)
    content = translateAcronym(tools.getMessageContent(command))
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
    content = tools.removePunctuation(content)
    searchOutput.append(getMoveByValue(content, file, "Motion"))
    searchOutput.append(getMoveByName(content, file))
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
                keyArray.append(tools.removePunctuation(key))
                keyList[tools.removePunctuation(key)] = key
            fuzzyMatch  = process.extractOne(query, keyArray, scorer=fuzz.token_sort_ratio)
            return [moveList[keyList[fuzzyMatch[0]]], keyList[fuzzyMatch[0]], fuzzyMatch[1]]
    except:
        return -1
   

def getMoveByValue(query, f, moveId):
    try:
        query = query.replace(" ", "")
        with open(f) as json_file:
            moveList = json.load(json_file)
            keyList = {}
            keyArray = []
            for key, row in moveList.items():
                keyArray.append(tools.removePunctuation(row[moveId]).replace(" ", ""))
                keyList[tools.removePunctuation(row[moveId]).replace(" ", "")] = key
            fuzzyMatch  = process.extractOne(query, keyArray, scorer=fuzz.token_sort_ratio)
            return [moveList[keyList[fuzzyMatch[0]]], keyList[fuzzyMatch[0]], fuzzyMatch[1]]
    except:
        return -1

def getMoveEmbed(moveRow, moveName, character):
    e = discord.Embed(title=character)
    e.add_field(name = "Name", value = moveName)
    for title, value in moveRow.items():
        if title != 'Image':
            e.add_field(
                name = title,
                value = value
            )
    try:
        e.set_image(url=moveRow['Image'])
    except:
        pass
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
        oBHeader = 'Blocked Advantage'
        for key, move in moveList.items():
            if not oBHeader in move:
                continue
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
    if "dp" in text:
        text = text.replace("dp", "fddf")
    return text
