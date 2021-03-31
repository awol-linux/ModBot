import os
from discord.ext import commands
import discord
import mongo
import datetime
import typing

settings = mongo.settings()
log_channel_id = settings.get('log_channel_id')
def Diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

def setup(bot):
    bot.add_cog(public_logger(bot))

# main function
class public_logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        roles = Diff(before.roles,  after.roles)
        muted_role = settings.get('muted_role')
        for role in roles:
            if role.id == muted_role:
                action = 'Toggled mute'
                roles=None
            else:
                action = "Toggled Role(s)"

            log_action = discord.AuditLogAction.member_role_update
            guild = after.guild
            entry =  await self.get_audit_log_event(log_action=log_action, guild=guild, user=after, action=action)
            await self.log_event(action, entry, roles)
                
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user: discord.User):
        action = 'Banned'
        log_action = discord.AuditLogAction.ban
        entry =  await self.get_audit_log_event(log_action=log_action, guild=guild, user=user, action=action)
        await self.log_event(action, entry)

    async def log_event(self, action=None, entry=None, roles=None): 
        admin_log = await self.bot.fetch_channel(log_channel_id)
        embedVar = discord.Embed(title='Moderaton')
        embedVar.add_field(name="Moderator", value=entry.user.mention, inline=True)
        if roles is not None:
            for role in roles:
                embedVar.add_field(name="Action", value=action + ' ' + role.mention, inline=True)
        else:
            embedVar.add_field(name="Action", value=action, inline=True)
        embedVar.add_field(name="Member", value=entry.target.mention, inline=True)
        if entry.reason:
            embedVar.add_field(name="Reason", value=entry.reason, inline=False)
        await admin_log.send(embed=embedVar)
 
    async def get_audit_log_event(self, log_action=None, guild=None, action=None, user=None):
        async for entry in guild.audit_logs(limit=10):
            if entry.action == log_action:
                if entry.target == user or user == None:
                    return entry
