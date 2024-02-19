import os
import datetime
import asyncio

import discord
import asyncpraw
from dotenv import load_dotenv
from discord.ext import tasks

load_dotenv() # Loads discord bot token from .env file
bot = discord.Bot() # Creates bot instance
channel = None

# Creates a read-only Reddit Instance
reddit = asyncpraw.Reddit(
    client_id = os.getenv("R_CLIENT_ID"),
    client_secret = os.getenv("R_CLIENT_SECRET"),
    user_agent = os.getenv("R_USER_AGENT"),
)

# override on_ready function to alert bot is online and start task loop
@bot.event
async def on_ready():
    print(f"{bot.user} is online")
    await bot.wait_until_ready()
    global channel
    channel = bot.get_channel(os.getenv("SERVER_MSG_CHANNEL"))
    chaptercheck.start()

# slash command /latestopm to get latest opm chapter from sub
@bot.command(brief="Get the latest OPM chapter")
async def latestopm(ctx):
    opm_sub = await reddit.subreddit("OnePunchMan")
    post = opm_sub.search(query = "flair:Murata Chapter", sort = "new", time_filter = "all", limit=1)
    async for x in post:
        post_title = x.title
        post_url = x.url

    embed = discord.Embed(
        title=post_title,
        url=post_url,
    )

    await ctx.respond(content="Latest Chapter",embed=embed)

# task loop for daily check of new chapters @7pm Central (UTC-6)
@tasks.loop(time = datetime.time(hour=1))
async def chaptercheck():
    subreddit = await reddit.subreddit("OnePunchMan")
    post = subreddit.search(query = "flair:Murata Chapter", sort = "new", time_filter = "day", limit=1)

    post_title=None
    post_url=None
    async for x in post:
        post_title = x.title
        post_url = x.url
    if(post_title):
        embed = discord.Embed(
            title=post_title,
            url=post_url,
        )
        await channel.send(content="NEW CHAPTER",embed=embed)

# shutdown command
@bot.command()
async def shutdown(ctx):
    print("Shutting down...")
    await reddit.close()
    await bot.close()

bot.run(os.getenv("TOKEN")) # Run the bot with the token