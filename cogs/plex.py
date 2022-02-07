# -*- coding: utf-8 -*-
"""
EDI PleX server commands and listeners
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

from discord.ext import commands
import discord

# Limit the number of results per search
NB_RESULTS_PER_PAGE = 30

# Possible sections
Sections = {
    'animes' : 'Animes Music',
    'audios' : 'Audio Series',
    'games' : 'Games Music',
    'movies' : 'Movies Music',
    'music' : 'Music',
    'shows' : 'TV Shows Music',
}

class CogPlexServer(commands.Cog, name='PleX Server'):
    """All PleX Server commands and listeners

    Attributes
        See commands.Cog
    """
    def __init__(self, bot):
        """CogVoice init"""
        self.bot = bot

    @commands.command(name='plex')
    async def plex(self, ctx, section: str, page: str=None):
        """Consult album names by section

        Parameters
            ctx (commands.Context) : Invocation context
            section (str) : Section to search for (Animes, Audios, Games, Movies, Music or Shows)
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
        embed.set_footer(text=f"Research requested by: {ctx.author.display_name}")
        await ctx.send(embed=embed)
