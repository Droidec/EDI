"""
plex.py

Plex EDI commands.
"""

import discord
from discord.ext import commands

class PlexNoMatchingResults(commands.CommandError):
    """Plex no matching results"""

class PlexAlbumNotFound(commands.CommandError):
    """Plex album not found"""

class Plex(commands.Cog):
    """EDI plex commands.

    Attributes:
        bot (commands.Bot):
            EDI bot instance.
    """

    plex_group = discord.SlashCommandGroup('plex')

    def __init__(self, bot: commands.Bot):
        """Plex cog initializer.

        Args:
            bot (commands.Bot):
                EDI bot instance.
        """
        self.bot = bot

    @plex_group.command(name='search', description='Search album by keyword.')
    async def search(self, ctx: discord.ApplicationContext) -> None:
        """TODO
        """
        await ctx.respond('search')

    @plex_group.command(name='info', description='View album informations.')
    async def info(self, ctx: discord.ApplicationContext) -> None:
        """TODO
        """
        await ctx.respond('info')

    async def cog_command_error(self, ctx: discord.ApplicationContext, err: discord.ApplicationCommandError) -> None:
        """Coroutine called when an exception is raised in the cog.

        If it is a specific error managed by this cog, a response is sent to
        the author to explain why an error occured. In any case, the generic
        error handler of EDI will be called after that to print the traceback.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command that raised the exception.
            err (discord.ApplicationCommandError):
                The error that was raised.
        """
        if isinstance(err, PlexNoMatchingResults):
            await ctx.respond(f'{ctx.author.mention} Your search did not match any results on the Plex server.', ephemeral=True)
        elif isinstance(err, PlexAlbumNotFound):
            await ctx.respond(f'{ctx.author.mention} The album you requested was not found on the Plex server.', ephemeral=True)

def setup(bot) -> None:
    """Setup Plex commands"""
    bot.add_cog(Plex(bot))
