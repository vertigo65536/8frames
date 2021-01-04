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

def getUserId(user):
    userPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
    with open(userPath) as json_file:
        data = json.load(json_file)
        try:
            return data[user]
        except:
            return -1

def removePunctuation(text):
    #return text.translate(str.maketrans('', '', string.punctuation)).rstrip().lower()
    return text.translate ({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).rstrip().lower()
