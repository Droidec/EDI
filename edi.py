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

    def upload_local_image(self, path: str) -> tuple:
        """Uploads a local image to the Discord API.

        Args:
            path (str):
                The path to the local image

        Returns:
            A tuple containing the url attachment and the Discord file.
        """
        return (f'attachment://{os.path.basename(path)}', discord.File(path))

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
        elif isinstance(err, commands.NotOwner):
            await ctx.respond(f'{ctx.author.mention} This command can be used by my owner only.', ephemeral=True)

        trace = ''.join(traceback.format_exception(type(err), err, err.__traceback__))
        self.logger.error(f'{ctx.author.name}#{ctx.author.discriminator} on {ctx.guild.name} raised an exception with slash command '
                          f'{ctx.command.name}:\n{trace}')

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

    @commands.slash_command(name='hello', description='Say hello to EDI.')
    async def hello(self, ctx: discord.ApplicationContext) -> None:
        """Mentions and greets author.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
        """
        await ctx.respond(f'Hello {ctx.author.mention}! Nice to meet you.', ephemeral=True)

    @commands.slash_command(name='help', description='View basic help and information about EDI.')
    async def help(self, ctx: discord.ApplicationContext) -> None:
        """Sends an embed with all available commands per cogs.

        TODO: display in paginator?

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
        """
        embed = discord.Embed(
            title='Help',
            description='List of available commands. See also builtin Discord menu.',
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name='Useful link',
            value='Source code: https://github.com/Droidec/EDI',
            inline=False
        )

        for cog_name in sorted(self.bot.cogs):
            cog = self.bot.get_cog(cog_name)
            cmds = cog.walk_commands()
            data = []

            for cmd in cmds:
                description = cmd.description.partition('\n')[0]
                if cmd.parent is None:
                    data.append(f'/{cmd.name} - {description}')
                else:
                    data.append(f'/{cmd.parent} {cmd.name} - {description}')

            help_text = '\n'.join(data)

            embed.add_field(
                name=f'{cog_name.capitalize()} commands',
                value=f'```{help_text}```',
                inline=False
            )

        await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(name='test', description='For development purpose.')
    @commands.is_owner()
    async def test(self, ctx: discord.ApplicationContext) -> None:
        """This command is used for development purpose only. Its content
        depends on the owner's need. It should be disabled when not needed.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
        """
        raise commands.DisabledCommand()

    @commands.slash_command(name='version', description='View EDI version.')
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
        help_command=None
    )
    edi.add_cog(Basic(edi))
    edi.load_local_extensions()
    edi.run(edi.config['BOT_TOKEN'])
