"""
basic.py

Basic EDI commands.
"""

import discord
from discord.ext import commands

class Basic(commands.Cog):
    """EDI basic commands

    Attributes:
        bot (EDI):
            EDI bot instance
    """
    def __init__(self, bot):
        """CogBasic initializer

        Args:
            bot (EDI):
                EDI bot instance
        """
        self.bot = bot

    @commands.slash_command(name='hello', description='Say hello to EDI')
    async def hello(self, ctx: discord.ApplicationContext):
        """Mentions and greets user

        Args:
            ctx (discord.ApplicationContext):
                The context of the command
        """
        await ctx.respond(f'Hello {ctx.author.mention}!')

def setup(bot) -> None:
    """Setup basic commands"""
    bot.add_cog(Basic(bot))
