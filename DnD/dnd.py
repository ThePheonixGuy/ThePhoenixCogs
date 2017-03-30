import discord
import asyncio
import os
from discord.ext import commands
from .utils import checks
from .utils.dataIO import dataIO
from copy import deepcopy
from datetime import datetime
from __main__ import send_cmd_help
from tabulate import tabulate
from random import randint

class RosterError(Exception):
    pass

class PlayerAlreadyRegistered(RosterError):
    pass


class NoAccount(RosterError):
    pass

class DiceRolls:

    def __init__(self, bot):
        self.bot=bot

    def roll4(self):
        outcome = randint(1,4)
        return outcome

    def roll6(self):
        outcome = randint(1,6)
        return outcome

    def roll8(self):
        outcome = randint(1,8)
        return outcome

    def roll10(self):
        outcome = randint(1,10)
        return outcome

    def roll12(self):
        outcome = randint(1,12)
        return outcome

    def roll20(self):
        outcome = randint(1,20)
        return outcome

    def roll100(self):
        outcome = randint(1,100)
        return outcome

class DnD:
    """D&D Cog by ThePheonixGuy"""

    def __init__(self, bot):
        self.bot = bot
        self.player_path  = "data/Dungeon_Records/players.json"
        self.players = dataIO.load_json(self.player_path)
        self.diceRolls = DiceRolls(bot)

    @commands.group(pass_context=True)
    async def dndset(self,ctx):
        """A Dungeons and Dragons cog that facilitates and records D&D games"""
        if ctx.invoked_subcommand is None:
                await send_cmd_help(ctx)


    @dndset.command(pass_context=True)
    async def setmaster(self, ctx, user):
    	"""Sets the Dungeon Master."""

    
    @commands.group(pass_context=True)
    async def dnd(self,ctx):
        """Options for your DnD profile"""
        if ctx.invoked_subcommand is None:
                await send_cmd_help(ctx)


    @dnd.command(pass_context=True)
    async def register(self,ctx, charName):
        """Registers you in the DnD Player Log. Use inverted commas for separated names.
        You will be alerted the next time a Master starts a game"""
        user = ctx.message.author
        try:
            newPlayer = self.createPlayer(user, charName)
            await self.bot.say("New Player profile created for {}.".format(user.mention))
        except PlayerAlreadyRegistered:
            await self.bot.say("{}Are you kidding? You already have a profile... Greedy, wanting more than one.".format(user.mention))

    @dnd.command(pass_context=True)
    async def gameinfo(self):
        """Returns information on the current/last DnD Game."""
        await self.bot.say("Info yo. Enjoy.")

    @dnd.command(pass_context=True)
    async def gameprofile(self, ctx):
        """Sends the user a DM of their current profile info"""
        author = ctx.message.author
        userProfile = self.getPlayer(author)
        header = "```{}```".format("{}'s DnD PROFILE".format(author.name))
        
        table = [["Name: ",userProfile["Name"]],["Character Name: ", userProfile["CharName"]],
        ["Games Played: ", userProfile["Games Played"]], ["In Game: ",userProfile["In Game"]], ]

        
        await self.bot.send_message(author, header)
        await self.bot.send_message(author, "```" + tabulate(table, tablefmt="rst") +"```")

    @dnd.group(pass_context=True)
    async def roll(self,ctx):
        """Rolls a dice of the selected size"""
        if ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group):
                await send_cmd_help(ctx)

    @roll.command(pass_context=True)
    async def d4(self,ctx,numberOfRolls):
        """Rolls a four sided die, the number of times specified"""
        author = ctx.message.author
        counter = int(numberOfRolls)
        results = []
        if counter == 1:
            await self.bot.say ("{}, You rolled a **{}**! ".format(author.mention, self.diceRolls.roll4()))
        else:
            while counter >0:
                results.append(self.diceRolls.roll4())
                counter -= 1
            await self.bot.say("{}, Your rolls were: {}".format(author.mention, results))

    @roll.command(pass_context=True)
    async def d6(self,ctx,numberOfRolls):
        """Rolls a six sided die, the number of times specified"""
        author = ctx.message.author
        counter = int(numberOfRolls)
        results = []
        if counter == 1:
            await self.bot.say ("{}, You rolled a **{}**! ".format(author.mention, self.diceRolls.roll6()))
        else:
            while counter >0:
                results.append(self.diceRolls.roll6())
                counter -= 1
            await self.bot.say("{}, Your rolls were: {}".format(author.mention, results))

    @roll.command(pass_context=True)
    async def d8(self,ctx,numberOfRolls):
        """Rolls an eight sided die, the number of times specified"""
        author = ctx.message.author
        counter = int(numberOfRolls)
        results = []
        if counter == 1:
            await self.bot.say ("{}, You rolled a **{}**! ".format(author.mention, self.diceRolls.roll8()))
        else:
            while counter >0:
                results.append(self.diceRolls.roll8())
                counter -= 1
            await self.bot.say("{}, Your rolls were: {}".format(author.mention, results))

    @roll.command(pass_context=True)
    async def d10(self,ctx,numberOfRolls):
        """Rolls a ten sided die, the number of times specified"""
        author = ctx.message.author
        counter = int(numberOfRolls)
        results = []
        if counter == 1:
            await self.bot.say ("{}, You rolled a **{}**! ".format(author.mention, self.diceRolls.roll10()))
        else:
            while counter >0:
                results.append(self.diceRolls.roll10())
                counter -= 1
            await self.bot.say("{}, Your rolls were: {}".format(author.mention, results))

    @roll.command(pass_context=True)
    async def d12(self,ctx,numberOfRolls):
        """Rolls a ten sided die, the number of times specified"""
        author = ctx.message.author
        counter = int(numberOfRolls)
        results = []
        if counter == 1:
            await self.bot.say ("{}, You rolled a **{}**! ".format(author.mention, self.diceRolls.roll12()))
        else:
            while counter >0:
                results.append(self.diceRolls.roll12())
                counter -= 1
            await self.bot.say("{}, Your rolls were: {}".format(author.mention, results))

    @roll.command(pass_context=True)
    async def d20(self,ctx,numberOfRolls):
        """Rolls a ten sided die, the number of times specified"""
        author = ctx.message.author
        counter = int(numberOfRolls)
        results = []
        if counter == 1:
            await self.bot.say ("{}, You rolled a **{}**! ".format(author.mention, self.diceRolls.roll20()))
        else:
            while counter >0:
                results.append(self.diceRolls.roll20())
                counter -= 1
            await self.bot.say("{}, Your rolls were: {}".format(author.mention, results))

    @roll.command(pass_context=True)
    async def d100(self,ctx,numberOfRolls):
        """Rolls a ten sided die, the number of times specified"""
        author = ctx.message.author
        counter = int(numberOfRolls)
        results = []
        if counter == 1:
            await self.bot.say ("{}, You rolled a **{}**! ".format(author.mention, self.diceRolls.roll100()))
        else:
            while counter >0:
                results.append(self.diceRolls.roll100())
                counter -= 1
            await self.bot.say("{}, Your rolls were: {}".format(author.mention, results))
            

    def createPlayer(self, user, charName):
        server = user.server
        if not self.playerExists(user):
            if server.id not in self.players:
                self.players[server.id] = {}
            timestamp = datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S")
            player = {"Name": user.name,
                      "Games Played": 0,
                      "In Game": False,
                      "CharName": charName
                      }
            self.players[server.id][user.id] = player
            self.savePlayers();
        else:
            raise PlayerAlreadyRegistered()

    def createCharacterSheet(self,ctx):
        #placeholder method for now, more to follow.
        #response = await self.bot.wait_for_message(timeout=15, author=user) this will be usefull
        pass
                      
    def changeGameStatus(self,ctx,user,newStatus):
        if newStatus:
            updateGameCount(user, 1)
        
        player["In Game"] = newStatus
        
    def updateGameCount(self,ctx,user,newCount):
        player["Games Played"] += newCount
            
    def changeCharName (self,ctx,user,newName):
        player["CharName": newName]

    def savePlayers(self):
        dataIO.save_json(self.player_path, self.players)
    
        
    def playerExists(self, user):
        try:
            self.getPlayer(user)
        except NoAccount:
            return False
        return True
    
    def getPlayer(self, user):
        server = user.server
        try:
            return deepcopy(self.players[server.id][user.id])
        except KeyError:
            raise NoAccount()  
    
def check_folders(): 
        if not os.path.exists("data/Dungeon_Records"): 
            print("Creating data/Dungeon_Records folder...")
            os.makedirs("data/Dungeon_Records")

def check_files():
    f = "data/Dungeon_Records/players.json"
    if not dataIO.is_valid_json(f):
        print("Creating default players.json...")
        dataIO.save_json(f, {})




def setup(bot):
    check_folders() 
    check_files()
    bot.add_cog(DnD(bot))
