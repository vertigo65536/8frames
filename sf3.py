import tools, os, re, discord, json
from fuzzywuzzy import fuzz

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sf3")
punct = "!@#$%^&*()[]{};:,./<>?\|`~-=_+"
replacePunct = " "

def getPath():
    return path

def getPossibleMoves(content, characterFile, extraLevels=[]):
    searchOutput = []
    scorer = fuzz.token_sort_ratio
    punctuation = [punct, replacePunct]
    searchOutput.append(tools.searchMove(content, characterFile, "Motion", punctuation, fuzz.ratio))
    searchOutput.append(tools.searchMove(formatAsInput(content), characterFile, "Motion", punctuation, fuzz.ratio))
    searchOutput.append(tools.searchMove(content, characterFile, "key", punctuation, scorer))
    searchOutput.append(tools.searchMove(formatAsInput(content, 1), characterFile, "key", punctuation, scorer))
    return searchOutput

def getPunishable(f, character, punishable = 0):
    with open(f) as json_file:
        moveList = json.load(json_file)
        moves = []
        minimum = 0
        maximum = 0
        if punishable == 0:
            minimum = -1
            maximum = -2
        elif punishable == 1:
            minimum = -3
            maximum = -200
        else:
           return -1
        oBHeader = 'Blocked Advantage'
        for key, move in moveList.items():
            if not oBHeader in move:
                continue
            oB = move[oBHeader]
            oB = str(oB).split("[")
            for i in range(len(oB)):
                try:
                    int(oB[i])
                except:
                    continue
                oB[i].replace("]", "")
                if int(oB[i]) <= minimum and int(oB[i]) >= maximum:
                    moves.append([key, move[oBHeader]])
                    break
    return [moves, ['Name', oBHeader]]


def translateAlias(text):
    return text

def translateAcronym(text):
    text = str(text).lower()
    if re.match(r"tc[0-9]+", text):
        text = text.replace("tc", "target combo ")
    if "dp" in text:
        text = text.replace("dp", "fddf")
    text = text.replace('uoh', 'Universal Overhead')
    text = text.replace("jump", "air")
    return text

def getMoveEmbed(moveRow, moveName, character):
    e = discord.Embed(title=character)
    e.add_field(name = "Name", value = moveName)
    for title, value in moveRow.items():
        if title != 'Image':
            e.add_field(
                name = title,
                value = value
            )
    try:
        e.set_image(url=moveRow['Image'])
    except:
        pass
    return e

def formatAsInput(string, reverse = 0):
    moveConversion = {
        'cr': 'd+',
        'j': '(air)',
        'fierce': 'hp',
        'strong': 'mp',
        'jab': 'lp',
        'short': 'lk',
        'forward': 'mk',
        'roundhouse': 'hk',
        'light kick': 'lk',
        'medium kick': 'mk',
        'heavy kick': 'hk',
        'light punch': 'lp',
        'medium punch': 'mp',
        'heavy punch': 'hp',
        'crouch': 'cr',
        'standing': '',
        'far': ''
    }
    for key, value in moveConversion.items():
        if reverse == 0:
            string = string.replace(key, value)
        elif reverse == 1:
            if value != '':
                string = string.replace(value, key)
    return string

def getBadPunctuation():
    return punct

def getPunctReplacement():
    return replacePunct
