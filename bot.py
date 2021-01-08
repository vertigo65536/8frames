import discord, os, numpy
import tools, t7, sfv, sf4, sf3
from fuzzywuzzy import process, fuzz
from dotenv import load_dotenv
from tabulate import tabulate

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

def parseCommand(command, game):
    character = tools.getMessagePrefix(command)
    character = game.translateAlias(character)
    content = game.translateAcronym(tools.getMessageContent(command))
    files = os.listdir(game.getPath())
    fuzzyMatch  = process.extractOne(character + ".json", files, scorer=fuzz.ratio)
    if fuzzyMatch[1] < 40:
        return "Could not find character '" + character + "'"
    characterFile = game.getPath() + "/" + fuzzyMatch[0]
    character = fuzzyMatch[0].replace(".json", "")
    if content.lower() == "punishable":
        moves = game.getPunishable(characterFile, character, 1)
        return formatMoveList(moves, character)
    if content.lower() == "lose turn":
        moves = game.getPunishable(characterFile, character, 0)
        return formatMoveList(moves, character)
    searchOutput = game.getPossibleMoves(content, characterFile)
    if isinstance(searchOutput, str):
        return searchOutput
    outputValue = searchOutput[0]
    for i in range(len(searchOutput)):
        if searchOutput[i] == -1:
            continue
        if searchOutput[i][2] > outputValue[2]:
            outputValue = searchOutput[i]
    return game.getMoveEmbed(outputValue[0], outputValue[1], character)

def formatMoveList(moves, character):
    if not isinstance(moves, list):
        return
    e = discord.Embed(title=character)
    headers = moves[1]
    moves = moves[0]
    embedArray = []
    offset = 0
    finished = 0
    listSize = 41
    while(True):
        stringArray = []
        for i in range(offset, offset + listSize):
            if i >= len(moves):
                finished = 1
                break
            stringArray.append([moves[i][0], moves[i][1]])
        embedArray.append("```" + tabulate(stringArray, headers=headers) + "```")
        offset += listSize
        if finished == 1:
            break
    return embedArray
 
async def handleMessage(message):
   prefix = tools.getMessagePrefix(message.content)
   content = tools.getMessageContent(message.content)
   commandSplit = prefix.split("!")
   if commandSplit[0].lower() in ["8frames", "8f"]:
       if commandSplit[1] in ["man", "help"]:
           return getManPage()
       return parseCommand(content, getGame(commandSplit[1]))

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
        content = response[i]
        if isinstance(response[i], discord.embeds.Embed):
            e = response[i]
            content = None
        if response[i] not in ["", None]:
            await message.channel.send(content, embed=e)
        else:
            continue
    return

@client.event
async def on_message_delete(message):
    await trophyProcess("delete", message)

client.run(TOKEN)
