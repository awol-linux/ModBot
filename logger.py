import os
from discord.ext import commands
import discord
import mongo
import datetime
import typing


def Diff(li1, li2):
    """
    Give two lists and return the diffrances
    """
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

def setup(bot):
    bot.add_cog(public_logger(bot))

# main function
class public_logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.log_handlers = log_handlers(self.bot)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        '''
        If role is mute then log mute
        Else log the role change
        '''
        roles = Diff(before.roles, after.roles)
        self.settings = mongo.settings(after.guild)
        muted_role = self.settings.get('muted_role')
        for role in roles:
            if str(role.id) == str(muted_role):
                action = 'Toggled_Mute'
                roles=None
            else:
                action = "Toggled_Role"

            log_action = discord.AuditLogAction.member_role_update
            guild = after.guild
            entry =  await self.log_handlers.get_audit_log_event(log_action=log_action, guild=guild, user=after, action=action)
            await self.log_handlers.log_event(action=action, entry=entry, roles=roles, guild=guild)
                
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(type(before))
        if before.mute != after.mute:
            action = 'Toggled_VC_Mute'
            log_action = discord.AuditLogAction.member_update
        elif before.deaf != after.deaf:
            action = 'Toggeled_VC_deaf'
            log_action = discord.AuditLogAction.member_update
## discord doesn't target so wauting for privat log
#        elif before.channel != None and after.channel == None:
#            action = 'Kicked_User_From_VC'
#            log_action = discord.AuditLogAction.member_disconnect
        else:
            return True
        self.settings = mongo.settings(member.guild)
        entry = await self.log_handlers.get_audit_log_event(log_action=log_action, guild=member.guild, action=action)
        if entry is not None:
            await self.log_handlers.log_event(action=action, entry=entry, guild=member.guild, target=member)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user: discord.User):
        '''
        Log ban events
        '''
        action = 'Banned'
        log_action = discord.AuditLogAction.ban
        entry =  await self.log_handlers.get_audit_log_event(log_action=log_action, guild=guild, user=user, action=action)
        await self.log_handlers.log_event(action=action, entry=entry, guild=guild)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user: discord.User):
        '''
        Log ban events
        '''
        action = 'Unbanned'
        log_action = discord.AuditLogAction.unban
        entry =  await self.log_handlers.get_audit_log_event(log_action=log_action, guild=guild, user=user, action=action)
        await self.log_handlers.log_event(action=action, entry=entry, guild=guild)

class log_handlers(object):
     def __init__(self, bot):
         self.bot = bot

     async def log_event(self, action=None, entry=None, guild=None, roles=None, target=None):
        '''
        Send event into moderation log
        '''
        # dont log bots because they log themselves
        if entry.user.bot:
            return
        # create embed
        embedVar = discord.Embed(title='Moderation')
        embedVar.add_field(name="Moderator", value=entry.user.mention, inline=True)
        
        # If role that was changed in audit log event 
        if roles is not None:
            for role in roles:
                embedVar.add_field(name="Action", value=action + ' ' + role.mention, inline=True)
        else:
            embedVar.add_field(name="Action", value=action, inline=True)

        # if target is known
        if entry.target is not None:
            target = entry.target
        if target is not None:
            embedVar.add_field(name="Member", value=target.mention, inline=True)

        # If reason exists
        if entry.reason:
            embedVar.add_field(name="Reason", value=entry.reason, inline=False)

        # send log
        log_channel = self.log_location(action, guild)
        if log_channel is not None:
            log = await self.bot.fetch_channel(log_channel)
            await log.send(embed=embedVar)

     async def get_audit_log_event(self, log_action=None, guild=None, action=None, user=None):
        '''
        Get audit log events that match action and target if target exists
        '''
        async for entry in guild.audit_logs(limit=1):
            print(entry)
            if entry.action == log_action:
                if entry.target == user or user == None:
                    return entry

     def log_location(self, log_item, guild):
        self.settings = mongo.settings(guild)
        channel_id = self.settings.get(log_item)
        if channel_id is None:
            channel_id = self.settings.get('log_channel_id')
        return channel_id 
