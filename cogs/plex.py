"""
plex.py

Plex EDI commands.
"""

import io
from datetime import datetime
from typing import Union

import discord
import plexapi
import requests
from discord import Option, OptionChoice
from discord.ext import commands
from plexapi.server import PlexServer

# Plex server instance
plex = None

# Available sections and their properties
# TODO: get sections dynamically from Plex server
available_section = {
    'Animes': 'show',
    'Animes Movies': 'movie',
    'Animes Music': 'album',
    'Audio Series': 'album',
    'Games Music': 'album',
    'Movies': 'movie',
    'Movies Music': 'album',
    'Music': 'album',
    'TV Shows': 'show',
    'TV Shows Music': 'album'
}

# Maximum size of a Discord embed title
DISCORD_EMBED_TITLE_MAX_LEN = 256

# Maximum size of a Discord embed description
DISCORD_EMBED_DESCRIPTION_MAX_LEN = 4096

# Maximum size of a Discord embed field value
DISCORD_EMBED_FIELD_VALUE_MAX_LEN = 1024

# Limits the size of an album description
ALBUM_DESCRIPTION_MAX_LEN = 300

# Number of milliseconds in an hour
NB_MILLISECONDS_PER_HOUR = 3600000

async def get_plex_medias(ctx: discord.AutocompleteContext):
    """Gets medias for keyword autocompletion

    Args:
        ctx (discord.AutocompleteContext):
            The context of the autocompletion.

    Returns:
        A list of medias corresponding to the user keyword.
    """
    section_name = ctx.options['section']
    section = plex.library.section(title=section_name)
    return [OptionChoice(media.title, media.key) for media in section.search(libtype=available_section[section_name], title=ctx.value, sort='titleSort')]

class PlexNoMatchingResults(commands.CommandError):
    """Plex no matching results"""

class PlexUnknownMediaType(commands.CommandError):
    """Plex unknown media type"""

