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
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)

    def load_extensions(self) -> None:
        """Load EDI extensions."""
        for file in os.listdir(f'{os.path.realpath(os.path.dirname(__file__))}/cogs'):
            if file.endswith('.py'):
                extension = file[:-3]
                try:
                    bot.load_extension(f'cogs.{extension}')
                    self.logger.info(f'Loaded extension "{extension}"')
                except Exception as e:
                    exception = f'{type(e).__name__}: {e}'
                    self.logger.error(f'Failed to load extension "{extension}"\n{exception}')

    async def on_ready(self) -> None:
        """Coroutine called when the bot finished logging in."""
        self.logger.info(f'Logged in as {self.user.name}#{self.user.discriminator}')
        self.logger.info(f'EDI API version: {self.version}')
        self.logger.info(f'pycord API version: {discord.__version__}')

    async def on_command_error(self, ctx: commands.Context, err: commands.errors.CommandError) -> None:
        """Coroutine called when an exception is raised in a prefix or mention
        command.

        As EDI only supports slash commands and mention is enabled by default,
        this error handler explicitely say that it does not support such
        commands and print the traceback in any case.
        """
        await ctx.send(f'I only support slash commands {ctx.author.mention}. Give it a try with the `/help` command.')

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
            await ctx.respond(f'I do not known this command {ctx.author.mention}.', ephemeral=True)
        elif isinstance(err, commands.DisabledCommand):
            await ctx.respond(f'This command is disabled {ctx.author.mention}.', ephemeral=True)

        trace = ''.join(traceback.format_exception(type(err), err, err.__traceback__))
        self.logger.error(f'{ctx.author.name}#{ctx.author.discriminator} on {ctx.guild.name} raised an exception with slash command '
                          f'{ctx.command.name}:{ctx.command.options}:\n{trace}')

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='EDI discord bot')
    parser.add_argument('json_file', help='JSON configuration file')
    args = parser.parse_args()

    # Load JSON configuration
    if not os.path.isfile(args.json_file):
        sys.exit('JSON configuration file not found! Please try again.')

    with open(args.json_file, encoding='utf-8') as file:
        json_config = json.load(file)

    # Start bot
    intents = discord.Intents.default()
    intents.message_content = True
    bot = EDI(
        config=json_config,
        intents=intents,
        help_command=None,
    )
    bot.load_extensions()
    bot.run(bot.config['BOT_TOKEN'])
