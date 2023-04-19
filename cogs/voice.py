"""
plex.py

Voice EDI commands.
"""

import discord
from discord import Option
from discord.ext import commands

class VoiceNoChannel(commands.CommandError):
    """Voice no channel"""

class VoiceNotConnected(commands.CommandError):
    """Voice not connected"""

class Voice(commands.Cog):
    """EDI voice commands.

    Attributes:
        bot (commands.Bot):
            EDI bot instance.
    """
    def __init__(self, bot: commands.Bot):
        """Voice cog initializer.

        Args:
            bot (commands.Bot):
                EDI bot instance.
        """
        self.bot = bot

    @commands.slash_command(name='join', description='Join a voice channel.')
    @commands.has_permissions(administrator=True)
    async def join(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(
            discord.channel.VoiceChannel,
            name='channel',
            description='The voice channel to join',
            default=None
        )
    ) -> None:
        """Joins a voice channel or the user voice channel.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
            channel (discord.channel.VoiceChannel):
                The channel to join, if any.

        Raises:
            VoiceNoChannel:
                No channel to join (either the user did not specified one or the
                user is not in a voice channel)
        """
        if channel is None:
            # Get author voice channel
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise VoiceNoChannel('No channel to join. Please either specifiy a valid channel or join one first')

        if ctx.guild.voice_client is not None:
            # Move bot if already in a voice channel
            await ctx.guild.voice_client.move_to(channel)
        else:
            # Connect bot to a voice channel
            await channel.connect()

        await ctx.respond(f'Joining `{channel}`')

    @commands.slash_command(name='leave', description='Leave the current voice channel.')
    @commands.has_permissions(administrator=True)
    async def leave(self, ctx: discord.ApplicationContext) -> None:
        """Leaves the current voice channel.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
        """
        channel = ctx.guild.voice_client.channel
        await ctx.guild.voice_client.disconnect(force=True)
        await ctx.respond(f'Left `{channel}`')

    @leave.before_invoke
    async def ensure_voice(self, ctx: discord.ApplicationContext) -> None:
        """Ensures that EDI is in a voice channel.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.

        Raises:
            VoiceNotConnected:
                EDI is not in a voice channel.
        """
        if ctx.guild.voice_client is None:
            raise VoiceNotConnected()

    async def cog_command_error(self, ctx: discord.ApplicationContext, err: discord.ApplicationCommandError) -> None:
        """Coroutine called when an exception is raised in the cog.

        If it is a specific error managed by this cog, a response is sent to
        the user to explain why an error occured. In any case, the generic
        error handler of EDI will be called after that to print the traceback.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command that raised the exception.
            err (discord.ApplicationCommandError):
                The error that was raised.
        """
        if isinstance(err, VoiceNoChannel):
            await ctx.respond(f'{ctx.author.mention} {str(err)}', ephemeral=True)
        elif isinstance(err, VoiceNotConnected):
            await ctx.respond(f'{ctx.author.mention} I\'m not currently in a voice channel', ephemeral=True)

def setup(bot) -> None:
    """Setup voice commands"""

    bot.add_cog(Voice(bot))
