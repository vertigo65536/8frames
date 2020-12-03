import csv, os, json, string
from fuzzy_match import match, algorithims

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
        
#Returns a value from a CSV, from a given value

def getStoredRowByInput(id, file):
    try:
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='`')
            line_count = 0
            id = str(id).translate(str.maketrans('', '', string.punctuation)).lower()
            moveData = {}
            moveKeys = []
            counter = 0
            for row in csv_reader:
                if len(row) <= 0:
                    continue
                moveKeys.append(row[0].translate(str.maketrans('', '', string.punctuation)))
                moveData[moveKeys[counter]] = row
                if moveKeys[counter] == id:
                    return row
                counter += 1
            return moveData[match.extractOne(id, moveKeys)[0]]
    except:
        return -1


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
    return text.translate(str.maketrans('', '', string.punctuation)).rstrip().lower().replace(" ", "")
