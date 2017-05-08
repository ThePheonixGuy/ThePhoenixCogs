import discord
from discord.ext import commands
from .utils import checks
import asyncio
import logging
log = logging.getLogger('red.massmove')


class Massmove:
    """Allows you to mark specific people and move them to Admin-only channels, or Create admin-only channel"""

    def __init__(self, bot):
        self.bot = bot
        self.marked_members = []
        self.moveable = []

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(move_members=True, no_pm = False)
    async def mark(self, ctx, user: discord.Member):
        """Marks a user as a user to be moved. Note: Non-persistant, removed after each move is performed."""
        self.marked_members.append(user)
        await self.bot.say("Got it. Marked by the beast...")

    @commands.command(pass_context=True, aliases = ["marked"], no_pm = False)
    async def markedmembers(self,ctx):
        """Sends the author a message with all currently marked users."""
        author = ctx.message.author
        if len(self.marked_members) > 0:
            reply = ""
            for member in self.marked_members:
                reply += "{}, ".format(member.name)
            await self.bot.whisper("{} are all marekd to be moved with you. Clear them with {}clearmarked".format(reply, ctx.prefix))
        else:
            await self.bot.whisper("No marked members yet.")

    @commands.command(pass_context = True, no_pm = False)
    async def clearmarked(self,ctx):
        """Clears the current marked member list"""
        self.marked_members = []
        await self.bot.whisper("List cleared. No More marked members")

    @commands.command(pass_context = True)
    @checks.admin_or_permissions(move_members=True)
    async def movemarked(self,ctx, to_channel:discord.Channel):
        """Moves all marked members to the specified channel"""
        success = await self._markedmove(ctx, to_channel)

        if success:
            await self.bot.whisper("All marked members moved sucessfully.")
        else:
            await self.bot.whisper("There was an issue. Sorry. Remaining members in list are: {}".format(self.moveable))
    
    @commands.command(pass_context=True)
    async def createprivate(self,ctx, name):
        await self.bot.whipser("TBC")


    async def _markedmove(self, ctx, to_channel):
        """Internal function of marked move, so accessible for createprivate function."""
        author = ctx.message.author
        type_to = str(to_channel.type)
        if type_to == 'text':
            await self.bot.say('{} is not a valid voice channel'.format(to_channel.name))
            return False

        for user in self.marked_members:
                if user.voice_channel is not None:
                    self.moveable.append(user)
        print(self.moveable)

        try:
            for member in self.moveable:
                await self.bot.move_member(member, to_channel)
                print('Member {} moved to channel {}'.format(member.name, to_channel.name))
            self.moveable = []
            self.marked_members = []
            return True
        except:
            await self.bot.say("An Error occured in the process. Not all Members can be moved")
            return False



    async def _massmove(self, ctx, from_channel, to_channel):
        """Internal function: Massmove users to another voice channel"""
        # check if channels are voice channels. Or moving will be very... interesting...
        type_from = str(from_channel.type)
        type_to = str(to_channel.type)
        if type_from == 'text':
            await self.bot.say('{} is not a valid voice channel'.format(from_channel.name))
            log.debug('SID: {}, from_channel not a voice channel'.format(from_channel.server.id))
        elif type_to == 'text':
            await self.bot.say('{} is not a valid voice channel'.format(to_channel.name))
            log.debug('SID: {}, to_channel not a voice channel'.format(to_channel.server.id))
        else:
            try:
                log.debug('Starting move on SID: {}'.format(from_channel.server.id))
                log.debug('Getting copy of current list to move')
                voice_list = list(from_channel.voice_members)
                for member in voice_list:
                    await self.bot.move_member(member, to_channel)
                    print('Member {} moved to channel {}'.format(member.id, to_channel.id))
                    #await asyncio.sleep(0.05)
            except discord.Forbidden:
                await self.bot.say('I have no permission to move members.')
            except discord.HTTPException:
                await self.bot.say('A error occured. Please try again')


def setup(bot):
    n = Massmove(bot)
    bot.add_cog(n)
