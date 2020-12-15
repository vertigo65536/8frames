import tools
import os, discord, json, re, string
from fuzzy_match import match, algorithims
from tabulate import tabulate

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "t7")

def parseCommand(command):
    character = parseAlias(tools.getMessagePrefix(command))
    content = tools.getMessageContent(command)
    files = os.listdir(path)

    fuzzyMatch  = match.extractOne(character + ".json", files, match_type='levenshtein')

    if fuzzyMatch[1] < 0.8:
        return "Could not find character '" + character + "'"
    character = fuzzyMatch[0][:-5]
    file = path + "/" + fuzzyMatch[0]
    if content == "punishable":
        return getMinusMoves(file, character, 1) 
    elif content == "lose turn":
        return getMinusMoves(file, character, 0)
    else:
        #row = tools.getStoredRowByInput(content, file)
        searchOutput = []
        searchOutput.append(findMoveByKey(content, file))
        outputValue = searchOutput[0]
        for i in range(len(searchOutput)):
            if searchOutput[i][2] > outputValue[2]:
                outputValue = searchOutput[i]
        return createSingleMoveEmbed(outputValue[0], outputValue[1], character)

def findMoveByKey(query, f):
#    try:
    with open(f) as json_file:
        moveList = json.load(json_file)
        keyList = {}
        keyArray = []
        query = re.sub('['+string.punctuation.replace("+", "")+']', '', query).replace(" ", "").lower()
        for key, row in moveList.items():
            editedKey = re.sub('['+string.punctuation.replace("+", "")+']', '', key).replace(" ", "").lower()

            keyArray.append(editedKey)
            keyList[editedKey] = key
        fuzzyMatch  = match.extractOne(query, keyArray, match_type='levenshtein')
        return [moveList[keyList[fuzzyMatch[0]]], keyList[fuzzyMatch[0]], fuzzyMatch[1]]
#    except:
        return -1
 
def createSingleMoveEmbed(dataDict, moveName, character):
    e = discord.Embed(title=character)
    e.add_field(
        name = "Move",
        value = moveName
    )
    for key, value in dataDict.items():
        if value in ['', None]:
            value = 'n/a'
        e.add_field(
            name = key,
            value = value
        )
    return e
        
def getMinusMoves(f, character, punishable = 0):
    with open(f) as json_file:
        moveList = json.load(json_file)
        moves = []
        minimum = 0
        maximum = 0
        if punishable == 0:
            minimum = 0
            maximum = -9
        elif punishable == 1:
            minimum = -9
            maximum = -200
        else:
            return -1
        oBHeader = 'Block frame'
        for key, move in moveList.items():
            try:
                move[oBHeader]
            except:
                continue
            oB = move[oBHeader]
            oB = str(oB).replace("~", "[").split("[")
            for i in range(len(oB)):
                oB[i] = oB[i].replace("]", "")
                try:
                    int(oB[i])
                except:
                    continue
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
        if stringArray != []:
            embedArray.append("```" + tabulate(stringArray, headers=headers) + "```")
        offset += listSize
        if finished == 1:
            break
    return embedArray

def parseAlias(name):
    if name.lower() == "ak":
        return "Armor King"
    if name.lower() == "dj":
        return "Devil Jin"
    if name.lower() == "violet":
        return "Lee"
    if name.lower() == "panda":
        return "Kuma"
    if name.lower() == "tiger":
        return "Eddy"
    if name.lower() == "zaf":
        return "Zafina"
    else:
        return name
