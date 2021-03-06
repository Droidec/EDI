# -*- coding: utf-8 -*-
"""
EDI Discord bot
"""
#
# Copyright (c) 2022, Marc GIANNETTI <mgtti.pro@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  - Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from argparse import ArgumentParser, RawTextHelpFormatter
from plexapi.server import PlexServer
from discord.ext import commands
import discord
import logging
import cogs

class EDI(commands.Bot):
    """EDI skeleton

    Attributes
        See commands.Bot
    """
    def __init__(self, *args, **kwargs):
        """Bot init"""
        super().__init__(*args, **kwargs)
        self.plex = None

    def init_plex(self, base_url, token):
        """Initialize Plex context

        Parameters
            base_url (str) : Base URL of the Plex server to connect to
            token (str) : Plex account token
        """
        self.plex = PlexServer(base_url, token)

    async def on_ready(self):
        """Coroutine called when the Bot is UP"""
        logging.info(f"Bot is UP: {self.user.name}:{self.user.id}")

if __name__ == "__main__":
    # Set logging
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] (%(levelname)s) %(message)s")

    # Parse arguments
    parser = ArgumentParser(description="EDI discord bot", formatter_class=RawTextHelpFormatter)
    parser.add_argument('plex_base_url', help="Base URL of the Plex server to connect to")
    parser.add_argument('plex_token', help="Plex account token")
    parser.add_argument('discord_token', help="Discord bot token")
    args = parser.parse_args()

    # Start bot
    bot = EDI(command_prefix='!', activity=discord.Game(name='!help'))
    bot.init_plex(args.plex_base_url, args.plex_token)
    bot.add_cog(cogs.CogErrHandler(bot))
    bot.add_cog(cogs.CogBasic(bot))
    bot.add_cog(cogs.CogVoice(bot))
    bot.add_cog(cogs.CogPlexServer(bot))
    bot.run(args.discord_token)
