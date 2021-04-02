from discord.ext import commands
import discord
import mongo
import time
from difflib import get_close_matches
import psutil
import defaults

#settings = mongo.settings()
#log_channel_id = settings.get('log_channel_id')

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

    
def is_admin():
    def predicate(ctx):
        if ctx.guild:
            settings = mongo.settings(ctx.guild)
            admin_roles = settings.get('admin_roles')
            perms = False
            for role in ctx.author.roles:
                if str(role.id) in str(admin_roles).split(';'):
                    perms = True
            if ctx.author.guild_permissions.administrator:
                perms = True
            print(perms)
            return perms
        else:
            print(False)
            return False
    return commands.check(predicate)    

def setup(bot):
    bot.add_cog(admin(bot))
    bot.add_cog(settings_commands(bot))

class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(name='ping', help='Archives the complaint putting a full log in admin log')
    @is_admin()
    async def ping(self, ctx):
        time_1 = time.perf_counter()
        await ctx.trigger_typing()
        time_2 = time.perf_counter()
        ping = round((time_2-time_1)*1000)
        embedVar = discord.Embed(title='status', inline=True)
        embedVar.add_field(name='Ping', value=ping, inline=True)
        embedVar.add_field(name='CPU', value=f"Average {psutil.cpu_percent(interval=1, percpu=False)} max {max(psutil.cpu_percent(interval=1, percpu=True))}", inline=True)
        embedVar.add_field(name='Memory', value=f"Available {sizeof_fmt(psutil.virtual_memory().available)} total {sizeof_fmt(psutil.virtual_memory().total)}", inline=True)

        await ctx.reply(embed=embedVar)
   
class settings_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(name='lookup', help='Get the value of a setting')
    @is_admin()
    async def lookup(self, ctx, arg):
        settingkeys = []
        settings = mongo.settings(ctx.guild)
        for setting in settings.print_all():
            settingkeys.append(setting['name'])
        embedVar = discord.Embed(title='Settings', inline=False)
        matches = (get_close_matches(arg, settingkeys))
        for match in matches:
            embedVar.add_field(name=match + ' = ' + str(settings.get(match)), value=settings.get_description(arg), inline=False)
        await ctx.reply(embed=embedVar)

    @commands.command(name='set', help='Changes the value of a setting')
    @is_admin()
    async def set(self, ctx, arg1, arg2 , *args):
        settings = mongo.settings(ctx.guild)
        embedVar = discord.Embed(title='Settings', inline=False)
        update = settings.update(arg1, arg2)
        if update:
            embedVar.add_field(name='Old', value=update['oldkey'], inline=True)
            embedVar.add_field(name='New', value=update['newkey'], inline=True)
            embedVar.add_field(name='Description', value=settings.get_description(arg1))
            await self.reload(ctx)
            await ctx.reply(embed=embedVar, content='reloaded')
        else:
            create = settings.create(arg1, arg2, *args)
            await ctx.reply(f"{arg1} didn't have any results so i created a new one")
            await(self.lookup(ctx, arg1))
            await self.reload(ctx)
            

    @commands.command(name='reload', help='Manually reload config')
    @is_admin()
    async def reload(self, ctx):
        await ctx.channel.trigger_typing()
        self.bot.reload_extension('other_commands')
        if str(ctx.command) == 'reload':
            await ctx.reply('reloaded')

    @commands.command(name='show', help='Shows the settings and their value')
    @is_admin()
    async def show(self, ctx):
        settings = mongo.settings(ctx.guild)
        settingkeys = []
        embedVar = discord.Embed(title='Settings', inline=False)
        for setting in settings.print_all():
            embedVar.add_field(name=setting['name'] + ' = ' + str(setting['value']), value=setting['Description'], inline=False)
        await ctx.reply(embed=embedVar)

    @commands.command(name='set_log', help='Archives the complaint putting a full log in admin log')
    @is_admin()
    async def set_log(self, ctx):
        await self.set(ctx, 'log_channel_id', ctx.channel.id)



class help(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            await destination.send(embed=emby)
