import os
import asyncio
import poe
import discord
from discord import app_commands
from dotenv import load_dotenv # new discord bot token library

# Setup variables here
waitingForMessage = False
chatModel = "ChatGPT3"
chatModelCodename = "chinchilla"
bypassPoeLogin = False # For debugging only. Leave this as False during production

load_dotenv()

if bypassPoeLogin == False:
    poeClient = poe.Client(os.getenv('POE_TOKEN'))
    # print(poeClient.bot_names)
    poeClient.send_chat_break("chinchilla")

    with open('starting-prompt.txt', 'r') as file:
        message = file.read()

    # ChatGPT (codename "chinchilla")
    for chunk in poeClient.send_message("chinchilla", message):
        try:
            print(chunk["text_new"], end="", flush=True)
        except:
            print("Something went wrong while connecting to Poe. Aborting program...")
            exit()
    print("\n")

intents = discord.Intents.default()
intents.message_content = True

discordBot = discord.Client(intents = intents)
tree = app_commands.CommandTree(discordBot)

@discordBot.event
async def on_ready():
    servers = discordBot.guilds
    print("Servers I'm currently in:")
    for server in servers:
        print(server.name)
    print('server successfully started as {0.user}'.format(discordBot))
    # discordBot.tree = app_commands.CommandTree(self)
    activity = discord.Activity(type=discord.ActivityType.listening, name="people to chat with (ping me!)")
    await discordBot.change_presence(activity=activity)
    await tree.sync()

@discordBot.event
async def on_message(message):
    global waitingForMessage, chatModelCodename
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    guild = str(message.guild.name)

    if discordBot.user.mentioned_in(message):
        print(f'Pinged in message: {username} on #{channel} in "{guild}": {user_message}')
        print("Paused listening for new messages")
        waitingForMessage = True
        await asyncio.sleep(4)
        async with message.channel.typing():
            for chunk in poeClient.send_message(chatModelCodename, user_message):
                pass
        print(chunk["text"])
        try:
            await message.channel.send(chunk["text"])
        except Exception as err:
            await message.channel.send(f"Error sending message: {err}")
        finally:
            waitingForMessage = False
            print("Resumed listening for new messages")

@tree.command(name="chat", description="Have a chat with ZymBot")
async def chat(interaction: discord.Interaction, *, message: str):
    await interaction.response.defer(ephemeral=False)
    if interaction.user == discordBot.user:
        return
    username = str(interaction.user)
    channel = str(interaction.channel)
    print(f"\x1b[31m{username}\x1b[0m : /chat [{message}] in ({channel})")
    await interaction.followup.send("**Error**: This command has not be programmed yet. Talk to me by pinging me instead!")

@tree.command(name="chat-model", description="Switch to a different chat model")
@app_commands.choices(choices=[
    app_commands.Choice(name="ChatGPT-3.5", value="ChatGPT3"),
    app_commands.Choice(name="Claude", value="Claude"),
    app_commands.Choice(name="Cadence", value="Cadence"),
    app_commands.Choice(name="Firefox", value="NeevaAI")
])
async def chat_model(interaction: discord.Interaction, choices: app_commands.Choice[str]):
    global chatModelCodename
    await interaction.response.defer(ephemeral=False)
    if choices.value == "ChatGPT3":
        chatModelCodename = "chinchilla"
        await interaction.followup.send(f"**INFO: Switched chat model to ChatGPT-3.5 (default)!**\n")
    elif choices.value == "Claude":
        chatModelCodename = "a2"
        await interaction.followup.send(f"**INFO: Switched chat model to Claude!**\n")
    elif choices.value == "Cadence":
        # chatModelCodename = ""
        await interaction.followup.send(f"**INFO**: Cadence model is coming soon!\n")
    elif choices.value == "NeevaAI":
        chatModelCodename = "hutia"
        await interaction.followup.send(f"**INFO: Switched chat model to Firefox!**\n")
    else:
        await interaction.followup.send(f"**INFO: Switching models is coming soon!**\n")

discord_token = os.getenv('DISCORD_TOKEN')
discordBot.run(discord_token)