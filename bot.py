# bot.py

import os
import yaml
import discord
from discord.ext import commands
from dotenv import load_dotenv
from mod.strike import ModCommands


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
settings = yaml.full_load(open("config.yml"))
bot = commands.Bot(command_prefix=settings['prefix'])

#mod.strike.init(settings)
# bot.add_cog(HelpOthers())
bot.add_cog(ModCommands())

bot.run(TOKEN)
