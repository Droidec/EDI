# -*- coding: utf-8 -*-
"""
EDI basic commands and listeners
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
import random
import re

class CogBasic(commands.Cog, name='Basic'):
    """CogBasic handles all basic commands and listeners

    Attributes
        See commands.Cog
    """
    def __init__(self):
        """CogBasic init"""
        pass

    @commands.command(name='hello', aliases=['hey'])
    async def greet(self, ctx):
        """Coroutine called when a user greets the bot
        Say hello to user

        Parameters
            ctx (commands.Context) : Invocation context
        """
        await ctx.send(f"Hello `{ctx.author.name}`!")

    @commands.command(name='roll', aliases=['dice'])
    async def roll(self, ctx, *dices):
        """Coroutine called when a user wants to roll some dice
        Roll some dice with a pattern like:
        xdy or xDy where x is the number of rolls and y the number of sides

        Parameters
            ctx (commands.Context) : Invocation context
        """
        results = []
        try:
            for dice in dices:
                rolls = []
                nb_rolls, nb_sides = [int(num) for num in re.split(r'd|D', dice, 1)]
                if nb_rolls <= 0 or nb_sides <= 0:
                    raise ValueError

                for _ in range(nb_rolls):
                    rolls.append(random.randint(1, nb_sides))

                results.append(rolls)
        except ValueError:
            await ctx.send(f"`{dice}` has a bad format...")
            return

        await ctx.send('\n'.join([f"`{dice}`: {', '.join(map(str, rolls))}" for dice, rolls in zip(dices, results)]))
