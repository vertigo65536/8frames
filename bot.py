import discord, os
import tools, t7, sfv, sf4, sf3
from dotenv import load_dotenv

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


async def handleMessage(message):
   prefix = tools.getMessagePrefix(message.content)
   content = tools.getMessageContent(message.content)
   commandSplit = prefix.split("!")
   if commandSplit[0].lower() in ["8frames", "8f"]:
       if commandSplit[1] in "man, help":
           return getManPage()
       return getGame(commandSplit[1]).parseCommand(content)

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