class Plex(commands.Cog):
    """EDI plex commands.

    Attributes:
        bot (commands.Bot):
            EDI bot instance.
        plex_group (discord.SlashCommandGroup):
            Group command /plex.
    """
    plex_group = discord.SlashCommandGroup('plex')

    def __init__(self, bot: commands.Bot):
        """Plex cog initializer.

        Args:
            bot (commands.Bot):
                EDI bot instance.
        """
        self.bot = bot

    def truncate_field(self, text: str, size: int):
        """Truncates a text to size bytes.

        TODO: Move this function in EDI skeleton?

        Args:
            text (str):
                The text to truncate.
            size (int):
                The maximum size.

        Returns:
            The text truncated.
        """
        return (text[:size - 3] + '...') if len(text) > size else text

    def download_image(self, url: str, name: str):
        """Downloads the image of a media.

        TODO: async requests?

        Args:
            url (str):
                The URL to the image on the Plex server.
            name (str):
                The name of the file image to send to Discord.

        Returns:
            A tuple containing the url attachment and the Discord file.
        """
        thumbnail = io.BytesIO(requests.get(plex.url(url, includeToken=True)).content)
        return (f'attachment://{name}.png', discord.File(fp=thumbnail, filename=f'{name}.png'))

    def format_duration(self, duration: int):
        """Formats a duration expressed in milliseconds.

        Args:
            duration (int):
                The duration to format.

        Returns:
            A string representing the duration.
        """
        if duration >= NB_MILLISECONDS_PER_HOUR:
            return datetime.fromtimestamp(duration / 1000.0).strftime('%H h %M min %S sec')

        return datetime.fromtimestamp(duration / 1000.0).strftime('%M min %S s')

    def format_track_duration(self, duration: int):
        """Formats a track duration expressed in milliseconds.

        Args:
            duration (int):
                The track duration to format.

        Returns:
            A string representing the track duration.
        """
        if duration >= NB_MILLISECONDS_PER_HOUR:
            return datetime.fromtimestamp(duration / 1000.0).strftime('%H:%M:%S')

        return datetime.fromtimestamp(duration / 1000.0).strftime('%M:%S')

    async def render_paginator(
        self,
        ctx: discord.ApplicationContext,
        section: plexapi.library.LibrarySection,
        medias: list,
        total: int
    ) -> None:
        """Renders a paginator containing a list of medias.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
            section (plexapi.library.LibrarySection):
                The medias section.
            medias (list):
                The list of medias to render.
        """
        #TODO
        await ctx.respond('I should render a paginator here')

    async def render_media_album(
        self,
        ctx: discord.ApplicationContext,
        album: plexapi.audio.Album
    ) -> None:
        """Renders an album in an embed.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
            album (plexapi.audio.Album):
                The album to render.
        """
        files = []
        title = self.truncate_field(album.title, DISCORD_EMBED_TITLE_MAX_LEN)
        description = self.truncate_field(album.summary, ALBUM_DESCRIPTION_MAX_LEN)
        artist = album.artist()
        tracks = album.tracks()
        nb_tracks = len(tracks)
        duration = sum(track.duration for track in tracks)

        if album.thumb is not None:
            (thumb_url, thumb_file) = self.download_image(album.thumb, 'thumb')
            files.append(thumb_file)

        if album.art is not None:
            (artist_url, artist_file) = self.download_image(album.art, 'art')
            files.append(artist_file)

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blurple()
        )

        if album.thumb is not None:
            embed.set_thumbnail(url=thumb_url)

        playlist = '\n'.join(f'{index+1}. {track.title} [{self.format_track_duration(track.duration)}]' for index, track in enumerate(tracks))
        playlist = self.truncate_field(playlist, DISCORD_EMBED_FIELD_VALUE_MAX_LEN)
        embed.add_field(name='Playlist', value=playlist)

        if album.art is not None:
            embed.set_footer(text=f'{artist.title} • {album.year} • {nb_tracks} track(s), {self.format_duration(duration)}', icon_url=artist_url)
        else:
            embed.set_footer(text=f'{artist.title} • {album.year} • {nb_tracks} track(s), {self.format_duration(duration)}')

        await ctx.respond(files=files, embed=embed)

    async def render_media_movie(
        self,
        ctx: discord.ApplicationContext,
        movie: plexapi.video.Movie
    ) -> None:
        """Renders a movie in an embed

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
            movie (plexapi.audio.Movie):
                The movie to render.
        """
        files = []
        title = self.truncate_field(movie.title, DISCORD_EMBED_TITLE_MAX_LEN)
        description = self.truncate_field(movie.summary, DISCORD_EMBED_DESCRIPTION_MAX_LEN)
        director = movie.directors[0]

        if movie.thumb is not None:
            (thumb_url, thumb_file) = self.download_image(movie.thumb, 'thumb')
            files.append(thumb_file)

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blurple()
        )

        if movie.thumb is not None:
            embed.set_thumbnail(url=thumb_url)

        embed.set_footer(text=f'{director} • {movie.year} • {self.format_duration(movie.duration)}')

        await ctx.respond(files=files, embed=embed)

    async def render_media_show(
        self,
        ctx: discord.ApplicationContext,
        show: plexapi.video.Show
    ) -> None:
        """Renders a show in an embed

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
            show (plexapi.audio.Show):
                The show to render.
        """
        files = []
        title = self.truncate_field(show.title, DISCORD_EMBED_TITLE_MAX_LEN)
        description = self.truncate_field(show.summary, DISCORD_EMBED_DESCRIPTION_MAX_LEN)

        if show.thumb is not None:
            (thumb_url, thumb_file) = self.download_image(show.thumb, 'thumb')
            files.append(thumb_file)

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blurple()
        )

        if show.thumb is not None:
            embed.set_thumbnail(url=thumb_url)

        embed.set_footer(text=f'{show.studio} • {show.year} • {show.seasonCount} seasons')

        await ctx.respond(files=files, embed=embed)

    async def render_media(
        self,
        ctx: discord.ApplicationContext,
        media: Union[plexapi.audio.Album, plexapi.video.Movie, plexapi.video.Show]
    ) -> None:
        """Renders a media in an embed.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
            media (plexapi.audio.Album or plexapi.video.Movie or plexapi.video.Show):
                The media to render.
        """
        match type(media):
            case plexapi.audio.Album:
                await self.render_media_album(ctx, media)
            case plexapi.video.Movie:
                await self.render_media_movie(ctx, media)
            case plexapi.video.Show:
                await self.render_media_show(ctx, media)
            case _:
                raise PlexUnknownMediaType(f'`{type(media)}` is not handled for rendering')

    @plex_group.command(name='search', description='Search medias by section.')
    async def search(
        self,
        ctx: discord.ApplicationContext,
        section_name: Option(
            discord.SlashCommandOptionType.string,
            name='section',
            description='The section to look for',
            choices=available_section.keys(),
        ),
        keyword: Option(
            discord.SlashCommandOptionType.string,
            name='keyword',
            description='Search by keyword',
            autocomplete=get_plex_medias,
            default=''
        )
    ) -> None:
        """Sends a paginator with all the requested medias of a section.

        Args:
            ctx (discord.ApplicationContext):
                The context of the command.
            section_name (str):
                The section to look for.
            keyword (str):
                The media key or the user input.
        """
        # The command can take more than 3 seconds to compute
        await ctx.defer()

        section = plex.library.section(title=section_name)

        if keyword.startswith('/library/metadata/'):
            # keyword is a media key
            try:
                medias = [plex.fetchItem(keyword)]
            except Exception:
                raise PlexNoMatchingResults(f'No matching results for `{section_name}` and `{keyword}`')
        else:
            medias = section.search(libtype=available_section[section_name], title=keyword, sort='titleSort')

        total = len(medias)

        match total:
            case 0:
                raise PlexNoMatchingResults(f'No matching results for `{section_name}` and `{keyword}`')
            case 1:
                await self.render_media(ctx, medias[0])
            case _:
                await self.render_paginator(ctx, section, medias, total)

    async def cog_command_error(self, ctx: discord.ApplicationContext, err: discord.ApplicationCommandError) -> None:
        """Coroutine called when an exception is raised in the cog.

        If it is a specific error managed by this cog, a response is sent to
        the author to explain why an error occured. In any case, the generic
        error handler of EDI will be called after that to print the traceback.

        TODO: mention and ephemeral not working properly?

        Args:
            ctx (discord.ApplicationContext):
                The context of the command that raised the exception.
            err (discord.ApplicationCommandError):
                The error that was raised.
        """
        if isinstance(err, PlexNoMatchingResults):
            await ctx.respond(f'{ctx.author.mention} Your search did not match any results.', ephemeral=True)
        elif isinstance(err, PlexUnknownMediaType):
            await ctx.respond(f'{ctx.author.mention} An internal error occurred.', ephemeral=True)

def setup(bot) -> None:
    """Setup Plex commands"""
    global plex

    plex = PlexServer(bot.config['PLEX_BASEURL'], bot.config['PLEX_TOKEN'])
    bot.add_cog(Plex(bot))
