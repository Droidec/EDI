"""
edi.py

EDI Discord bot.
"""

import argparse
import json
import logging
import os
import sys
import traceback

import discord
from discord.ext import commands
from discord.ext.pages import Paginator, Page

EDI_VERSION = '1.0.0'

class EDI(commands.Bot):
    """EDI skeleton.

    Attributes:
        version (str):
            The bot version.
        config (dict):
            The bot configuration.
        logger (logging.Logger):
            The bot logger.
    """
    version = EDI_VERSION

    def __init__(self, config: dict, **options):
        """EDI initializer.

        Args:
            config (dict):
                The bot configuration.
        """
        super().__init__(**options)

        # Set configuration
        self.config = config

        # Set logger
        self.logger = logging.getLogger('discord')
        self.logger.setLevel(config['LOG_LEVEL'])
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)

    def load_local_extensions(self) -> None:
        """Load EDI local extensions."""
        for file in os.listdir(f'{os.path.realpath(os.path.dirname(__file__))}/cogs'):
            if file.endswith('.py'):
                extension = file[:-3]
                try:
                    self.load_extension(f'cogs.{extension}')
                    self.logger.info(f'Loaded extension "{extension}"')
                except Exception as err:
                    exception = f'{type(err).__name__}: {err}'
                    self.logger.error(f'Failed to load extension "{extension}"\n{exception}')

    async def on_ready(self) -> None:
        """Coroutine called when the bot finished logging in."""
        self.logger.info(f'Logged in as {self.user.name}#{self.user.discriminator}')
        self.logger.info(f'EDI API version: {self.version}')
        self.logger.info(f'pycord API version: {discord.__version__}')
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='/help'))

    async def on_command_error(self, ctx: commands.Context, err: commands.errors.CommandError) -> None:
        """Coroutine called when an exception is raised in a prefix or mention
        command.

        As EDI only supports slash commands and mention is enabled by default,
        this error handler explicitely say that it does not support such
        commands and print the traceback in any case.
        """
        await ctx.send(f'{ctx.author.mention} I only support slash commands. Give it a try with the `/help` command.')

        trace = ''.join(traceback.format_exception(type(err), err, err.__traceback__))
        self.logger.error(f'{ctx.author.name}#{ctx.author.discriminator} on {ctx.guild.name} tried to use a prefix/mention command:\n'
                          f'{trace}')

    async def on_application_command_error(self, ctx: discord.ApplicationContext, err: discord.errors.DiscordException) -> None:
        """Coroutine called when an exception is raised in a slash command.

        This error handler responds to the author for generic errors and print
        the traceback in any case.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command that raised the exception.
            err (discord.errors.DiscordException):
                The error that was raised.
        """
        if isinstance(err, commands.CommandNotFound):
            await ctx.respond(f'{ctx.author.mention} I do not known this command.', ephemeral=True)
        elif isinstance(err, commands.DisabledCommand):
            await ctx.respond(f'{ctx.author.mention} This command is disabled.', ephemeral=True)
        elif isinstance(err, commands.MissingPermissions):
            await ctx.respond(f'{ctx.author.mention} {str(err)}', ephemeral=True)

        trace = ''.join(traceback.format_exception(type(err), err, err.__traceback__))
        self.logger.error(f'{ctx.author.name}#{ctx.author.discriminator} on {ctx.guild.name} raised an exception with slash command '
                          f'{ctx.command.name}:{ctx.command.options}:\n{trace}')

class Basic(commands.Cog):
    """EDI basic commands.

    These commands are loaded by EDI in any circumstances.

    Attributes:
        bot (commands.Bot):
            EDI bot instance.
    """
    def __init__(self, bot: commands.Bot):
        """Basic cog initializer.

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

        TODO: embed footer with timestamp and avatar?

        TODO: develop an embed page system because of the limited size of data
        we can display

        TODO: optional argument to have commands for a specific cog?

        TODO: optional argument to display in non-ephemeral if admin?

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
        """
        embed = discord.Embed(
            title='Help',
            description='List of available commands.',
            color=discord.Color.blurple(),
        )

        # Useful links
        embed.add_field(
            name='Useful links',
            value='- Source code: https://github.com/Droidec/EDI',
            inline=False,
        )

        for cog_name in sorted(self.bot.cogs):
            cog = self.bot.get_cog(cog_name)
            cmds = cog.get_commands()
            data = []

            for cmd in cmds:
                description = cmd.description.partition('\n')[0]
                data.append(f'/{cmd.name} - {description}')

            help_text = '\n'.join(data)

            # Cog commands
            embed.add_field(
                name=f'{cog_name.capitalize()} commands',
                value=f'```{help_text}```',
                inline=False,
            )

        await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(name='test', description='For development purpose (admin only).')
    @commands.has_permissions(administrator=True)
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
        await ctx.respond(f'{ctx.author.mention} My current version is `{self.bot.version}`.', ephemeral=True)

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='EDI discord bot')
    parser.add_argument('json_config', help='JSON configuration file')
    args = parser.parse_args()

    # Load JSON configuration
    if not os.path.isfile(args.json_config):
        sys.exit('JSON configuration file not found! Please try again.')

    with open(args.json_config, encoding='utf-8') as json_file:
        json_config = json.load(json_file)

    # Start bot
    intents = discord.Intents.default()
    intents.message_content = True
    edi = EDI(
        config=json_config,
        intents=intents,
        help_command=None,
    )
    edi.add_cog(Basic(edi))
    edi.load_local_extensions()
    edi.run(edi.config['BOT_TOKEN'])
