import os
import discord
from discord.ext import commands
import mongo
import datetime
from typing import Optional, Union


def Diff(li1, li2):
    """
    Give two lists and return the diffrances
    """
    return [i for i in li1 + li2 if i not in li1 or i not in li2]


def setup(bot):
    bot.add_cog(public_logger(bot))


class public_logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.log_handlers = log_handlers(self.bot)

    @commands.Cog.listener()
    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> bool:
        """
        If role is mute then log mute
        Else log the role change
        """

        try:
            role = Diff(before.roles, after.roles)[0]
        except IndexError:
            return True

        self.settings = mongo.settings(after.guild)
        muted_role = self.settings.get("muted_role")
        if str(role.id) == str(muted_role):
            action = "Toggled_Mute"
            role = None
            if str(muted_role) in [str(i.id) for i in after.roles]:
                action_pretty = "Muted"
            else:
                action_pretty = "Unmuted"
        else:
            action = "Toggled_Role"
            if role in after.roles:
                action_pretty = "Gave Role"
            else:
                action_pretty = "Removed Role"

        log_action = discord.AuditLogAction.member_role_update
        guild = after.guild
        entry = await self.log_handlers.get_audit_log_event(
            log_action=log_action,
            guild=guild,
            user=after,
            action=action,
        )

        return await self.log_handlers.log_event(
            action=action,
            entry=entry,
            role=role,
            guild=guild,
            action_pretty=action_pretty,
        )

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> bool:

        if before.mute != after.mute:
            action = "Toggled_VC_Mute"
            if before.mute is False:
                action_pretty = "VC Muted"
            elif before.mute is True:
                action_pretty = "VC Unmute"
            log_action = discord.AuditLogAction.member_update

        elif before.deaf != after.deaf:
            action = "Toggled_VC_deaf"
            if before.deaf is False:
                action_pretty = "VC deafened"
            elif before.deaf is True:
                action_pretty = "VC undeafened"
            log_action = discord.AuditLogAction.member_update

        else:
            return True
        self.settings = mongo.settings(member.guild)
        entry = await self.log_handlers.get_audit_log_event(
            log_action=log_action, guild=member.guild, action=action
        )
        if entry is None:
            return False

        return await self.log_handlers.log_event(
            action=action,
            entry=entry,
            guild=member.guild,
            target=member,
            action_pretty=action_pretty,
        )

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User) -> bool:
        """
        Log ban events
        """
        action = "Banned"
        log_action = discord.AuditLogAction.ban
        entry = await self.log_handlers.get_audit_log_event(
            log_action=log_action, guild=guild, user=user, action=action
        )
        return await self.log_handlers.log_event(
            action=action, entry=entry, guild=guild
        )

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User) -> bool:
        """
        Log ban events
        """
        action = "Unbanned"
        log_action = discord.AuditLogAction.unban
        entry = await self.log_handlers.get_audit_log_event(
            log_action=log_action, guild=guild, user=user, action=action
        )
        return await self.log_handlers.log_event(
            action=action, entry=entry, guild=guild
        )


class log_handlers(object):
    def __init__(self, bot):
        self.bot = bot

    async def log_event(
        self,
        entry: Optional[discord.AuditLogEntry] = None,
        guild: Optional[discord.Guild] = None,
        role: Optional[discord.Role] = None,
        target: Optional[Union[discord.User, discord.Member]] = None,
        action: Optional[str] = None,
        action_pretty: Optional[str] = None,
    ) -> bool:

        """
        Send event into moderation log
        """
        # define bot member object
        self.bot_member = guild.get_member(self.bot.user.id)

        # define action_pretty as action if it's undefined
        if action_pretty == None:
            action_pretty = action

        # Dont log bots because they log themselves
        if entry.user.bot or entry.user == entry.target:
            return

        # create embed
        embedVar = discord.Embed(title="")
        embedVar.set_author(
            name=f"{self.bot_member.display_name} | {action_pretty}",
            icon_url=str(self.bot_member.avatar_url),
        )

        embedVar.add_field(name="Moderator", value=entry.user.mention, inline=True)

        # If role that was changed in audit log event
        if role is not None:
            embedVar.add_field(
                name="Action", value=f"{action_pretty} {role.mention}", inline=True
            )
        else:
            embedVar.add_field(name="Action", value=action_pretty, inline=True)

        # Tf target is known add target and add target_id to footer
        if entry.target is not None:
            target = entry.target
        if target is not None and hasattr(target, "guild"):
            embedVar.add_field(name="Member", value=target.mention, inline=True)
            embedVar.set_footer(text=f"Mod: {entry.user.id} | User: {entry.target.id}")
        elif target is not None and not hasattr(target, "guild"):
            embedVar.add_field(
                name="Member",
                value=f"{target.name}#{target.discriminator}",
                inline=True,
            )
            embedVar.set_footer(text=f"Mod: {entry.user.id} | User: {entry.target.id}")
        elif entry.target is None:
            embedVar.set_footer(text=f"Mod: {entry.user.id}")

        # If reason exists
        if entry.reason is not None:
            embedVar.add_field(name="Reason", value=entry.reason, inline=False)

        # send log
        log_channel = self.log_location(action, guild)
        if log_channel is None:
            return False

        log = await self.bot.fetch_channel(log_channel)
        return await log.send(embed=embedVar)

    async def get_audit_log_event(
        self,
        log_action: Optional[discord.AuditLogAction] = None,
        guild: Optional[discord.Guild] = None,
        action: Optional[str] = None,
        action_pretty: Optional[str] = None,
        user: Optional[Union[discord.User, discord.Member]] = None,
    ) -> discord.AuditLogEntry:
        """
        Get audit log events that match action and target if target exists
        """
        audit_list = await guild.audit_logs(limit=10).flatten()
        for entry in audit_list:
            print(f"Action: {log_action} Entry action: {entry.action}")
            if entry.action == log_action:
                if entry.target == user or user == None:
                    print(
                        f"Action: {entry.action}, User: {entry.user.nick}, Target: {entry.target}. Is user bot: {entry.user.bot}, Guild: {entry.guild}"
                    )
                    return entry

    def log_location(self, log_item: str, guild: discord.Guild) -> int:
        self.settings = mongo.settings(guild)
        return self.settings.get(log_item) or self.settings.get("log_channel_id")
