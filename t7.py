import tools
import os, discord
from fuzzy_match import match, algorithims

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
        

def parseAcronyms(name):
    if name.lower() == "ak":
        return "Armor King"
    if name.lower() == "dj":
        return "Devil Jin"
    else:
        return name
