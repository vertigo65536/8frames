import tools, os, re, discord, json
from fuzzywuzzy import fuzz

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "t7")
punct = "!@#$%^&*()[]{};:,./<>?\|`~-=_ "
replacePunct = ""

def getPath():
    return path

def getPossibleMoves(content, characterFile, extraLevels=[]):
    searchOutput = []
    searchOutput.append(tools.searchMove(content, characterFile, "key", [punct, replacePunct], fuzz.ratio))
    return searchOutput

def getPunishable(f, character, punishable = 0):
    with open(f) as json_file:
        moveList = json.load(json_file)
        moves = []
        minimum = 0
        maximum = 0
        if punishable == 0:
            minimum = -9
            maximum = 0
        elif punishable == 1:
            minimum = -200
            maximum = -9
        elif punishable == 2:
            minimum = -8
            maximum = 200
        elif punishable == 3:
            minimum = 1
            maximum = 200
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
                if int(oB[i]) >= minimum and int(oB[i]) <= maximum:
                    moves.append([key, move[oBHeader]])
                    break
    return [moves, ['Name', oBHeader]]

def getPunish(f, character, startupQuery):
    with open(f) as json_file:
        moveList = json.load(json_file)
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
        name = "Move",
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
