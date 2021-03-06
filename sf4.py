import tools, os, re, discord, string, json
from fuzzywuzzy import fuzz

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sf4")
punct = string.punctuation.replace(">", "")
replacePunct = " "
game = "sf4"
extraLevels = ['moves']

def getPath():
    return path

def getGame():
    return game

def getPossibleMoves(content, characterFile):
    searchOutput = []
    scorer = fuzz.token_sort_ratio
    punctuation = [punct, replacePunct]
    searchOutput.append(tools.searchMove(content, characterFile, "input", punctuation, fuzz.ratio, extraLevels))
    searchOutput.append(tools.searchMove(content, characterFile, "key", punctuation, scorer, extraLevels))
    searchOutput.append(tools.searchMove(content, characterFile, "key", punctuation, fuzz.ratio, extraLevels))
    if 'super' in content:
        searchOutput.append(tools.searchMove(content, characterFile, "moveType", punctuation, fuzz.ratio, extraLevels))
    if re.match('(ultra|u+) ?\d+$', content):
        content = content.replace("ultra", "").replace("u", "").rstrip().strip()
        searchOutput.append(tools.searchMove(content, characterFile, "ultra", punctuation, fuzz.ratio, extraLevels))
    return searchOutput

def getMoveByKey(content, characterFile):
    return tools.getByKey(content, characterFile, extraLevels)

def getPunishable(f, character, punishable = 0):
    moveList = tools.loadJsonAsDict(f)['moves']
    moves = []
    try:
        limits = tools.getLimits(game)[punishable]
        minimum = limits['min']
        maximum = limits['max']
        
    except:
        return -1
    oBHeader = 'onBlock'
    for key, move in moveList.items():
        oB = move[oBHeader]
        oB = str(oB).split("[")
        for i in range(len(oB)):
            try:
                int(oB[i])
            except:
                continue
            oB[i].replace("]", "")
            if int(oB[i]) >= minimum and int(oB[i]) <= maximum:
                moves.append([key, move[oBHeader]])
                break
    return [moves, ['Name', oBHeader]]

def getPunish(f, character, startupQuery):
    moveList = tools.loadJsonAsDict(f)['moves']
    moves = []
    startup = 'startup'
    for key, move in moveList.items():
        if 'Jump' in key:
            continue
        if not startup in move:
            continue
        startupVal = move[startup]
        startupVal = str(startupVal).replace("~", "[").replace("/", "[").replace("～", "[")
        startupVal = str(startupVal).split("[")
        for i in range(len(startupVal)):
            startupVal[i] = startupVal[i].rstrip().strip()
            try:
                int(startupVal[i])
            except:
                continue
            startupVal[i].replace("]", "")
            if int(startupVal[i]) <= startupQuery:
                moves.append([key, move[startup]])
                break
    return [moves, ['Name', startup]]


def translateAlias(text):
    text = text.lower()
    text = text.replace("eryu", "Evil Ryu")
    text = text.replace("claw", "Vega")
    text = text.replace("dictator", "Bison")
    text = text.replace("boxer", "Balrog")
    return text

def translateAcronym(text):
    text = str(text).lower()
    if re.match(r"tc[0-9]+", text):
        text = text.replace("tc", "target combo ")
    if re.search(r"rekka [0-9]+", text) or  re.search(r"rekkaken [0-9]+", text):
        text = text.replace("rekka", "rekka part")
        text = text.replace("rekkaken", "rekkaken part")
        text = text.replace("part 1", "")
    text = text.replace("qcfqcf", "dqcf")
    text = text.replace("qcf qcf", "dqcf")
    text = text.replace("qcbqcb", "dqcb")
    text = text.replace("qcb qcb", "dqcb")
    text = text.replace("hcbhcb", "dhcb")
    text = text.replace("hcb hcb", "dhcb")
    text = text.replace("pp", "2p")
    text = text.replace("ppp", "3p")
    text = text.replace("kk", "2k")
    text = text.replace("kkk", "3k")
    return text

def getMoveEmbed(moveRow, moveName, character):
    e = discord.Embed(title=character)
    e.add_field(name = "Name", value = moveName)
    for title, value in moveRow.items():
        e.add_field(
            name = title,
            value = str(value).replace("*", "•")
        )
    return e

def getBadPunctuation():
    return punct

def getPunctReplacement():
    return replacePunct
