import tools, os, re, discord, json
from fuzzywuzzy import fuzz

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "t7")
punct = "!@#$%^&*()[]{};:,./<>?\|`~-=_ "
replacePunct = ""
game = "t7"

def getPath():
    return path

def getGame():
    return game

def getPossibleMoves(content, characterFile):
    searchOutput = []
    searchOutput.append(tools.searchMove(content, characterFile, "key", [punct, replacePunct], fuzz.ratio))
    return searchOutput

def getMoveByKey(content, characterFile):
    return tools.getByKey(content, characterFile)

def getPunishable(f, character, punishable = 0):
    moveList = tools.loadJsonAsDict(f)
    moves = []
    try:
        limits = tools.getLimits(game)[punishable]
        minimum = limits['min']
        maximum = limits['max']
        
    except:
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
            if int(oB[i]) >= minimum and int(oB[i]) <= maximum:
                moves.append([key, move[oBHeader]])
                break
    return [moves, ['Name', oBHeader]]

def getPunish(f, character, startupQuery):
    moveList = tools.loadJsonAsDict(f)
    moves = []
    startup = 'Start up frame'
    for key, move in moveList.items():
        if 'Jump' in key:
            continue
        if not startup in move:
            continue
        startupVal = move[startup]
        startupVal = str(startupVal).replace("~", "[").replace(",", "[")
        startupVal = str(startupVal).split("(")
        for i in range(len(startupVal)):
            startupVal[i] = startupVal[i].rstrip().strip()
            try:
                int(startupVal[i])
            except:
                continue
            startupVal[i].replace(")", "")
            if int(startupVal[i]) <= startupQuery:
                moves.append([key, move[startup]])
                break
    return [moves, ['Name', startup]]


def translateAlias(name):
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

def translateAcronym(text):
    return text

def getMoveEmbed(moveRow, moveName, character):
    e = discord.Embed(title=character)
    e.add_field(
        name = "Name",
        value = moveName
    )
    for key, value in moveRow.items():
        if value in ['', None]:
            value = 'n/a'
        e.add_field(
            name = key,
            value = value
        )
    return e

def getBadPunctuation():
    return punct

def getPunctReplacement():
    return replacePunct
