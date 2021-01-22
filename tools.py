import csv, os, json, string
from fuzzywuzzy import process, fuzz

# Returns the first word from a string (Usually a bot command)

def getMessagePrefix(message):
    return message.split(" ")[0]

# Returns everything after the first word

def getAbsPath(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

def getMessageContent(message):
    split = message.split(" ")
    content = ""
    if len(split) <= 1:
        return -1
    else:
        for i in range(len(split)-1):
            if i == 0:
                content = split[i+1]
            else:
                content = content + " " + split[i+1]
    return content
        
# Determines a user's colour and returns it

def getUserColour(message):
    bestColour = "#000000"
    bestRank = 0 
    for role in message.author.roles:
        if role.position > bestRank and str(role.colour) != "#000000":
            bestColour = role.colour
    return bestColour


# Returns the user ID for nickname

def searchMove(query, f, moveId, punct, scorer, extraLevel=[]):
    query = removePunctuation(query, punct)
    try:
        moveList = loadJsonAsDict(f)
        keyArray = []
        for i in range(len(extraLevel)):
            moveList = moveList[extraLevel[i]]
        if moveId != 'key':
            i = 0
            for key, row in moveList.items():
                if moveId not in row:
                    continue
                keyArray.append([removePunctuation(row[moveId], punct), row, key])
        else:
            for key, row in moveList.items():
                keyArray.append([removePunctuation(key, punct), row, key])
        outputArray = []
        for i in range(len(keyArray)):
            matchCheck = process.extract(query, [keyArray[i][0]], scorer=scorer)
            outputArray.append([keyArray[i][1], keyArray[i][2], matchCheck[0][1]])
        outputArray = sorted(outputArray, key=lambda x: x[2], reverse=True)
        outputArray = outputArray[:5]
        return outputArray
    except:
        return -1


def getUserId(user):
    userPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
    data = loadJsonAsDict(userPath)
    try:
        return data[user]
    except:
        return -1

def correctTableWrap(array):
    limit = 58
    averageColWidth = limit//len(array)
    colWidth = []
    lenSum = 0
    smallSum = 0
    smallKeys = []
    for i in range(len(array[0])):
        colWidth.append(0)
    for i in range(len(array)):
        for j in range(len(array[i])):
            array[i][j] = str(array[i][j])
            tmpStrLen = len(array[i][j])
            if colWidth[j] < tmpStrLen:
                colWidth[j] = tmpStrLen
    for i in range(len(colWidth)):
        lenSum += colWidth[i]
        if colWidth[i] < averageColWidth:
            smallKeys.append(j)
            smallSum += colWidth[i]
    if lenSum > limit:
        maxWidth = (limit - smallSum)//(len(colWidth) - len(smallKeys))
        for i in range(len(colWidth)):
            if i not in smallKeys:
                colWidth[i] = maxWidth
    output = []
    counter = 0
    for i in range(len(array)):
        largestTmp = 0
        for j in range(len(array[i])):
            tmp = splitString(array[i][j], colWidth[j])
            if len(tmp) > largestTmp:
                largestTmp = len(tmp)
            for k in range(len(tmp)):
                try:
                    output[counter + k][j]
                except:
                    output.append([])
                    for l in range(len(array[i])):
                        output[counter + k].append("")
                output[counter + k][j] = tmp[k]
        counter += largestTmp
    return output

def splitString(string, limit):
    limit += 1
    stringArr = str(string).split(" ")
    output = []
    tmpString = ""
    for i in range(len(stringArr)):
        if len(stringArr[i]) > limit:
            return [ stringArr[i][j:j+limit] for j in range(0, len(string), limit) ]
        if len(tmpString + " " + stringArr[i]) > limit:
            output.append(tmpString.strip())
            tmpString = ""
        tmpString = tmpString + " " + stringArr[i]
    if tmpString != "":
        output.append(tmpString.strip())
    return output

async def addReacts(message, emojis):
    if isinstance(emojis, list):
        for i in range(len(emojis)):
            try:
                await message.add_reaction(emojis[i])
            except:
                print(emojis[i] + " is not an emoji")
    else:
        await message.add_reaction(emojis)
    return 

def getLimits(game):
    allLimits = loadJsonAsDict("searchJsons/limits.json")
    return allLimits[game]

def loadJsonAsDict(filename):
    with open(getAbsPath(filename)) as json_file:
        jsonDict = json.load(json_file)
    return jsonDict

def removePunctuation(text, punct):
    text = text.translate ({ord(c): punct[1] for c in punct[0]}).rstrip().lower()
    return text
