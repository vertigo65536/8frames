import tools
import os, discord, string, csv, re
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
    content = translateAcronym(tools.getMessageContent(command))
    files = os.listdir(path)

    fuzzyMatch  = match.extractOne(character + ".csv", files)
    if fuzzyMatch[1] < 0.6:
        return "Could not find character '" + character + "'"
    file = path + "/" + fuzzyMatch[0]
    character = fuzzyMatch[0].replace(".csv", "")
    if content.lower() == "punishable":
        return getPunishable(file, character, 1)
    if content.lower() == "lose turn":
        return getPunishable(file, character, 0)
    searchOutput = []
    searchOutput.append(getMoveByCommand(content, file))
    searchOutput.append(getMoveByName(content, file))
    searchOutput.append(getMoveByNickname(id, file))
    outputValue = searchOutput[0]
    for i in range(len(searchOutput)):
        if searchOutput[i][1] > outputValue[1]:
            outputValue = searchOutput[i]
    return getMoveEmbed(outputValue[0], character)

def getMoveByCommand(id, file):
    return getMoveByNthKey(id, file, 0)

def getMoveByName(id, file):
    return getMoveByNthKey(id, file, 1)

def getMoveByNickname(id, file):
    return getMoveByNthKey(id, file, 2)

def getMoveByNthKey(id, file, n):
    try:
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='`')
            line_count = 0
            id = removePunctuation(str(id))
            moveData = {}
            moveKeys = []
            counter = 0
            for row in csv_reader:
                if len(row) <= 0:
                    continue
                moveKeys.append(removePunctuation(row[n]))
                moveData[moveKeys[counter]] = row
                #if moveKeys[counter] == id:
                #    return row
                counter += 1
            matchOutput = match.extractOne(id, moveKeys)
            return [moveData[matchOutput[0]], matchOutput[1]]
    except:
        return -1

def getMoveEmbed(moveRow, character):
    e = discord.Embed(title=character)
    for i in range(len(moveRow)):
        e.add_field(
            name = titles[i],
            value = moveRow[i]
        )
    return e

def getPunishable(file, character, punishable = 0):
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='`')
        moves = []
        minimum = 0
        maximum = 0
        oBKey = 11
        if punishable == 0:
            minimum = -1
            maximum = -2
        elif punishable == 1:
            minimum = -3
            maximum = -200
        else:
           return -1
        for row in csv_reader:
            if len(row) <= 0 or removePunctuation(row[oBKey]) in ["", None]:
                continue
            oB = row[oBKey]
            if int(oB) <= minimum and int(oB) >= maximum:
                    moves.append(row)
    e = discord.Embed(title=character)
    headers = [titles[1], titles[oBKey]]
    embedArray = []
    offset = 0
    finished = 0
    listSize = 40
    while(True):
        stringArray = []
        for i in range(offset, offset + listSize - 1):
            if i >= len(moves):
                finished = 1
                break
            moveName = moves[i][1]
            moveButton = getButton(moves[i][2])
            if getButton(moveName) == None and moveButton != None:
                moveName = moveButton + " " + moveName
            stringArray.append([moveName, moves[i][oBKey]])
        embedArray.append("```" + tabulate(stringArray, headers=headers) + "```")
        offset += listSize
        if finished == 1:
            break
    return embedArray
 
def translateAcronym(text):
    if re.match(r"tc[0-9]+", text.lower()):
        text = text.replace("tc", "Target Combo ")
    return text

def removePunctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation)).rstrip().replace("+", "").lower().replace(" ", "")
