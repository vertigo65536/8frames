import tools
import os, discord, json, re, string
from fuzzy_match import match, algorithims
from tabulate import tabulate

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "t7")

def parseCommand(command):
    character = parseAlias(tools.getMessagePrefix(command))
    content = tools.getMessageContent(command)
    files = os.listdir(path)

    fuzzyMatch  = match.extractOne(character + ".json", files)
    if fuzzyMatch[1] < 0.8:
        return "Could not find character '" + character + "'"
    file = path + "/" + fuzzyMatch[0]
    if content == "punishable":
        return getMinusMovesEmbed(getMinusMoves(file, 1), fuzzyMatch[0][:-4]) 
    elif content == "lose turn":
        return getMinusMovesEmbed(getMinusMoves(file, 0), fuzzyMatch[0][:-4])
    else:
        #row = tools.getStoredRowByInput(content, file)
        searchOutput = []
        searchOutput.append(findMoveByKey(content, file))
        outputValue = searchOutput[0]
        for i in range(len(searchOutput)):
            if searchOutput[i][2] > outputValue[2]:
                outputValue = searchOutput[i]
        return createSingleMoveEmbed(outputValue[0], outputValue[1], fuzzyMatch[0][:-5])

def findMoveByKey(query, f):
#    try:
    with open(f) as json_file:
        moveList = json.load(json_file)
        keyList = {}
        keyArray = []
        query = re.sub('['+string.punctuation.replace("+", "")+']', '', query).replace(" ", "")
        for key, row in moveList.items():
            editedKey = re.sub('['+string.punctuation.replace("+", "")+']', '', key).replace(" ", "")

            keyArray.append(editedKey)
            keyList[editedKey] = key
        fuzzyMatch  = match.extractOne(query, keyArray)
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
        
def getMinusMoves(file, punishable = 0):
#try:
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='`')
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
        for row in csv_reader:
            if len(row) <= 0 or row[4] in ["", None]:
                continue
            try:
                oB = row[4].split("~")
                if (len(oB) == 1):
                    continue
            except:
                oB = [row[4]]
            for i in range(len(oB)):
                try:
                    int(oB[i])
                except:
                    continue
                if int(oB[i]) < minimum and int(oB[i]) > maximum:
                    moves.append(row)
                    break
    return moves

def getMinusMovesEmbed(data, character):
    e = discord.Embed(title=character)
    titles = getColumnHeaders()
    headers = [titles[0], titles[4]]
    embedArray = []
    offset = 0
    finished = 0
    listSize = 30
    while(True):
        stringArray = []
        for i in range(offset, offset + listSize - 1):
            if i >= len(data):
                finished = 1
                break
            stringArray.append([data[i][0], data[i][4]])
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
    else:
        return name
