import tools
import os, discord, string, csv
from fuzzy_match import match, algorithims
from tabulate import tabulate

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sf4")

headers = [
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

def parseCommand(command):
    character = tools.getMessagePrefix(command)
    content = tools.getMessageContent(command)
    files = os.listdir(path)

    fuzzyMatch  = match.extractOne(character + ".csv", files)
    if fuzzyMatch[1] < 0.6:
        return "Could not find character '" + character + "'"
    file = path + "/" + fuzzyMatch[0]

    searchOutput = []
    searchOutput.append(getMoveByCommand(content, file))
    searchOutput.append(getMoveByName(content, file))
    searchOutput.append(getMoveByNickname(id, file))
    outputValue = searchOutput[0]
    for i in range(len(searchOutput)):
        if searchOutput[i][1] > outputValue[1]:
            outputValue = searchOutput[i]
    return getMoveEmbed(outputValue[0], fuzzyMatch[0].replace(".csv", ""))

def getMoveByCommand(id, file):
    return getMoveByNthKey(id, file, 0)

def getMoveByName(id, file):
    return getMoveByNthKey(id, file, 1)

def getMoveByNickname(id, file):
    return getMoveByNthKey(id, file, 2)

def getMoveByNthKey(id, file, n):
    #try:
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
    #except:
    #    return -1

def getMoveEmbed(moveRow, character):
    e = discord.Embed(title=character)
    for i in range(len(moveRow)):
        e.add_field(
            name = headers[i],
            value = moveRow[i]
        )
    return e

def removePunctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation)).rstrip().replace("+", "").lower()
