"""
fun.py

Fun EDI commands.
"""

import discord
from discord.ext import commands

class Fun(commands.Cog):
    """EDI fun commands.

    Attributes:
        bot (commands.Bot):
            EDI bot instance.
    """
    def __init__(self, bot: commands.Bot):
        """Fun cog initializer.

        Args:
            bot (commands.Bot):
                EDI bot instance.
        """
        self.bot = bot

    @commands.slash_command(name='roll', description='Roll dices and sum the result.')
    async def roll(self, ctx: discord.ApplicationContext) -> None:
        """TODO
        """
        await ctx.respond(f'{ctx.author.mention} This command is currently not implemented.', ephemeral=True)

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
    #     if isinstance(err, FunCommandError):
    #         await ctx.respond(f'Fun command error {ctx.author.mention}.', ephemeral=True)
    #     elif isinstance(err, FunAnotherCommandError):
    #         await ctx.respond(f'Another fun command error {ctx.author.mention}.', ephemeral=True)

def setup(bot) -> None:
    """Setup fun commands"""
    bot.add_cog(Fun(bot))
