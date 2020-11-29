import tools
import os, discord, csv
from fuzzy_match import match, algorithims
from tabulate import tabulate

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "t7")

def getColumnHeaders():
    return [
        "Command",
        "Hit Level",
        "Damage",
        "Start up Frame",
        "Block Frame",
        "Hit Frame",
        "Counter Hit Frame",
        "Notes"
        ]

def parseCommand(command):
    character = parseAcronyms(tools.getMessagePrefix(command))
    content = tools.getMessageContent(command)
    files = os.listdir(path)

    fuzzyMatch  = match.extractOne(character + ".csv", files)
    if fuzzyMatch[1] < 0.8:
        return "Could not find character '" + character + "'"
    file = path + "/" + fuzzyMatch[0]
    if content == "punishable":
        return getMinusMovesEmbed(getMinusMoves(file, 1), fuzzyMatch[0][:-4]) 
    elif content == "lose turn":
        return getMinusMovesEmbed(getMinusMoves(file, 0), fuzzyMatch[0][:-4])
    else:
        row = tools.getStoredRowByInput(content, file)
        if row == -1:
            return "Couldnt find move '" + content + "'"
        return createSingleMoveEmbed(row, fuzzyMatch[0][:-4])

def createSingleMoveEmbed(dataArray, character):
    e = discord.Embed(title=character)
    titles = getColumnHeaders()
    for i in range(len(dataArray)):
        if dataArray[i] in ["", None]:
            dataArray[i] = "n/a"
        e.add_field(
            name = titles[i],
            value = dataArray[i]
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
    listSize = 40
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

def parseAcronyms(name):
    if name.lower() == "ak":
        return "Armor King"
    if name.lower() == "dj":
        return "Devil Jin"
    else:
        return name
