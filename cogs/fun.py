"""
fun.py

Fun EDI commands.
"""

import os
from random import randint

import discord
from discord import Option, OptionChoice
from discord.ext import commands

class Fun(commands.Cog):
    """EDI fun commands.

    Attributes:
        bot (commands.Bot):
            EDI bot instance.
    """
    images = f'{os.path.realpath(os.path.dirname(__file__))}/images'
    dice_image = {
        'd4': f'{images}/d4.png',
        'd6': f'{images}/d6.png',
        'd8': f'{images}/d8.png',
        'd10': f'{images}/d10.png',
        'd12': f'{images}/d12.png',
        'd20': f'{images}/d20.png'
    }

    def __init__(self, bot: commands.Bot):
        """Fun cog initializer.

        Args:
            bot (commands.Bot):
                EDI bot instance.
        """
        self.bot = bot

    @commands.slash_command(name='roll', description='Roll the dice.')
    async def roll(
        self,
        ctx: discord.ApplicationContext,
        sides: Option(
            discord.SlashCommandOptionType.integer,
            name='sides',
            description='How many sides for the dice',
            choices=[
                OptionChoice('d4', 4),
                OptionChoice('d6', 6),
                OptionChoice('d8', 8),
                OptionChoice('d10', 10),
                OptionChoice('d12', 12),
                OptionChoice('d20', 20),
            ]
        ),
        count: Option(
            discord.SlashCommandOptionType.integer,
            name='count',
            description='How many dice to roll',
            min_value=1,
            max_value=100,
            default=1
        )
    ) -> None:
        """Sends an embed with the dices result.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
            sides (int):
                The number of sides of the dice to roll
            count (int):
                The number of rolls
        """
        dice = f'd{sides}'
        rolls = [randint(1, sides) for _ in range(0, count)]
        embed = discord.Embed(
            title=f'{sides}-sided dice • {count} time(s)',
            description=f'You rolled {", ".join(map(str, rolls))}',
            color=discord.Color.blurple()
        )

        (url, file) = self.bot.upload_local_image(self.dice_image[dice])
        embed.set_thumbnail(url=url)

        await ctx.respond(file=file, embed=embed)

def setup(bot) -> None:
    """Setup fun commands"""
    bot.add_cog(Fun(bot))
