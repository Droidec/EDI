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

from async_timeout import timeout
from discord.ext import commands
from .plex import PlexSource
import discord
import asyncio
import os

class MusicPlayer:
    """A music player which implements a queue and a loop for each guild.
    When the bot is disconnected from voice channel, the player is destroyed

    Attributes
        ctx (commands.Context) : Invocation context
    """
    def __init__(self, ctx):
        """MusicPlayer init"""
        self.bot = ctx.bot
        self.cog = ctx.cog
        self.guild = ctx.guild
        self.channel = ctx.channel

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None # Now playing message
        self.current = None # Current song played

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Main player loop"""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            # Wait for the next song
            # If we timeout, cancel the player and disconnect...
            try:
                async with timeout(60): # 1 min...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self.guild)

            # Check consistency
            if not isinstance(source, PlexSource):
                await self.channel.send("There was an error processing your song...")
                continue

            # Play song
            self.current = source
            self.guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            embed = discord.Embed(title="Now playing", description="TODO", color=discord.Color.green())
            self.np = await channel.send(embed=embed)
            await self.next.wait()

            # Prepare for next song
            source.cleanup()
            self.current = None

    async def destroy(self, guild):
        """Disconnect and cleanup the player

        Parameters
            guild (discord.Guild) : Guild of the player to destroy
        """
        return self.bot.loop.create_task(self.cog._cleanup(guild))

class VoiceContextError(commands.CommandError):
    """Custom Exception class for voice context error"""

class CogVoice(commands.Cog, name='Voice'):
    """All voice commands and listeners

    Attributes
        See commands.Cog
    """
    def __init__(self, bot):
        """CogVoice init"""
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        """Disconnect and cleanup the player of a guild

        Parameters
            guild (discord.Guild) : Guild of the player to destroy
        """
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, ctx):
        """Retrieve the guild player, or create one

        Parameters
            ctx (commands.Context) : Invocation context
        """
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

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

    @commands.command(name='np')
    async def now_playing(self, ctx):
        """Show the current song played

        Parameters
            ctx (commands.Context) : Invocation context
        """
        vc = ctx.voice_client
        await ctx.send(f"[{vc.source.data.title}]({vc.source.requester.mention})")

    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pause audio

        Parameters
            ctx (commands.Context) : Invocation context
        """
        ctx.voice_client.pause()
        await ctx.send("Player paused...")

    @commands.command(name='resume')
    async def resume(self, ctx):
        """Resume audio

        Parameters
            ctx (commands.Context) : Invocation context
        """
        ctx.voice_client.resume()
        await ctx.send("Player resumed...")

    @commands.command(name='stop')
    async def stop(self, ctx):
        """Stop audio

        Parameters
           ctx (commands.Context) : Invocation context
        """
        ctx.voice_client.stop()
        await ctx.send("Player stopped...")

    @commands.command(name='leave')
    async def leave(self, ctx):
        """Leave a voice channel

        Parameters
            ctx (commands.Context) : Invocation context
        """
        return await self._cleanup(ctx.guild)

    @leave.before_invoke
    async def ensure_voice(self, ctx):
        """Ensure that EDI is in a voice channel

        Parameters
            ctx (commands.Context) : Invocation context
        """
        if ctx.voice_client is None:
            await ctx.send("Not currently in a voice channel...")
            raise VoiceContextError("Not currently in a voice channel...")

    @now_playing.before_invoke
    @pause.before_invoke
    @resume.before_invoke
    @stop.before_invoke
    async def ensure_play(self, ctx):
        """Ensure that EDI is in a voice channel and player is active

        Parameters
            ctx (commands.Context) : Invocation context
        """
        if ctx.voice_client is None:
            await ctx.send("Not currently in a voice channel...")
            raise VoiceContextError("Not currently in a voice channel...")
        elif not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            await ctx.send("Not currently playing anything...")
            raise VoiceContextError("Not currently playing anything...")
