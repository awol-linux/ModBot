from discord.ext import commands
import discord
import mongo
import time
from difflib import get_close_matches
import psutil
import defaults
import asyncio
def sizeof_fmt(num, suffix='B'):
    '''
    Takes a number and returns it in human readable format

    ARGS:
        num: number to convert into human readable format
        suffix: string to append to human readable text

    returns:
        human readable number
    '''
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
    
def is_admin():
    def predicate(ctx):
        if ctx.guild:
            settings = mongo.settings(ctx.guild)
            admin_roles = settings.get('admin_roles').split(';')
            return set([str(i.id) for i in ctx.author.roles]).__and__(set([str(x) for x in admin_roles])) != set() or ctx.author.guild_permissions.administrator
        else:
            return False
    return commands.check(predicate)

def setup(bot):
    bot.add_cog(log_location(bot))
    bot.add_cog(settings_commands(bot))

class log_location(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
  
    @commands.command(name='get_action', help='Returns action item for given pretty name if empty returns full list')
    @is_admin()
    async def get_action(self, ctx, *action_item):
        action_items = mongo.action_items()
        embedVar = discord.Embed(title=None, inline=False)
        self.bot_member = ctx.guild.get_member(self.bot.user.id)
        embedVar.set_author(name=f'{self.bot_member.display_name} | {ctx.command}', icon_url=str(self.bot_member.avatar_url_as(size=512)))
        matches = action_items.get_action_item(action_item)
        print(matches)
        for match in matches:
            embedVar.add_field(name=match['name'], value=", ".join(match['prettys']), inline=False)
        await ctx.reply(embed=embedVar)

class settings_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(name='set_log', help='Archives the complaint putting a full log in admin log')
    @is_admin()
    async def set_log(self, ctx, *action_items):
        if action_items:
            for item in action_items:
                await self.set(ctx, item, ctx.channel.id, 'Log', 'Channel', 'For', item )
        else:
            await self.set(ctx, 'log_channel_id', ctx.channel.id, 'Default', 'Log', 'Channel')


    @commands.command(name='lookup', help='Get the value of a setting')
    @is_admin()
    async def lookup(self, ctx, setting):
        embedVar = discord.Embed(title='', inline=False)
        self.bot_member = ctx.guild.get_member(self.bot.user.id)
        embedVar.set_author(name=f'{self.bot_member.display_name} | {ctx.command}', icon_url=str(self.bot_member.avatar_url_as(size=512)))
        settingkeys = []
        settings = mongo.settings(ctx.guild)
        for setting_list in settings.print_all():
            settingkeys.append(setting_list['name'])
        print(settingkeys)
        matches = (get_close_matches(setting, settingkeys))
        print(matches)
        for match in matches:
            embedVar.add_field(name=match + ' = ' + str(settings.get(match)), value=settings.get_description(setting), inline=False)
        return await ctx.reply(embed=embedVar)

    @commands.command(name='set', help='Changes the value of a setting')
    @is_admin()
    async def set(self, ctx, setting, value, *desc):
        embedVar = discord.Embed(title=None, inline=False)
        print(ctx)
        self.bot_member = ctx.guild.get_member(self.bot.user.id)
        embedVar.set_author(name=f'{self.bot_member.display_name} | {ctx.command}', icon_url=str(self.bot_member.avatar_url_as(size=512)))
        
        settings = mongo.settings(ctx.guild)
        update = settings.update(setting, value, *desc)
        if update:
            embedVar.add_field(name='Old', value=update['oldkey'], inline=True)
            embedVar.add_field(name='New', value=update['newkey'], inline=True)
            embedVar.add_field(name='Description', value=settings.get_description(setting))
            await self.reload(ctx)
            m1 = await ctx.reply(embed=embedVar, content='reloaded')
        else:
            settings.create(setting, value, *desc)
            m1 = await ctx.reply(f"{setting} didn't have any results so i created a new one")
            m2 = await self.lookup(ctx, setting)
            await self.reload(ctx)
            print(ctx.command)
        if str(ctx.command) == 'set_log':
            await ctx.channel.trigger_typing()
            await asyncio.sleep(10)
            await ctx.message.delete()
            await m1.delete()
            try:
                await m2.delete()
            except UnboundLocalError:
                pass
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
        embedVar = discord.Embed(title=None, inline=False)
        self.bot_member = ctx.guild.get_member(self.bot.user.id)
        embedVar.set_author(name=f'{self.bot_member.display_name} | {ctx.command}', icon_url=str(self.bot_member.avatar_url_as(size=512)))
        settings = mongo.settings(ctx.guild)
        settingkeys = []
        for setting in settings.print_all():
            embedVar.add_field(name=setting['name'] + ' = ' + str(setting['value']), value=setting['Description'], inline=False)
        await ctx.reply(embed=embedVar)

    @commands.command(name='ping', help='Replys with server status')
    @is_admin()
    async def ping(self, ctx):
        embedVar = discord.Embed(title=None, inline=True)
        self.bot_member = ctx.guild.get_member(self.bot.user.id)
        embedVar.set_author(name=f'{self.bot_member.display_name} | {ctx.command}', icon_url=str(self.bot_member.avatar_url_as(size=512)))

        time_1 = time.perf_counter()
        await ctx.trigger_typing()
        time_2 = time.perf_counter()
        ping = round((time_2-time_1)*1000)

        embedVar.add_field(name='Ping', value=f"{ping}ms", inline=True)
        embedVar.add_field(name='CPU', value=f"Average {psutil.cpu_percent(interval=1, percpu=False)}% max {max(psutil.cpu_percent(interval=1, percpu=True))}%", inline=True)
        embedVar.add_field(name='Memory', value=f"Available {sizeof_fmt(psutil.virtual_memory().available)} total {sizeof_fmt(psutil.virtual_memory().total)}", inline=True)

        await ctx.reply(embed=embedVar)
 
class help(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            await destination.send(embed=emby)
