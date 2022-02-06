# -*- coding: utf-8 -*-
"""
EDI voice commands and listeners
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

import discord
import logging
from discord.ext import commands

class CogVoice(commands.Cog, name='voice'):
    """All voice commands and listeners

    Attributes
        See commands.Cog
    """
    def __init__(self, bot):
        """CogVoice init"""
        self.bot = bot

    @commands.command(name='join')
    async def join(self, ctx, *channel):
        """Join a voice channel
        If a channel is specified, join that channel instead of user's channel

        Parameters
            ctx (commands.Context) : Invocation context
            channel (tuple) [optional] : Voice channel name to join
        """
        # Get channel...
        if channel:
            # ...by name
            name = ' '.join(channel) if len(channel) > 1 else channel[0]
            ch = discord.utils.get(ctx.guild.channels, name=name)
        else:
            # ...by user
            try:
                ch = ctx.author.voice.channel
            except AttributeError:
                return await ctx.send("No channel specified and user is not in a channel...")

        # Check consistency
        if ch is None:
            return await ctx.send("Voice channel specified does not exist...")

        if isinstance(ch, discord.TextChannel):
            return await ctx.send("Cannot connect to a text channel...")

        # Join voice channel
        if ctx.voice_client is not None:
            # Move bot if already in a voice channel
            return await ctx.voice_client.move_to(ch)

        await ch.connect()

    @commands.command(name='play')
    async def play(self, ctx, *, path: str):
        """Play audio from local filesystem

        Parameters
            ctx (commands.Context) : Invocation context
            path (str) : Path of the file to play
        """
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        if ctx.voice_client.is_playing():
            # Ignore while currently playing. TODO: make a queue
            return

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(path))
        ctx.voice_client.play(source, after=lambda e: logging.error(f"Player error: {e}") if e else None)

        await ctx.send(f"Now playing: `{path}`")

    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pause audio

        Parameters
            ctx (commands.Context) : Invocation context
        """
        vc = ctx.voice_client

        if not vc:
            return await ctx.send("Not currently in a voice channel...")
        elif not vc.is_playing():
            if not vc.is_paused():
                return await ctx.send("Not currently playing anything...")
            else:
                return await ctx.send("Already in pause...")
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send("Paused...")

    @commands.command(name='resume')
    async def resume(self, ctx):
        """Resume audio

        Parameters
            ctx (commands.Context) : Invocation context
        """
        vc = ctx.voice_client

        if not vc:
            return await ctx.send("Not currently in a voice channel...")
        elif not vc.is_paused():
            if not vc.is_playing():
                return await ctx.send("Not currently playing anything...")
            else:
                return await ctx.send("Currently playing...")

        vc.resume()
        await ctx.send("Resuming...")

    @commands.command(name='leave')
    async def leave(self, ctx):
        """Leave a voice channel

        Parameters
            ctx (commands.Context) : Invocation context
        """
        vc = ctx.voice_client

        if not vc:
            await ctx.send("Not currently in a voice channel...")

        return await vc.disconnect()
