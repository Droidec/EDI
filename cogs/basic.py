"""
basic.py

Basic EDI commands.
"""

import discord
from discord.ext import commands

# class BasicCommandError(commands.CommandError):
#     """Custom error"""

# class BasicAnotherCommandError(commands.CommandError):
#     """Another custom error"""

class Basic(commands.Cog):
    """EDI basic commands.

    Attributes:
        bot (EDI):
            EDI bot instance.
    """
    def __init__(self, bot):
        """CogBasic initializer.

        Args:
            bot (EDI):
                EDI bot instance.
        """
        self.bot = bot

    @commands.slash_command(name='hello', description='Say hello to the bot.')
    async def hello(self, ctx: discord.ApplicationContext):
        """Mentions and greets author.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
        """
        await ctx.respond(f'Hello {ctx.author.mention}! Nice to meet you.', ephemeral=True)

    @commands.slash_command(name='version', description='Ask the bot version.')
    async def version(self, ctx: discord.ApplicationContext):
        """Send the current version to the author.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
        """
        await ctx.respond(f'My current version is `{self.bot.version}`', ephemeral=True)

    # async def cog_command_error(self, ctx: discord.ApplicationContext, err: discord.ApplicationCommandError) -> None:
    #     """Coroutine called when an exception is raised in the cog.

    #     If it is a specific error managed by this cog, a response is sent to
    #     the author to explain why an error occured. In any case, the generic
    #     error handler of EDI will be called after that to print the traceback.

    #     Args:
    #         ctx (discord.ApplicationContext):
    #             The context of the command that raised the exception.
    #         err (discord.ApplicationCommandError):
    #             The error that was raised.
    #     """
    #     if isinstance(err, BasicCommandError):
    #         await ctx.respond(f'Basic command error {ctx.author.mention}.', ephemeral=True)
    #     elif isinstance(err, BasicAnotherCommandError):
    #         await ctx.respond(f'Another basic command error {ctx.author.mention}.', ephemeral=True)

def setup(bot) -> None:
    """Setup basic commands"""
    bot.add_cog(Basic(bot))
