# -*- coding: utf-8 -*-
"""
EDI Plex Server commands and listeners
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
from colorthief import ColorThief
from discord.ext import commands
import discord
import plexapi
import os

# Limits the number of results per page
NB_RESULTS_PER_PAGE = 20

# Limits the number of results per search
NB_RESULTS_PER_SEARCH = 20

# Limits the number of tracks per embed field
NB_TRACKS_PER_EMBED_FIELD = 20

# Possible sections to choose from
Sections = {
    'animes' : 'Animes Music',
    'audios' : 'Audio Series',
    'games'  : 'Games Music',
    'movies' : 'Movies Music',
    'music'  : 'Music',
    'shows'  : 'TV Shows Music',
}

# Possible partitions mounted
Partitions = {
    'animes' : 'U:',
    'audios' : 'V:',
    'games'  : 'W:',
    'movies' : 'X:',
    'music'  : 'Y:',
    'shows'  : 'Z:',
}

def format_duration(duration):
    """Format duration to %M:%S

    Parameters
        duration (int) : Duration of the track in ms

    Returns
        Formatted duration as a str
    """
    return dt.fromtimestamp(duration/1000.0).strftime('%M:%S')

def get_path(section, album):
    """Gets album path

    Parameters
        section (str) : Section of the album (must be valid)
        album (plexapi.audio.Album) : Album to search from

    Returns
        Path to the album as a str
    """
    location = album.tracks()[0].media[0].parts[0].file
    return Partitions[section.lower()] + '/' + os.path.dirname(location.split('/', 3)[3])

def get_thumbnail(path):
    """Gets album thumbnail path

    Parameters
        path (str) : Path to the album

    Returns
        Path to the album thumbnail as a str if found else None
    """
    try:
        # We search a file named 'cover' in the album directory
        return path + '/' + [name for name in os.listdir(path) if 'cover' in name.lower()][0]
    except IndexError:
        return None

class PlexSource(discord.PCMVolumeTransformer):
    """Represents a Plex audio source

    Attributes
        source (discord.FFmpegPCMAudio) : Audio source
        title (str) : Audio title
        duration (int) : Audio duration in ms
        requester (discord.User|discord.Member) : Requester
        thumb (str) : Path to the album thumbnail if exists
    """
    def __init__(self, source, *, title, duration, requester, thumb=None):
        """PlexSource init"""
        super().__init__(source)
        self.title = title
        self.duration = format_duration(duration)
        self.requester = requester
        self.thumb = thumb

    @classmethod
    async def create_source(cls, ctx, section: str, path: str, thumb: str, track):
        """Creates a Plex audio source

        Parameters
            ctx (commands.Context) : Invocation context
            section (str) : Section of the album
            path (str) : Path to the album
            thumb (str) : Path to the album thumbnail
            track (plexapi.audio.track) : Audio track
        """
        return cls(discord.FFmpegPCMAudio(path), title=track.title, duration=track.duration, requester=ctx.author.display_name, thumb=thumb)

class PlexInvalidSection(commands.CommandError):
    """Custom Exception class for Plex invalid section"""

class PlexInvalidPage(commands.CommandError):
    """Custom Exception class for Plex invalid page"""

class PlexNoMatchingResults(commands.CommandError):
    """Custom Exception class for Plex no matching results"""

class PlexAlbumNotFound(commands.CommandError):
    """Custom Exception class for Plex album not found"""

class CogPlexServer(commands.Cog, name='Plex Server'):
    """All Plex Server commands and listeners

    Attributes
        See commands.Cog
    """
    def __init__(self, bot):
        """CogPlexServer init"""
        self.bot = bot

    def get_page(self, ctx, page):
        """Gets page number from user input

        Parameters
            ctx (commands.Context) : Invocation context
            page (str) : Page to cast

        Returns
            Page as an int

        Raises
            PlexInvalidPage if page is not valid
        """
        try:
            page = int(page)
        except ValueError:
            raise PlexInvalidPage(f"The page number `{page}` is invalid {ctx.author.mention}")

        if page <= 0:
            raise PlexInvalidPage(f"The page number can only be strictly positive {ctx.author.mention}")

    def get_section(self, ctx, section):
        """Gets section from user input

        Parameters
            ctx (commands.Context) : Invocation context
            section (str) : Section to search for

        Returns
            A valid plexapi.library.LibrarySection object

        Raises
            PlexInvalidSection if section is not valid
        """
        try:
            return self.bot.plex.library.section(Sections[section.lower()])
        except KeyError:
            raise PlexInvalidSection(f"The section `{section}` is invalid {ctx.author.mention}\n"
                                     f"Please specify one of the following sections: {', '.join(s.title() for s in Sections.keys())}")

    def get_album(self, ctx, section, album):
        """Gets album from user input

        Parameters
            ctx (commands.Context) : Invocation context
            section (plexapi.library.LibrarySection) : Section of the album to search from
            album (str) : Name of the album to search for

        Returns
            A valid plexapi.audio.Album object

        Raises
            PlexAlbumNotFound if album is not found
        """
        try:
            # We remove commas in album title as it provokes search errors...
            return section.search(title=album.replace(',', ''), libtype='album', limit=1)[0]
        except (plexapi.exceptions.NotFound, IndexError):
            raise PlexAlbumNotFound(f"The album `{album}` did not match any results {ctx.author.mention}")

    @commands.group(name='plex')
    async def plex(self, ctx):
        """Invokes Plex Server commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid plex command passed...")

    @plex.command(name='list')
    async def list(self, ctx, section: str, page: str=None):
        """Lists album names by section

        Parameters
            ctx (commands.Context) : Invocation context
            section (str) : Section to list (Animes, Audios, Games, Movies, Music or Shows)
            page (str) [Optional] : Page of results (Default is 1)
        """
        await ctx.trigger_typing()

        # Check consistency
        s = self.get_section(ctx, section)
        s_name = Sections[section.lower()].title()

        if page is None:
            page = 1
        else:
            page = self.get_page(ctx, page)

        # Query Plex server for all albums in this section
        results = [album.title for album in s.search(libtype='album', sort='titleSort')]
        total = len(results)
        nb_pages = total // NB_RESULTS_PER_PAGE + int(total % NB_RESULTS_PER_PAGE != 0)

        if page > nb_pages:
            raise PlexInvalidPage(f"There are a maximum of {nb_pages} pages for the `{s_name}` section {ctx.author.mention}")

        start = NB_RESULTS_PER_PAGE * (page - 1)
        end = NB_RESULTS_PER_PAGE * page

        # Render result in a Discord embed
        embed = discord.Embed(title=f'Page {page} of {nb_pages} in {s_name} section', description='\n'.join(results[start:end]))
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f"List requested by: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @plex.command(name='search')
    async def search(self, ctx, section: str, keyword: str):
        """Searches album by keyword

        Parameters
            ctx (commands.Context) : Invocation context
            section (str) : Section to search in (Animes, Audios, Games, Movies, Music or Shows)
            keyword (str) : Keyword to search for
        """
        await ctx.trigger_typing()

        # Check consistency
        s = self.get_section(ctx, section)

        # Query Plex server for all albums that match keyword
        results = [album.title for album in s.search(title=keyword, libtype='album', limit=NB_RESULTS_PER_SEARCH)]
        if not results:
            raise PlexNoMatchingResults(f"Your search did not match any results {ctx.author.mention}")

        # Render result in Discord embed
        fmt = '\n'.join(f"- {result}" for result in results) if len(results) > 1 else results[0]
        embed = discord.Embed(title=f'Most relevant results', description=fmt)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f"Search requested by: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @plex.command(name='info')
    async def info(self, ctx, section: str, album: str):
        """Consults album info

        Parameters
            ctx (commands.Context) : Invocation context
            section (str) : Section of the album (Animes, Audios, Games, Movies, Music or Shows)
            album (str) : Name of the album
        """
        await ctx.trigger_typing()
        attachment = None
        ite = 0

        # Check consistency
        s = self.get_section(ctx, section)
        a = self.get_album(ctx, s, album)

        # Get album info
        tracks = a.tracks()
        nb_tracks = len(tracks)
        path = get_path(section, a)
        thumb = get_thumbnail(path)
        if thumb is not None and os.path.isfile(thumb):
            attachment = discord.File(thumb)
            color = ColorThief(thumb).get_color(quality=7)

        # Render result in Discord embed
        if attachment is not None:
            embed = discord.Embed(title=a.title, description=a.artist().title, color=discord.Color.from_rgb(*color))
            embed.set_thumbnail(url=f'attachment://{os.path.basename(thumb)}')
        else:
            embed = discord.Embed(title=a.title, description=a.artist().title)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f"Info requested by: {ctx.author.display_name}")

        while (NB_TRACKS_PER_EMBED_FIELD * ite) < nb_tracks:
            start = NB_TRACKS_PER_EMBED_FIELD * ite
            end = NB_TRACKS_PER_EMBED_FIELD * (ite + 1)
            fmt = '\n'.join(f"{start+index+1}. {track.title} [{format_duration(track.duration)}]" for index, track in enumerate(tracks[start:end]))
            embed.add_field(name=f'{start+1} - {min(nb_tracks, end)}', value=fmt, inline=False)
            ite += 1

        await ctx.send(file=attachment, embed=embed)

    @plex.command(name='play')
    async def play(self, ctx, section: str, album: str):
        """Add album to the player queue

        Parameters
            ctx (commands.Context) : Invocation context
            section (str) : Section of the album (Animes, Audios, Games, Movies, Music or Shows)
            album (str) : Name of the album
        """
        await ctx.trigger_typing()

        # Check consistency
        s = get_section(ctx, section)
        a = get_album(ctx, s, album)

        # Get voice & player
        v = self.bot.get_cog('Voice')

        if not ctx.voice_client:
            await ctx.invoke(v.join)

        player = v.get_player(ctx)

        # Get album info
        tracks = a.tracks()
        nb_tracks = len(tracks)
        path = get_path(section, a)
        thumb = get_thumbnail(path)

        # Add tracks to music player queue
        for track in a.tracks():
            source = await PlexSource.create_source(ctx, section, path, thumb, track)
            await player.queue.put(source)

        embed = discord.Embed(title="Player info", description=f"Queued `{a.title}` ({nb_tracks} tracks)", color=discord.Color.blue())
        embed.set_footer(text=f"Play requested by: {ctx.author.display_name}")
        await ctx.send(embed=embed)
