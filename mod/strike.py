from discord.ext import commands
import discord
import yaml

settings = yaml.full_load(open("config.yml"))


class ModCommands(commands.Cog):
         @commands.command(name='strike', help='gives user a strike')
         async def sync(self, ctx, arg1, arg2, *args):
             if settings['modrole'] in [i.name.lower() for i in ctx.author.roles]:
                 user = arg1
                 num = int(arg2)
                 reason = ' '.join(args)
                 warn_embed = discord.Embed(title="Strike", color=0x00ff00)
                 warn_embed.add_field(name=ctx.author,
                     value= "gave " + str(num) + " strike to " + user + " for:\n" + reason,
                     inline=False)
                     
                 if settings['warn_channel']:    
                     print(settings['warn_channel'])
                     channel = discord.Client.get_channel(790757133355974656)
                     await channel.send(embed=warn_embed)
             else:
                 embedVar = discord.Embed(title="Sorry",
                         description="",
                         color=0x00ff00 )
#                  embedVar.add_field(name='not a mod',
#                         value="You are not a mod" ,
#                         inline=False)
                 await ctx.send(embed=embedVar)
