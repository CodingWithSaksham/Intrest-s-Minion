from asyncio import sleep
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext.commands import UserNotFound

from utils.settings import *

time_dict = {'s': 1, 'm': 60, 'd': 86400, 'h': 3600, 'w': 604800}
logger = logging.getLogger('bot')
formatted_time_limit = ''


class Staff(app_commands.Group):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

        # Gets the logging channel
        self.logging_channel = bot.get_channel(LOGGING_CHANNEL)

    @app_commands.command(name='voice_mute')
    @app_commands.describe(member='The member to mute from voice channel',
                           reason='The reason for the mute',
                           time_limit='How long is the number timed out for? (use s/m/h/w)')
    @app_commands.checks.cooldown(1, 20)
    @app_commands.checks.has_permissions(mute_members=True)
    async def mute_from_voice(self, interaction: discord.Interaction, member: discord.Member, reason: str, time_limit: str):
        """Mutes a member from the voice"""

        global formatted_time_limit

        # Checks if given a time format is in seconds, minutes, hours, etc. If yes converts it into seconds
        if time_limit[-1].lower() in time_dict:
            formatted_time_limit = timedelta(seconds=(int(time_limit[:-1]) * time_dict[time_limit[-1]]))

        # Edits members permission to not speak in a voice channel and sends the user a DM saying that they got muted
        await member.edit(mute=True, reason=reason, timed_out_until=discord.utils.utcnow() + formatted_time_limit)
        await member.send(f'Voice Muted by {interaction.user} for reason: {reason} till {time_limit}')
        await interaction.response.send_message(f'Voice Muted {member.mention} for reason: {reason}', ephemeral=True, delete_after=5)

        # Sends a log to the bot log saying member got muted from a voice channel by a mod for reason and time limit
        await self.logging_channel.send(f'{interaction.user.mention} voice muted {member.mention} from channel {member.voice.channel} '
                                        f'for reason: {reason} and timed out for {time_limit}')

    @app_commands.command(name='mute')
    @app_commands.describe(member='The member to mute',
                           reason='The reason for the mute',
                           time_limit='How long is the number timed out for? (use s/m/h/w)')
    @app_commands.checks.cooldown(1, 20)
    @app_commands.checks.has_permissions(mute_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, reason: str = None, time_limit: str = None):
        """Mutes the member"""

        global formatted_time_limit

        # Checks if given a time format is in seconds, minutes, hours, etc. If yes converts it into seconds
        if time_limit is not None and time_limit[-1].lower() in time_dict:
            time_limit = int(time_limit[:-1]) * time_dict[time_limit[-1]]

        # Fetches the muted role from the guild
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")

        # Adds the 'Muted' role to the user and sends them a DM saying they got muted
        await member.add_roles(muted_role, reason=reason)
        await member.send(f'Muted by {interaction.user} for reason: {reason}')
        await interaction.response.send_message(f'Muted {member.mention} for reason: {reason} for duration {time_limit}',
                                                ephemeral=True, delete_after=5)

        # Removed the muted role after a time limit
        if time_limit:
            await sleep(time_limit)
            await member.remove_roles(muted_role)

        # Logging the interaction
        await self.logging_channel.send(f'{interaction.user} muted {member.mention} for reason: {reason} for time limit {time_limit}')

    @app_commands.command(name='voice_unmute')
    @app_commands.describe(member='The member to un-mute from voice channel')
    @app_commands.checks.cooldown(1, 20)
    @app_commands.checks.has_permissions(mute_members=True)
    async def voice_unmute(self, interaction: discord.Interaction, member: discord.Member):
        """Unmute a member from the voice channel"""

        # Unmute the member
        await member.edit(mute=False)
        await interaction.response.send_message(f'Un-muted {member.mention}', ephemeral=True, delete_after=5)
        await member.send(f'You have been Un-muted by {interaction.user} for')

        # Logs the interaction
        await self.logging_channel.send(f'{interaction.user} un-muted from voice {member.mention}')

    @app_commands.command(name='unmute')
    @app_commands.describe(member='The member to un-mute')
    @app_commands.checks.cooldown(1, 20)
    @app_commands.checks.has_permissions(mute_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        """Unmute a member"""

        # Fetches the muted role and removed it from member
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        await member.remove_roles(muted_role)
        await interaction.response.send_message(f'Un-muted {member.mention}', ephemeral=True, delete_after=5)

        # Log the interaction
        await self.logging_channel.send(f'{interaction.user} un-muted {member.mention}')

    @app_commands.command(name='kick')
    @app_commands.describe(member='The member to kick',
                           reason='The reason to kick the member')
    @app_commands.checks.cooldown(1, 20)
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """Kicks a member"""

        # Kicks the member
        await member.kick(reason=reason)
        await interaction.response.send_message(f'Kicked {member.mention}!', ephemeral=True, delete_after=5)

        # Checks if reason is None or not
        if reason:
            await member.send(f'You have been kicked from {interaction.guild} by {interaction.user} with reason: {reason}.')
        else:
            await member.send(f'You have been from {interaction.guild} by {interaction.user}.')

        # Log the interaction
        await self.logging_channel.send(f'{interaction.user} un-muted {member.mention}')

    @app_commands.command(name='ban')
    @app_commands.describe(member='The member to ban',
                           reason='The reason of banning this member',
                           time_limit='The duration of the ban (in s/m/d/w)')
    @app_commands.checks.cooldown(1, 20)
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str, time_limit: str = None):
        """Bans a member"""
        global formatted_time_limit

        member_id = discord.utils.get(interaction.guild.members, id=member.id)
        await member.send(f'You have been **banned** from {interaction.guild} by {interaction.user} with reason: {reason}.')

        # Checks if given a time format is in seconds, minutes, hours, etc. If yes converts it into seconds
        if time_limit[-1].lower() in time_dict:
            formatted_time_limit = int(time_limit[:-1]) * time_dict[time_limit[-1]]

        await interaction.response.send_message(f'Banned {member.mention}!', ephemeral=True, delete_after=5)
        await interaction.guild.ban(member, reason=reason, delete_message_seconds=0)

        if time_limit is not None:
            await sleep(formatted_time_limit)
            await interaction.guild.unban(member_id)

        # Log the interaction
        await self.logging_channel.send(f'{interaction.user} banned {member.mention} for reason: {reason}, time limit {time_limit}')

    @app_commands.command(name='unban')
    @app_commands.checks.cooldown(1, 20)
    @app_commands.describe(member='The member to unban(MUST USE MEMBER ID)')
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, member: discord.User):
        """Unbans the specified user"""

        # Tries to unban the user
        try:
            await interaction.guild.unban(member)
        except UserNotFound:
            interaction.response.send_message('User not found or wrong user id given', ephemeral=True, delete_after=5)

        # Log the interaction
        await self.logging_channel.send(f'{interaction.user} unbanned {member.mention}')

    @app_commands.command(name='clear')
    @app_commands.checks.cooldown(1, 2)
    @app_commands.describe(amount='The amount of messages to delete')
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        """Clears a specific number of messages from the server"""

        # Removing the messages
        await interaction.response.send_message(f'Clearing {amount} messages!', delete_after=5)
        await interaction.channel.purge(limit=amount)

        # Log the interaction
        await self.logging_channel.send(f'{interaction.user.mention} cleared {amount} messages from {interaction.channel.mention}')
