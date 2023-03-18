"""
edi.py

EDI Discord bot.
"""

import json
import logging
import os
import sys
from argparse import ArgumentParser

import discord
from discord.ext import commands

class EDI(commands.Bot):
    """EDI skeleton

    Attributes:
        config (dict):
            The bot configuration
        logger (logging.Logger):
            The bot logger
    """
    def __init__(self, config: dict, **options):
        """EDI initializer

        Args:
            config (dict):
                The bot configuration
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
        """Load EDI extensions"""
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
        """Coroutine called when the bot finished logging in"""
        self.logger.info(f'Logged in as {self.user.name}:{self.user.id}')
        self.logger.info(f'pycord API version: {discord.__version__}')

if __name__ == '__main__':
    # Parse arguments
    parser = ArgumentParser(description='EDI discord bot')
    parser.add_argument('json_file', help='JSON configuration file')
    args = parser.parse_args()

    # Load JSON configuration
    if not os.path.isfile(args.json_file):
        sys.exit('JSON configuration file not found! Please try again.')

    with open(args.json_file, encoding='utf-8') as file:
        json_config = json.load(file)

    # Start bot
    bot = EDI(
        config=json_config,
        intents=discord.Intents.default(),
    )
    bot.load_extensions()
    bot.run(bot.config['BOT_TOKEN'])
