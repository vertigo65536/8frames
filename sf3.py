import tools, os, re, discord, json
from fuzzywuzzy import fuzz

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sf3")
punct = "!@#$%^&*()[]{};:,./<>?\|`~-=_+"
replacePunct = " "
game = "sf3"
extraLevels = ['moves', 'normal']

def getFieldTitle(field):
    fieldTitles = {
        'plnCmd': 'Move Input',
        'cmnName': 'Common Name',
        'karaRange': 'Kara Range',
        'meterAtkWhiff': 'Meter Build on Whiff',
        'meterAtkBlk': 'Meter Build on Block',
        'meterAtkHit': 'Meter Build on Hit',
        'meterOppBlk': 'Meter Build on Block Opponent',
        'meterOppHit': 'Meter Build on Opponent Hit',
        'onBlock': 'On Block',
        'onHit': 'On Hit',
        'onHitCrouch': 'On Crouching Hit',
        'nJump': 'Neutral Jump',
        'fJump': 'Forward Jump',
        'bJump': 'Backward Jump',
        'nSuperJump': 'Neutral Super Jump',
        'fSuperJump': 'Forward Super Jump',
        'bSuperJump': 'Backward Super Jump',
        'fDash': 'Forward Dash',
        'bDash': 'Back Dash',
        'wakeupNormal': 'Normal Wakeup',
        'wakeupQuick': 'Quick Getup'
    }
    try:
        return fieldTitles[field]
    except:
        return field.capitalize()

def getPath():
    return path

def getGame():
    return game

def getStats(characterFile):
    with open(characterFile) as json_file:
        data = json.load(json_file)
    return data['stats']

def getPossibleMoves(content, characterFile):
    searchOutput = []
    scorer = fuzz.token_sort_ratio
    punctuation = [punct, replacePunct]
    searchOutput.append(tools.searchMove(content, characterFile, "plnCmd", punctuation, fuzz.ratio, extraLevels))
    searchOutput.append(tools.searchMove(tools.formatAsSFInput(content), characterFile, "plnCmd", punctuation, fuzz.ratio, extraLevels))
    searchOutput.append(tools.searchMove(content, characterFile, "key", punctuation, scorer, extraLevels))
    searchOutput.append(tools.searchMove(tools.formatAsSFInput(content, 1), characterFile, "key", punctuation, scorer, extraLevels))
    searchOutput.append(tools.searchMove(content, characterFile, "cmnName", punctuation, scorer, extraLevels))
    return searchOutput

def getMoveByKey(content, characterFile):
    return tools.getByKey(content, characterFile)

def parseSa(string):
    string = string.replace("sa", "").replace("super art", "")
    string = string.rstrip().strip()
    string = string.replace("3", "III").replace("2", "II").replace("1", "I")
    return string

def getPunishable(f, character, punishable = 0):
    moveList = tools.loadJsonAsDict(f)
    for i in range(len(extraLevels)):
        moveList = moveList[extraLevels[i]]
    moves = []
    try:
        limits = tools.getLimits(game)[punishable]
        minimum = limits['min']
        maximum = limits['max']
        
    except:
        return -1
    oBHeader = 'onBlock'
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
    moveList = tools.loadJsonAsDict(f)
    for i in range(len(extraLevels)):
        moveList = moveList[extraLevels[i]]
    moves = []
    startup = 'startup'
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
    text = text.replace('uoh', 'mp+mk')
    text = text.replace('throw', 'lp+lk')
    text = text.replace('grab', 'lp+lk')
    text = text.replace("jump", "air")
    text = text.replace("raging demon", "shun goku satsu")
    text = text.replace("kkz", "kongou kokuretsu zan")
    text = text.replace('taunt', 'hp+hk')

    text = text.replace('fierce', 'hp')
    text = text.replace('strong', 'mp')
    text = text.replace('jab', 'lp')
    text = text.replace('roundhouse', 'hk')
    text = text.replace('forward', 'mk')
    text = text.replace('short', 'lk')
    return text

def getMoveEmbed(moveRow, moveName, character):
    e = discord.Embed(title=character)
    e.add_field(name = "Name", value = moveName)
    for title, value in moveRow.items():
        if title not in ['image', 'moveName', 'numCmd', 'moveType', 'moveMotion', 'moveButton', 'nonHittingMove', 'threeLetterCode', 'color']:
            e.add_field(
                name = getFieldTitle(title),
                value = value
            )
    try:
        e.set_image(url=moveRow['image'])
    except:
        pass
    return e

def getBadPunctuation():
    return punct

def getPunctReplacement():
    return replacePunct
