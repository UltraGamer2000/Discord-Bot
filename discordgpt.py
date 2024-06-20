import discord
from discord.ext import commands
from chatgpt import send_to_chatGPT

import os
from dotenv import load_dotenv
load_dotenv()
Discord_Token = os.getenv('Discord_Token')

import time
start_time = time.time()

import requests
import random
import asyncio

from collections import defaultdict, deque

censored=["lol"]
SPAM_THRESHOLD = 5  
TIME_WINDOW = 10  
FEEDBACK_CHANNEL_ID = 1234567890

user_messages = defaultdict(lambda: deque(maxlen=SPAM_THRESHOLD))
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!',intents=intents)
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.names}')
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if any(word in message.content.lower() for word in censored):
        print(f"Censored word used by {message.author.name}: {message.content}")
        message.delete()
        message.channel.send(f"{message.author.name}, please avoid sending inapproprite content")
        return
    current_time = time.time()
    user_messages[message.author.id].append(current_time)

    if len(user_messages[message.author.id]) == SPAM_THRESHOLD and \
       (current_time - user_messages[message.author.id][0]) < TIME_WINDOW:
        print(f"Spam detected from {message.author.name}")
        await message.channel.send(f"{message.author.mention}, please avoid spamming.")
        user_messages[message.author.id].clear()  
        return
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
    else:
     messages = [{"role":"user","content": message.content}]
     response = send_to_chatGPT(messages)
     await message.channel.send(response)

@bot.command(name='help')
async def help_command(ctx):
    help_message = (
         "**Here are the available commands:**\n"
        "`!ping` - Check the bot's latency.\n"
        "`!serverinfo` - Get information about the server.\n"
        "`!userinfo [user]` - Get information about a specific user or yourself.\n"
        "`!uptime` - Check how long the bot has been running.\n"
        "`!joke` - Get a random joke.\n"
        "`!weather [city]` - Get the weather information for a specified city.\n"
        "`!roll [number_of_dice] [number_of_sides]` - Roll a specified number of dice with a specified number of sides.\n"
        "`!remindme [time_in_seconds] [reminder]` - Set a reminder.\n"
        "`!meme` - Get a random meme from the internet.\n"
        "`!feedback [message]` - Submit anonymous feedback.\n"
        "`!help` - Display this help message."
    )
    await ctx.send(help_message)

@bot.command(name='serverinfo')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='serverinfo')
async def serverinfo(ctx):
    server = ctx.guild
    server_info_message = (
        f"Server Name: {server.name}\n"
        f"Total Members: {server.member_count}\n"
        f"Owner: {server.owner}\n"
        f"Region: {server.region}\n"
        f"Created At: {server.created_at}"
    )
    await ctx.send(server_info_message)

@bot.command(name='uptime')
async def uptime(ctx):
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    uptime_message = f"I've been running for {uptime_seconds // 3600} hours, {(uptime_seconds % 3600) // 60} minutes, and {uptime_seconds % 60} seconds."
    await ctx.send(uptime_message)

@bot.command(name='userinfo')
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    user_info_message = (
        f"User: {member}\n"
        f"Display Name: {member.display_name}\n"
        f"Joined At: {member.joined_at}\n"
        f"Roles: {', '.join(role.name for role in member.roles if role.name != '@everyone')}\n"
        f"Status: {member.status}\n"
        f"Top Role: {member.top_role}\n"
        f"Bot: {member.bot}"
    )
    await ctx.send(user_info_message)

@bot.command(name='joke')
async def joke(ctx):
    response = requests.get('https://official-joke-api.appspot.com/random_joke')
    if response.status_code == 200:
        joke = response.json()
        await ctx.send(f"{joke['setup']}... {joke['punchline']}")
    else:
        await ctx.send("Couldn't retrieve a joke at the moment. Try again later!")

@bot.command(name='weather')
async def weather(ctx, *, city: str):
    api_key = os.getenv('WEATHER_API_KEY')
    response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric')
    if response.status_code == 200:
        weather_data = response.json()
        weather_message = (
            f"Weather in {city}:\n"
            f"Temperature: {weather_data['main']['temp']}°C\n"
            f"Weather: {weather_data['weather'][0]['description']}\n"
            f"Humidity: {weather_data['main']['humidity']}%\n"
            f"Wind Speed: {weather_data['wind']['speed']} m/s"
        )
        await ctx.send(weather_message)
    else:
        await ctx.send(f"Couldn't retrieve weather information for {city}. Please check the city name and try again.")       

@bot.command(name='roll')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [random.randint(1, number_of_sides) for _ in range(number_of_dice)]
    await ctx.send(f'You rolled: {", ".join(map(str, dice))}')

@bot.command(name='remindme')
async def remindme(ctx, time: int, *, reminder: str):
    await ctx.send(f'Reminder set for {time} seconds: {reminder}')
    await asyncio.sleep(time)
    await ctx.send(f'{ctx.author.mention}, here is your reminder: {reminder}')         

@bot.command(name='meme')
async def meme(ctx):
    response = requests.get('https://meme-api.herokuapp.com/gimme')
    if response.status_code == 200:
        data = response.json()
        await ctx.send(data['url'])
    else:
        await ctx.send("Couldn't fetch a meme at the moment. Try again later!")

@bot.command(name='feedback')
async def feedback(ctx, *, message: str):
    feedback_channel = bot.get_channel(FEEDBACK_CHANNEL_ID)
    if feedback_channel:
        await feedback_channel.send(f"Anonymous Feedback:\n{message}")
        await ctx.send("Your feedback has been submitted anonymously. Thank you!")
    else:
        await ctx.send("Unable to submit feedback at the moment. Please try again later.")


bot.run(Discord_Token)