import csv, os, json, string
from fuzzywuzzy import process, fuzz

# Returns the first word from a string (Usually a bot command)

def getMessagePrefix(message):
    return message.split(" ")[0]

# Returns everything after the first word

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
        with open(f) as json_file:
            moveList = json.load(json_file)
            keyList = {}
            keyArray = []
            for i in range(len(extraLevel)):
                moveList = moveList[extraLevel[i]]
            if moveId != 'key':
                for key, row in moveList.items():
                    if moveId not in row:
                        continue
                    keyArray.append(removePunctuation(row[moveId], punct))
                    keyList[removePunctuation(row[moveId], punct)] = key
            else:
                for key, row in moveList.items():
                    keyArray.append(removePunctuation(key, punct))
                    keyList[removePunctuation(key, punct)] = key
            fuzzyMatch  = process.extractOne(query, keyArray, scorer=scorer)
            return [moveList[keyList[fuzzyMatch[0]]], keyList[fuzzyMatch[0]], fuzzyMatch[1]]
    except:
        return -1


def getUserId(user):
    userPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
    with open(userPath) as json_file:
        data = json.load(json_file)
        try:
            return data[user]
        except:
            return -1

def removePunctuation(text, punct):
    text = text.translate ({ord(c): punct[1] for c in punct[0]}).rstrip().lower()
    return text
