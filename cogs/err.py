# -*- coding: utf-8 -*-
"""
EDI cog error handler
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

from .voice import VoiceChannelMissing, VoiceChannelNotFound, VoiceInvalidChannel, VoiceInvalidValue, VoiceConnectionError, VoiceNotConnected, VoiceNotPlaying
from .plex import PlexInvalidCommand, PlexInvalidPage, PlexInvalidSection, PlexNoMatchingResults, PlexAlbumNotFound
from discord.ext import commands
import traceback
import logging

class CogErrHandler(commands.Cog, name='Err'):
    """Handle cog errors

    Attributes
        See commands.Cog
    """
    def __init__(self, bot):
        """CogErrHandler init"""
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        """Coroutine called when an error is raised from a command

        Parameters
            ctx (commands.Context) : Invocation context
            err (commands.CommandError) : Error that was raised
        """
        if isinstance(err, commands.DisabledCommand):
            msg = f"This command is disabled {ctx.author.mention}"
        elif isinstance(err, commands.CommandNotFound):
            msg = f"I do not know this command {ctx.author.mention}"
        elif isinstance(err, commands.NoPrivateMessage):
            msg = f"This command can not be used in Private Messages {ctx.author.mention}"
        elif isinstance(err, commands.MissingPermissions):
            msg = f"You're not allowed to do that {ctx.author.mention}"
        elif isinstance(err, commands.MissingRequiredArgument):
            msg = f"The argument `{err.param.name}` is missing for this command {ctx.author.mention}: "
        elif isinstance(err, (VoiceChannelMissing, VoiceChannelNotFound, VoiceInvalidChannel, VoiceInvalidValue, VoiceConnectionError, VoiceNotConnected, VoiceNotPlaying)):
            msg = err
        elif isinstance(err, (PlexInvalidCommand, PlexInvalidPage, PlexInvalidSection, PlexNoMatchingResults, PlexAlbumNotFound)):
            msg = err
        else:
            msg = f"Congratulations, you've raised an exception {ctx.author.mention}"
            logging.error(f"=> `{ctx.message.content}` from `{ctx.author.display_name}` raised an exception:")
            logging.error(''.join(traceback.format_exception(type(err), err, err.__traceback__)))

        await ctx.send(msg)
