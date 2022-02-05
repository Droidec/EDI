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
        if isinstance(err, commands.CommandNotFound):
            await ctx.send("Sorry, I do not know this command...")
        elif isinstance(err, commands.MissingRequiredArgument):
            await ctx.send("Sorry, an argument is missing for this command...")
        else:
            await ctx.send("Sorry, this command raised an exception...")
            logging.error(f"Exception raised in command '{ctx.command}'")
            logging.error(''.join(traceback.format_exception(type(err), err, err.__traceback__)))
