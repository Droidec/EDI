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
import discord
import random
import re

class CogBasic(commands.Cog, name='Basic'):
    """All basic commands and listeners

    Attributes
        See commands.Cog
    """
    def __init__(self, bot):
        """CogBasic init"""
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Coroutine called when a member joins a guild

        Parameters
            member (discord.Member) : Member who joined
        """
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f"Welcome {member.mention}!")

    @commands.command(name='hello', aliases=['hey'])
    async def greet(self, ctx):
        """Mentions and greets user

        Parameters
            ctx (commands.Context) : Invocation context
        """
        await ctx.send(f"Hello {ctx.author.mention}!")

    @commands.command(name='roll', aliases=['dice'])
    async def roll(self, ctx, *expr):
        """Rolls some dice (1d6, 2d12, ...) and sum the result

        Parameters
            ctx (commands.Context) : Invocation context
            expr (tuple) : Roll expression
        """
        dices = []
        res = []

        # Check consistency
        if not expr:
            return await ctx.send("An expression is required to perform a roll...")

        # Split user tokens
        tokens = [x.strip() for x in ''.join(expr).split('+')]
        for token in tokens:
            dices.append([x.strip() for x in re.split(r'd|D', token, 1)])

        # Roll dices
        for index, dice in enumerate(dices):
            try:
                if len(dice) == 1:
                    roll = [int(dice[0])]
                    res.append(roll)
                elif len(dice) == 2:
                    rolls = []
                    nb_rolls = int(dice[0]) if dice[0] else 1
                    nb_sides = int(dice[1])
                    if nb_rolls <= 0 or nb_sides <= 0:
                        raise ValueError

                    for _ in range(nb_rolls):
                        rolls.append(random.randint(1, nb_sides))

                    res.append(rolls)
                else:
                    raise ValueError
            except ValueError:
                if tokens[index]:
                    return await ctx.send(f"`{tokens[index]}` dice has a bad format...")
                else:
                    return await ctx.send("Invalid expression...")

        # Send result
        algebra = '+'.join([f"({'+'.join(map(str, rolls))})" for rolls in res])
        total = sum([sum(rolls) for rolls in res])
        await ctx.send(f"{algebra}\n=`{total}`")
