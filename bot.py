import discord, os
import tools, t7
from dotenv import load_dotenv

def getGame(string):
    if string == "t7":
        return t7

async def handleMessage(message):
   prefix = tools.getMessagePrefix(message.content)
   content = tools.getMessageContent(message.content)
   commandSplit = prefix.split("!")
   if commandSplit[0] in ["8frames", "8f"]:
       return getGame(commandSplit[1]).parseCommand(content)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    
@client.event    
async def on_message(message):
    if message.author == client.user:
        return
    response = await handleMessage(message)
    e = None
    content = response
    if isinstance(response, discord.embeds.Embed):
        e = response
        content = None
    if response != "" and response != None:
        await message.channel.send(content, embed=e)
    else:
        return

@client.event
async def on_message_delete(message):
    await trophyProcess("delete", message)

client.run(TOKEN)
