"""
EDI Discord bot.
"""

import json
import logging
import os
import sys
from argparse import ArgumentParser

import discord
from discord.ext.commands import Bot

class EDI(Bot):
    """EDI skeleton

    Attributes:
        config (dict):
            A dictionary containing the bot configuration
    """
    def __init__(self, config: dict, **options):
        """EDI initializer

        Args:
            config (dict):
                A dictionary containing the bot configuration
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

    async def on_ready(self):
        """Coroutine called when the bot finished logging in"""
        logger = logging.getLogger('discord')
        self.logger.info(type(self.config))

if __name__ == '__main__':
    # Parse arguments
    parser = ArgumentParser(description='EDI discord bot')
    parser.add_argument('json_file', help='JSON configuration file')
    args = parser.parse_args()

    # Load JSON configuration
    if not os.path.isfile(args.json_file):
        sys.exit(f'JSON configuration file not found! Please try again.')

    with open(args.json_file) as file:
        config = json.load(file)

    # Start bot
    bot = EDI(
        config=config,
        intents=discord.Intents.default(),
    )
    bot.run(config['BOT_TOKEN'])
