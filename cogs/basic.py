"""
basic.py

Basic EDI commands.
"""

import discord
from discord.ext import commands
from discord.ext.pages import Paginator, Page

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
    def __init__(self, bot: commands.Bot):
        """CogBasic initializer.

        Args:
            bot (commands.Bot):
                EDI bot instance.
        """
        self.bot = bot

    @commands.slash_command(name='hello', description='Say hello to the bot.')
    async def hello(self, ctx: discord.ApplicationContext) -> None:
        """Mentions and greets author.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
        """
        await ctx.respond(f'Hello {ctx.author.mention}! Nice to meet you.', ephemeral=True)

    @commands.slash_command(name='help', description='Show all available commands.')
    async def help(self, ctx: discord.ApplicationContext) -> None:
        """Sends an embed with all available commands per cogs.

        TODO: develop an embed page system because of the limited size of data
        we can display

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
        """
        embed = discord.Embed(
            title='Help',
            description='List of available commands.',
            color=discord.Color.blurple(),
        )

        for cog_name in self.bot.cogs:
            cog = self.bot.get_cog(cog_name)
            cmds = cog.get_commands()
            data = []

            for cmd in cmds:
                description = cmd.description.partition('\n')[0]
                data.append(f'/{cmd.name} - {description}')

            help_text = '\n'.join(data)
            embed.add_field(
                name=f'{cog_name.capitalize()} commands',
                value=f'```{help_text}```',
                inline=False,
            )

        await ctx.respond(embed=embed)

    @commands.slash_command(name='test', description='For development purpose only.')
    async def test(self, ctx: discord.ApplicationContext) -> None:
        """This command is used for development purpose only. Its content
        depends on the developer's need. It should be disabled when not needed.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
        """
        pages = []

        for i in range(1, 50):
            embed = discord.Embed(
                title=f'Embed 1-{i}'
            )
            pages.append(Page(embeds=[embed]))

        await Paginator(
            pages=pages,
            timeout=10.0
        ).respond(ctx.interaction)

    @commands.slash_command(name='version', description='Ask the bot version.')
    async def version(self, ctx: discord.ApplicationContext) -> None:
        """Sends the current version to the author.

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
