import discord, os, numpy, re, json, imgkit, time
import tools, t7, sfv, sf4, sf3
import db_bot as db
from fuzzywuzzy import process, fuzz
from dotenv import load_dotenv
from tabulate import tabulate
from bs4 import BeautifulSoup

numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]


def numberToEmoji(n):
    try:
        return numbers[n-1]
    except:
        return -1

def getGame(string):
    if string.lower() == "t7":
        return t7
    if string.lower() in ["sfv", "sf5"]:
        return sfv
    if string.lower() == "sf4":
        return sf4
    if string.lower() in ["sf3", "3s"]:
        return sf3

def getManPage():
    f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "man.txt"), "r")
    if f.mode == "r":
        return f.read()
    print("Failed to open man file")
    return

async def wrongResultEdit(botMessage):
    row = db.getRowByBotMessage(botMessage.id)
    game = row[4]
    character = row[5]
    command = row[6]
    game = getGame(game)
    path = getCharacterPath(character, game.getPath())[0]
    searchOutput = game.getPossibleMoves(command, path)
    reducedDict = {}
    for i in range(len(searchOutput)):
        for j in range(len(searchOutput[i])):
            if searchOutput[i][j][1] in reducedDict:
                if reducedDict[searchOutput[i][j][1]] > searchOutput[i][j][2]:
                    continue
            reducedDict[searchOutput[i][j][1]] = searchOutput[i][j][2]
    counter = 5
    rankedList = []
    for key, value in reducedDict.items():
        rankedList.append([key, value])
    rankedList = sorted(rankedList,key=lambda x: x[1], reverse=True)
    if len(reducedDict) < 5:
        counter = len(reducedDict)
    rankedList = rankedList[:counter]
    await botMessage.edit(content = getCorrectionEmbed(rankedList), embed = None)
    try:
        await botMessage.clear_reactions()
    except:
        pass
    await tools.addReacts(botMessage, ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"])

async def resultCorrection(message, emoji):
    row = db.getRowByBotMessage(message.id)
    content = message.content.split("\n")
    moveName = None
    for i in range(len(content)):
        if emoji in content[i]:
            moveName = content[i].replace(emoji, "").rstrip().strip()
    if moveName == None:
        return -1
    game = row[4]
    character = row[5]
    command = row[6]
    game = getGame(game)
    path = getCharacterPath(character, game.getPath())[0]
    outputRow = game.getPossibleMoves(command, path)
    for i in range(len(outputRow)):
        for j in range(len(outputRow[i])):
            if outputRow[i][j][1] == moveName:
                e = game.getMoveEmbed(outputRow[i][j][0], outputRow[i][j][1], character)
                await message.edit(content=None, embed=e)
                db.correctQuery(character+command, game.getGame(), moveName, message.id)
                try:
                    await message.clear_reactions()
                except:
                    pass
                return

def getCorrectionEmbed(array):
    string = "Did you mean:\n"
    for i in range(len(array)):
        string = string + numberToEmoji(i+1) + " " + array[i][0] + "\n"
    return string.rstrip().strip()
    
def getCharacterPath(query, gamedir):
    files = os.listdir(gamedir)
    fuzzyMatch  = process.extractOne(query + ".json", files, scorer=fuzz.ratio)
    if fuzzyMatch[1] < 60:
        return -1
    return [gamedir + "/" + fuzzyMatch[0], fuzzyMatch[0].replace(".json", "")]

async def parseCommand(message, game):
    prefix = tools.getMessagePrefix(message.content)
    if prefix.split("!")[0].lower() in ["8fm", "8framesm", "8framesmobile", "8fmobile"]:
        mobile = True
    else:
        mobile = False

    command = tools.getMessageContent(message.content)
    command = ' '.join(command.split())
    if command == -1:
        return "Requres a character and a query. Consult 8f!man for more info"
    character = tools.getMessagePrefix(command)
    character = game.translateAlias(character)
    content = game.translateAcronym(tools.getMessageContent(command))
    print(content)
    getChar = getCharacterPath(character, game.getPath())
    if getChar == -1:
        return "Could not find character '" + character + "'"
    characterFile = getChar[0]
    character = getChar[1]
    if content == "-1":
        return "Requires extra input: Either a move name or query such as 'punishable'. consult 8f!man for more info."
    presetCmds = tools.loadJsonAsDict("searchJsons/limitsKey.json")
    for i in range(len(presetCmds)):
        if content in presetCmds[i]:
            moves = game.getPunishable(characterFile, character, i)
            return outputArray(moves, character+" "+content, mobile)
    searchParams = tools.loadJsonAsDict("searchJsons/searchParamKey.json")
    for i in range(len(searchParams)):
        if content in searchParams[i]:
            try:
                moves = game.getNote(characterFile, character, i)
            except:
                return "Function not available for this game"
            return outputArray(moves, character+" "+content, mobile)
    if content == 'stats':
        return game.getMoveEmbed(game.getStats(characterFile), 'Stats', character)
    if re.match('\d+f? punish', content):
        punishValue = content.replace("f ", "").replace("punish", "")
        punishValue = int(punishValue.rstrip().strip())
        moves = game.getPunish(characterFile, character, punishValue)
        return outputArray(moves, character+" "+content, mobile)
    ratio = db.getMoveResultRatio(character+content, game.getGame())
    e = None
    if ratio != -1:
        guessedKey = None
        for key, value in ratio.items():
            if value > 70:
                guessedKey = key
                break
        if guessedKey != None:
            row = game.getMoveByKey(guessedKey, characterFile)
            if row != -1:
                output = ""
                e = game.getMoveEmbed(row, guessedKey, character)
                finalMoveKey = guessedKey
    if e == None:
        searchOutput = game.getPossibleMoves(content, characterFile)
        if isinstance(searchOutput, str):
            return searchOutput
        outputValue = searchOutput[0][0]
        for i in range(len(searchOutput)):
            if searchOutput[i] == -1 or searchOutput[i] == []:
                continue
            if searchOutput[i][0][2] > outputValue[2]:
                outputValue = searchOutput[i][0]
        if outputValue[2] < 60:
            output = "Move not found"
            e = None
        else:
            output = ""
            e = game.getMoveEmbed(outputValue[0], outputValue[1], character)
            finalMoveKey = outputValue[1]
    postMessage = await message.channel.send(output, embed=e)
    try:
        db.insertIntoBotPosts(postMessage.id, message.id, postMessage.channel.id, message.author.id, prefix.split("!")[1], character, content, finalMoveKey, mobile)
        queryId = character+content
        db.createQueryRow(queryId, game.getGame())
        db.updateQueryCount(queryId, game.getGame())
        db.createQuerySelectionRow(queryId, game.getGame(), finalMoveKey)
        db.updateQuerySelectionCount(queryId, game.getGame(), finalMoveKey)
        await tools.addReacts(postMessage, ["❌"])
    except:
        pass
    return


def outputArray(moves, character, mobile):
    if mobile == True:
        return arrayToImage(moves, character)
    return formatMoveList(moves, character)

def arrayToImage(array, title):
    options = {'width': '400','disable-smart-width': ''}
    tableString = tabulate(array[0], array[1], tablefmt="html").replace("<table>", "<table style=\"color:blue; width:100%;\">")
    soup = BeautifulSoup(tableString, features='html.parser')
    colours = ["#f2f2f2", "#d9d9d9"]
    counter = 0
    for table in soup.findAll('table'):
        table['style'] = "border-collapse: collapse; width: 100%;"
    for row in soup.findAll('tr'):
        row['style'] = "background-color: " + colours[counter%2] + ";"
        counter += 1
    path = tools.getAbsPath('media/image' + str(int(time.time())) + '.jpg')
    image = imgkit.from_string(str(soup), path, options=options)
    df = discord.File(path, filename=title + ".jpg")
    os.remove(path)
    return df

def formatMoveList(moves, character):
    if moves[0] == []:
        return 'None'
    if not isinstance(moves, list):
        return
    e = discord.Embed(title=character)
    headers = moves[1]
    moves = tools.correctTableWrap(moves[0])
    embedArray = []
    offset = 0
    finished = 0
    listSize = 26
    outputArray = []
    while(True):
        stringArray = []
        for i in range(offset, offset + listSize):
            if i >= len(moves):
                finished = 1
                break
            row = []
            for j in range(len(moves[i])):
                row.append(moves[i][j])
            stringArray.append(row)
            #stringArray.append([moves[i][0], moves[i][1]])
        embedArray.append("```\n" + tabulate(stringArray, headers=headers) + "```")
        offset += listSize
        if finished == 1:
            break
    return embedArray

def isAdmin(authorId):
    admins = os.getenv('ADMIN_ID').split(" ")
    if str(authorId) in admins:
        return True
    else:
        return False

async def handleMessage(message):
    prefix = tools.getMessagePrefix(message.content)
    content = tools.getMessageContent(message.content)
    commandSplit = prefix.split("!")
    if commandSplit[0].lower() in ["8frames", "8f", "8fm", "8framesm", "8framesmobile", "8fmobile"]:
        if commandSplit[1] in ["man", "help"]:
            return getManPage()
        if isAdmin(message.author.id):
            if commandSplit[1] == 'servers':
                serverList = []
                for i in range(len(client.guilds)):
                    serverList.append([client.guilds[i].name, client.guilds[i].member_count, str(client.guilds[i].id)])
                return formatMoveList([serverList, ['Name', 'Size', 'id']], 'Servers')
        return await parseCommand(message, getGame(commandSplit[1]))

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Game(name="type 8f!man for help"))
    
@client.event    
async def on_message(message):
    if message.author == client.user:
        return
    response = await handleMessage(message)
    if not isinstance(response, list):
        response = [response]
    for i in range(len(response)):
        e = None
        f = None
        content = response[i]
        if isinstance(response[i], discord.embeds.Embed):
            e = response[i]
            content = None
        elif isinstance(response[i], discord.file.File):
            f = response[i]
            content = f.filename.replace(".jpg", "")
        if response[i] not in ["", None]:
            await message.channel.send(content, embed=e, file=f)
        else:
            continue
    return

@client.event
async def on_reaction_add(reaction, user):
    if reaction.me and reaction.count == 1:
        return
    if reaction.message.author == client.user:
        results = db.getQueryAuthor(reaction.message.id)
        try:
            if results[0][0] != str(user.id):
                return
        except:
            return
        if reaction.emoji == '❌':
            await wrongResultEdit(reaction.message)
        elif reaction.emoji in numbers:
            await resultCorrection(reaction.message, reaction.emoji)
        else:
            print('nothing')


@client.event
async def on_message_delete(message):
    await trophyProcess("delete", message)

client.run(TOKEN)
