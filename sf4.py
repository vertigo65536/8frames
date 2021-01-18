import tools, os, re, discord, string, json
from fuzzywuzzy import fuzz

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sf4")
punct = string.punctuation.replace(">", "")
replacePunct = " "
game = "sf4"

def getPath():
    return path

def getPossibleMoves(content, characterFile, extraLevels=['moves']):
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

def getPunishable(f, character, punishable = 0):
    with open(f) as json_file:
        moveList = json.load(json_file)['moves']
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
    with open(f) as json_file:
        moveList = json.load(json_file)['moves']
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
    return text

def translateAcronym(text):
    text = str(text).lower()
    if re.match(r"tc[0-9]+", text):
        text = text.replace("tc", "target combo ")
    if re.search(r"rekka [0-9]+", text) or  re.search(r"rekkaken [0-9]+", text):
        text = text.replace("rekka", "rekka part")
        text = text.replace("rekkaken", "rekkaken part")
        text = text.replace("part 1", "")
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
