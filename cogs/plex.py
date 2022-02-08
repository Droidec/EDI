# -*- coding: utf-8 -*-
"""
EDI PleX Server commands and listeners
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

from datetime import datetime as dt
from discord.ext import commands
import discord
import plexapi
import os

# Limit the number of results per search
NB_RESULTS_PER_PAGE = 20

# Limit the number of tracks per embed field
NB_TRACKS_PER_EMBED_FIELD = 20

# Possible sections
Sections = {
    'animes' : 'Animes Music',
    'audios' : 'Audio Series',
    'games'  : 'Games Music',
    'movies' : 'Movies Music',
    'music'  : 'Music',
    'shows'  : 'TV Shows Music',
}

# Possible partitions
Partitions = {
    'animes' : 'U:',
    'audios' : 'V:',
    'games'  : 'W:',
    'movies' : 'X:',
    'music'  : 'Y:',
    'shows'  : 'Z:',
}

class CogPlexServer(commands.Cog, name='PleX Server'):
    """All PleX Server commands and listeners

    Attributes
        See commands.Cog
    """
    def __init__(self, bot):
        """CogPlexServer init"""
        self.bot = bot

    @commands.group(name='plex')
    async def plex(self, ctx):
        """Invoke PleX Server commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid plex command passed...")

    @plex.command(name='list')
    async def list(self, ctx, section: str, page: str=None):
        """Consult album names by section

        Parameters
            ctx (commands.Context) : Invocation context
            section (str) : Section to list (Animes, Audios, Games, Movies, Music or Shows)
            page (str) [Optional] : Page of results (Default is 1)
        """
        await ctx.trigger_typing()

        # Check consistency
        if page is None:
            page = '1'

        try:
            page = int(page)
        except ValueError:
            return await ctx.send("Invalid page number...")

        # Query PleX results
        try:
            s = self.bot.plex.library.section(Sections[section.lower()])
        except KeyError:
            return await ctx.send("Invalid section...")
        results = [album.title for album in s.search(libtype='album', sort='titleSort')]
        total = len(results)
        nb_pages = total // NB_RESULTS_PER_PAGE + int(total % NB_RESULTS_PER_PAGE != 0)

        if page > nb_pages:
            return await ctx.send(f"There is currently {nb_pages} pages at max...")

        start = NB_RESULTS_PER_PAGE * (page - 1)
        end = NB_RESULTS_PER_PAGE * page

        # Render result in a Discord embed
        embed = discord.Embed(title=f'Page {page} of {nb_pages} in {section} section', description='\n'.join(results[start:end]))
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f"List requested by: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @plex.command(name='search')
    async def search(self, ctx, section: str, keyword: str)
        """ Search album by keyword

        Parameters
            ctx (commands.Context) : Invocation context
            section (str) : Section to search in (Animes, Audios, Games, Movies, Music or Shows)
            keyword (str) : Keyword to search for
        """
        await ctx.trigger_typing()

        # Check consistency
        try:
            s = self.bot.plex.library.section(Sections[section.lower()])
        except KeyError:
            return await ctx.send("Invalid session...")

        # Search by keyword
        results = [album.title for album in s.search(title=keyword, libtype='album', limit=20)]

        # Render result in Discord embed
        embed = Discord.Embed(title='Results...', description='\n'.join(results))
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f"List requested by: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @plex.command(name='info')
    async def info(self, ctx, section: str, album: str):
        """Get album info

        Parameters
            ctx (commands.Context) : Invocation context
            section (str) : Section of the album (Animes, Audios, Games, Movies, Music or Shows)
            album (str) : Name of the album
        """
        await ctx.trigger_typing()
        thumb = None
        ite = 0

        # Check consistency
        try:
            s = self.bot.plex.library.section(Sections[section.lower()])
        except KeyError:
            return await ctx.send("Invalid session...")

        try:
            a = s.search(title=album, libtype='album', limit=1)[0]
        except plexapi.exceptions.NotFound:
            return await ctx.send("Could not find album...")

        tracks = a.tracks()
        nb_tracks = len(tracks)

        # Search thumbnail
        location = tracks[0].media[0].parts[0].file
        thumb_path = f"{Partitions[section.lower()]}/{os.path.dirname(location.split('/', 3)[3])}"
        try:
            cover = [name for name in os.listdir(thumb_path) if 'Cover' in name][0]
            thumb_path = f'{thumb_path}/{cover}'
        except IndexError:
            cover = None

        if cover is not None and os.path.isfile(thumb_path):
            thumb = discord.File(thumb_path)

        # Build Discord embed
        embed = discord.Embed(title=a.title, description=a.artist().title, color=discord.Color.blue())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        if thumb is not None:
            embed.set_thumbnail(url=f'attachment://{cover}')

        while (NB_TRACKS_PER_EMBED_FIELD * ite) < nb_tracks:
            start = NB_TRACKS_PER_EMBED_FIELD * ite
            end = NB_TRACKS_PER_EMBED_FIELD * (ite + 1)
            value = '\n'.join(f"{track.index}. {track.title} [{dt.fromtimestamp(track.duration/1000.0).strftime('%M:%S')}]" for track in tracks[start:end])
            embed.add_field(name=f'{start+1} - {min(nb_tracks, end)}', value=value, inline=False)
            ite += 1

        embed.set_footer(text=f"Info requested by: {ctx.author.display_name}")

        await ctx.send(file=thumb, embed=embed)
