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
import itertools
import discord
import asyncio
import os

class VoicePlayer:
    """A voice player which implements a queue and a loop for each guild.
    When the bot is disconnected from voice channel, the player is destroyed

    Attributes
        ctx (commands.Context) : Invocation context
    """
    def __init__(self, ctx):
        """VoicePlayer init"""
        self.bot = ctx.bot
        self.cog = ctx.cog
        self.guild = ctx.guild
        self.channel = ctx.channel

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None # Current now playing embed
        self.current = None # Current track played
        self.attachment = None # Current thumb file

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Main player loop"""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            # Wait for the next track
            # If we timeout, cancel the player and disconnect...
            try:
                async with timeout(60): # 1 min...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self.guild)

            # Check consistency
            if not isinstance(source, PlexSource):
                await self.channel.send("Unmanaged track detected. Skipping...")
                continue

            # Play track
            self.current = source
            self.guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))

            # Set now playing embed
            fmt = f"{source.title} [{source.duration}]\n*{source.album}*"
            self.np = discord.Embed(title="Now playing", description=fmt, color=discord.Color.blue())
            self.np.set_footer(text=f"Requested by: {source.requester}")
            if source.thumb is not None and os.path.isfile(source.thumb):
                self.attachment = discord.File(source.thumb)
                self.np.set_thumbnail(url=f'attachment://{os.path.basename(source.thumb)}')

            await self.channel.send(file=self.attachment, embed=self.np)
            await self.next.wait()

            # Prepare for next track
            source.cleanup()
            self.np = None
            self.current = None
            self.attachment = None

    async def destroy(self, guild):
        """Disconnects and cleanup the player

        Parameters
            guild (discord.Guild) : Guild of the player to destroy
        """
        return self.bot.loop.create_task(self.cog.cleanup(guild))

class VoiceChannelMissing(commands.CommandError):
    """Custom Exception class for voice channel missing"""

class VoiceChannelNotFound(commands.CommandError):
    """Custom Exception class for voice channel not found"""

class VoiceChannelInvalid(commands.CommandError):
    """Custom Exception class for voice channel invalid"""

class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for voice connection error"""

class VoiceNotConnected(commands.CommandError):
    """Custom Exception class for voice not connected"""

class VoiceNotPlaying(commands.CommandError):
    """Custom Exception class for voice not playing"""

class CogVoice(commands.Cog, name='Voice'):
    """All voice commands and listeners

    Attributes
        See commands.Cog
    """
    def __init__(self, bot):
        """CogVoice init"""
        self.bot = bot
        self.players = {}

    def get_player(self, ctx):
        """Retrieves the guild player, or create one

        Parameters
            ctx (commands.Context) : Invocation context
        """
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = VoicePlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    async def cleanup(self, guild):
        """Disconnects and cleanup the player of a guild

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

    @commands.command(name='join')
    async def join(self, ctx, *channel):
        """Joins a voice channel
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
                raise VoiceChannelMissing(f"No channel to join. Please either specify a valid channel or join one first {ctx.author.mention}")

        # Check consistency
        if ch is None:
            raise VoiceChannelNotFound(f"Channel not found on this server {ctx.author.mention}")

        if isinstance(ch, discord.channel.TextChannel):
            raise VoiceChannelInvalid(f"I can not connect to a text channel {ctx.author.mention}")

        # Join voice channel
        if ctx.voice_client is not None:
            # Move bot if already in a voice channel
            try:
                await ctx.voice_client.move_to(ch)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f"Moving to channel {ch} timed out...")
        else:
            # Connect bot to a voice channel
            try:
                await ch.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f"Connecting to channel {ch} timed out...")

    @commands.command(name='np')
    async def now_playing(self, ctx):
        """Shows the current track played

        Parameters
            ctx (commands.Context) : Invocation context
        """
        player = self.get_player(ctx)
        await ctx.send(file=player.attachment, embed=player.np)

    @commands.command(name='queue')
    async def queue_info(self, ctx):
        """Shows the player queue

        Parameters
            ctx (commands.Context) : Invocation context
        """
        player = self.get_player(ctx)

        if player.queue.empty():
            fmt = "*There is nothing in the queue...*"
        else:
            nb_tracks = player.queue.qsize()
            tracks = list(itertools.islice(player.queue._queue, 0, nb_tracks))
            fmt = '\n'.join(f"{index + 1}. {track.title} [{track.duration}]" for index, track in enumerate(tracks))

        embed = discord.Embed(title="Player queue", description=fmt, color=discord.Color.blue())
        embed.set_footer(text=f"Queue requested by: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pauses audio

        Parameters
            ctx (commands.Context) : Invocation context
        """
        if ctx.voice_client.is_paused():
            return

        ctx.voice_client.pause()
        embed = discord.Embed(title="Player info", description="Player has been paused", color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command(name='resume')
    async def resume(self, ctx):
        """Resumes audio

        Parameters
            ctx (commands.Context) : Invocation context
        """
        if ctx.voice_client.is_playing():
            return

        ctx.voice_client.resume()
        embed = discord.Embed(title="Player info", description="Player has been resumed", color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command(name='skip')
    async def skip(self, ctx):
        """Skips to next track in the queue

        Parameters
           ctx (commands.Context) : Invocation context
        """
        ctx.voice_client.stop()

    @commands.command(name='stop')
    async def stop(self, ctx):
        """Clears the queue and stops audio

        Parameters
            ctx (commands.Context) : Invocation context
        """
        player = self.get_player(ctx)

        # Clear the queue
        for _ in range(player.queue.qsize()):
            player.queue.get_nowait()
            player.queue.task_done()

        # Stop current track
        ctx.voice_client.stop()
        embed = discord.Embed(title="Player info", description="Queue has been cleared and player has been stopped", color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command(name='leave')
    async def leave(self, ctx):
        """Leaves voice channel

        Parameters
            ctx (commands.Context) : Invocation context
        """
        await self.cleanup(ctx.guild)

    @queue_info.before_invoke
    @leave.before_invoke
    async def ensure_voice(self, ctx):
        """Ensures that EDI is in a voice channel

        Parameters
            ctx (commands.Context) : Invocation context
        """
        if ctx.voice_client is None:
            raise VoiceNotConnected(f"I'm not currently in a voice channel {ctx.author.mention}")

    @now_playing.before_invoke
    @pause.before_invoke
    @resume.before_invoke
    @skip.before_invoke
    @stop.before_invoke
    async def ensure_play(self, ctx):
        """Ensures that EDI is in a voice channel and player is active

        Parameters
            ctx (commands.Context) : Invocation context
        """
        vc = ctx.voice_client
        if vc is None:
            raise VoiceNotConnected(f"I'm not currently in a voice channel {ctx.author.mention}")
        elif not vc.is_playing() and not vc.is_paused():
            raise VoiceNotPlaying(f"I'm currently not playing anything {ctx.author.mention}")
