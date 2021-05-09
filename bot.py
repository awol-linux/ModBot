# bot.py

import os
from discord.ext import commands
import discord
import mongo
import defaults
from other_commands import help


async def get_pre(bot, message):
    if message.guild is not None:
        settings = mongo.settings(message.guild)
        prefix = settings.get("prefix")
    return prefix


TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix=get_pre,
    status="active",
    help_command=help(),
    intents=intents,
    activity=discord.Activity(type=discord.ActivityType.watching, name="The Mods"),
)


async def on_ready():
    print("Connected to bot: {}".format(bot.user.name))
    print("Bot ID: {}".format(bot.user.id))


@bot.event
async def on_guild_join(guild):
    await defaults.set_defaults(guild)


@bot.listen("on_message")
async def on_ping(message):
    if bot.user.mentioned_in(message):
        pre = await get_pre(bot, message)
        await message.channel.send(f"Prefix is {pre}")


bot.load_extension("logger")
bot.load_extension("other_commands")
bot.run(TOKEN)
