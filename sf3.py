import tools
import os, discord, csv, string, re
from fuzzy_match import match, algorithims
from tabulate import tabulate

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sf3")

titles = [
    "Input",
    "Move Name",
    "Startup",
    "Active",
    "Recovery",
    "Adv. On Block",
    "Adv. On Hit",
    "Adv. On Hit (crouch)",
    "Guard",
    "Parry"
]

def parseCommand(command):
    character = tools.getMessagePrefix(command)
    content = translateAcronym(tools.getMessageContent(command))
    files = os.listdir(path)

    fuzzyMatch  = match.extractOne(character + ".csv", files)
    if fuzzyMatch[1] < 0.6:
        return "Could not find character '" + character + "'"
    file = path + "/" + fuzzyMatch[0]
    if content == "punishable":
        return getMinusMovesEmbed(getMinusMoves(file, 1), fuzzyMatch[0][:-4]) 
    elif content == "lose turn":
        return getMinusMovesEmbed(getMinusMoves(file, 0), fuzzyMatch[0][:-4])
    else:
        rawSearch = []
        rawSearch.append(getStoredRowByInput(content, file))
        rawSearch.append(getStoredRowByName(content, file))
        row = rawSearch[0]
        for i in range(len(rawSearch)):
            if rawSearch[i] == -1:
                continue
            if row == -1 or rawSearch[i][1] > row[1]:
                row = rawSearch[i]

        if row == -1 or row[1] < 0.3:
            return "Couldnt find move '" + content + "'"
        return createSingleMoveEmbed(row[0], fuzzyMatch[0][:-4])

def getStoredRowByInput(search, file):
    return getStoredRowNthValue(search, file, 0)

def getStoredRowByName(search, file):
    return getStoredRowNthValue(search, file, 1)

def getStoredRowNthValue(search, file, n):
    try:
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='`')
            line_count = 0
            search = tools.removePunctuation(str(search))
            moveData = {}
            moveKeys = []
            counter = 0
            for row in csv_reader:
                if len(row) <= 0:
                    continue
                moveKeys.append(row[n].translate(str.maketrans('', '', string.punctuation)))
                moveData[moveKeys[counter]] = row
                if moveKeys[counter] == search:
                    return row
                counter += 1
            matchCheck = match.extractOne(search, moveKeys)
            return [moveData[matchCheck[0]], matchCheck[1]]
    except:
        return -1

def createSingleMoveEmbed(row, character):
    e = discord.Embed(title=character)
    for i in range(len(row) - 1):
        if len(row[i]) < 1:
            row[i] = "-"
        e.add_field(
            name=titles[i],
            value=row[i]
        )
    try:
        e.set_image(url=row[len(row)-1])
    except:
        pass
    return e

def getMinusMoves(file, punishable = 0):
#try:
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='`')
        moves = []
        minimum = 0
        maximum = 0
        blockColumn = 5
        if punishable == 0:
            minimum = -1
            maximum = -1
        elif punishable == 1:
            minimum = -2
            maximum = -200
        else:
            return -1
        for row in csv_reader:
            if len(row) <= 0 or row[blockColumn] in ["", None]:
                continue
            oB = row[blockColumn].replace("~", "").split("/")
            for i in range(len(oB)):
                oB[i] = oB[i].replace("+", "").strip()
                try:
                    int(oB[i])
                except:
                    continue
                if int(oB[i]) <= minimum and int(oB[i]) >= maximum:
                    moves.append(row)
                    break
    return moves

def getMinusMovesEmbed(data, character):
    headers = [titles[0], titles[5]]
    embedArray = []
    offset = 0
    finished = 0
    listSize = 30
    while(True):
        stringArray = []
        for i in range(offset, offset + listSize):
            if i >= len(data):
                finished = 1
                break
            stringArray.append([data[i][1], data[i][5]])
        embedArray.append("```" + tabulate(stringArray, headers=headers) + "```")
        offset += listSize
        if finished == 1:
            break
    return embedArray

def translateAcronym(text):
    text = text.lower()
    if re.match(r"tc[0-9]+", text):
        text = text.replace("tc", "Target Combo ")
    if "dp " in text.lower():
        text = text.replace("dp", "fddf")
    return text

