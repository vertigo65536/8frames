import tools, os, re, discord, json
from fuzzywuzzy import fuzz

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sf3")
punct = "!@#$%^&*()[]{};:,./<>?\|`~-=_+"
replacePunct = " "
game = "sf3"

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
    if re.match('(super art|sa+) ?\d+$', content):
        searchOutput.append(tools.searchMove(parseSa(content), characterFile, "Super Art", punctuation, scorer))
    return searchOutput

def parseSa(string):
    string = string.replace("sa", "").replace("super art", "")
    string = string.rstrip().strip()
    string = string.replace("3", "III").replace("2", "II").replace("1", "I")
    return string

def getPunishable(f, character, punishable = 0):
    with open(f) as json_file:
        moveList = json.load(json_file)
        moves = []
        try:
            limits = tools.getLimits(game)[punishable]
            minimum = limits['min']
            maximum = limits['max']
            
        except:
            return -1
        oBHeader = 'Blocked Advantage'
        for key, move in moveList.items():
            if not oBHeader in move:
                continue
            oB = move[oBHeader]
            oB = str(oB).replace("~", "[").replace("/", "[").replace("～", "[")
            oB = str(oB).split("[")
            for i in range(len(oB)):
                oB[i] = oB[i].rstrip().strip()
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
        moveList = json.load(json_file)
        moves = []
        startup = 'Startup'
        for key, move in moveList.items():
            if 'Jump' in key:
                continue
            if not startup in move:
                continue
            startupVal = move[startup]
            startupVal = str(startupVal).replace("~", "[").replace("/", "[").replace("～", "[").replace("・", "[")
            startupVal = str(startupVal).split("[")
            for i in range(len(startupVal)):
                startupVal[i] = startupVal[i].rstrip().strip()
                try:
                    int(startupVal[i])
                except:
                    continue
                startupVal[i].replace("]", "")
                if int(startupVal[i]) <= startupQuery-1:
                    moves.append([key, startupVal[0]])
                    break
    return [moves, ['Name', startup]]
  

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
    text = text.replace("raging demon", "shun goku satsu")
    text = text.replace("kkz", "kongou kokuretsu zan")
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
        'far': '',
        'lp': ' lp',
        'mp': ' mp',
        'hp': ' hp',
        'lk': ' lk',
        'mk': ' mk',
        'hk': ' hk',
        'fddf': 'f d df'
    }
    numberInputs = {
        '63214': 'hcb',
        '41236': 'hcf',
        '236': 'qcf',
        '214': 'qcb',
        '623': 'f d df',
        '421': 'b d db',
        '1': 'db',
        '2': 'd',
        '3': 'df',
        '4': 'b',
        '5': 'n',
        '6': 'f',
        '7': 'ub',
        '8': 'u',
        '9': 'uf'
    } 
    for key, value in moveConversion.items():
        if reverse == 0:
            string = string.replace(key, value)
        elif reverse == 1:
            if value != '':
                string = string.replace(value, key)
    for key,value in numberInputs.items():
        if reverse == 0:
            string = string.replace(key, value)
    return string

def getBadPunctuation():
    return punct

def getPunctReplacement():
    return replacePunct
