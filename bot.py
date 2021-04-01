# bot.py

import os
from discord.ext import commands
import discord
import mongo 


#if not settings.print_all():
#    import defaults 
#else:
#    print(settings.print_all())
async def get_pre(bot, message):
    if message.guild is not None:
        settings = mongo.settings(message.guild)
        prefix = settings.get('prefix')
    return prefix

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True

bot = commands.Bot(command_prefix=get_pre, 
                   status='active',
                   help_command=help(),
                   intents=intents,
                   activity=discord.Activity(
                       type=discord.ActivityType.watching, 
                       name="The Mods"))

@bot.event
async def on_ready():
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))
#    print('Prefix is: {}'.format(settings.get('prefix')))
#    print('Category ID: {}'.format(settings.get('category_id')))

bot.load_extension('logger')
bot.load_extension('other_commands')
bot.run(TOKEN)
