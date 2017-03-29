import discord
import os
from discord.ext import commands
import asyncio
from .utils.dataIO import dataIO
from __main__ import send_cmd_help
import chardet
import time
from cogs.utils.chat_formatting import pagify

try:   # Check if Tabulate is installed
    import validators
    validatorAvailable = True
except ImportError:
    validatorAvailable = False


class PlaylistManager():

    def __init__(self,bot):
        self.bot = bot
        #self.file_path = "data/playlist/settings.json"
        #self.settings = dataIO.load_json(self.file_path)

    @commands.group(pass_context=True)
    async def pl(self,ctx):
        """Playlist Handler for Red's associated Music Bot. Needs Validators. use [p]debug bot.pip_install('pillow')"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            return

    @pl.command(pass_context=True, name = "play")
    async def play_playlist(self,ctx,list_name:str=None):
        """Lists all stored playlists of Red, and lets you queue them to Music Minion"""
        message = ctx.message
        author = ctx.message.author
        channelID = '246396593291526155'
        channel = discord.utils.get(self.bot.get_all_channels(), id=channelID)
        if list_name == None:
            await self.list_playlist(ctx.message.author)
        else:
            current_list = await self.load_playlist(message.content)
            await self.queue_up_list(current_list,author)
            await self.bot.say("Successfully queued. Here is the current queue...")
            await self.bot.say("=queue")

    @pl.command(pass_context=True, name = "list")
    async def return_list(self,ctx):
        """Retuns the list of playlists."""
        await self.list_playlist(ctx.message.author)

    @pl.command(pass_context=True, name = "build")
    async def build_list(self,ctx,name):
        """lets you input youtube links for a playlist. Use exit to stop"""
        author = ctx.message.author
        channel = ctx.message.channel
        plname = name
        new_list = []
        #add validators with pip install validators
        await self.bot.say("Please send each link as a new message. When done, say `exit`")
        with open("data/playlists/{}.txt".format(plname),"a+") as text_file:
            while True:
                response = await self.bot.wait_for_message(author = ctx.message.author, channel = ctx.message.channel)
                
                if "exit" in response.content:
                    break
                    return
                newLink = "{}{}".format(response.content,'`\n')
                if validators.url(response.content):
                    await self.bot.say("Valid and saved. Next?")
                    print(validators.url(response.content))
                    text_file.write(newLink)
                else:
                    await self.bot.say("Invalid Link. Please send a valid link in the form ```http://***.com```")
                response = None
        text_file.close()
        await self.bot.say("Exitted Successfuly. Sending your songs to the magic gnomes for construction....")

    async def list_playlist(self, author):
        msg = "**Available playlists:** \n\n```"
        lists = "data/playlists/"

        ret = []
        for thing in os.listdir(lists):
            if os.path.isdir(os.path.join(lists)):
                ret.append(thing)
        print("local playlists:\n\t{}".format(ret))

        playlists = ", ".join(ret)
        if playlists:
            playlists = "Available local playlists:\n\n" + playlists
            for page in pagify(playlists, delims=[" "]):
                await self.bot.say(page)

        else:
            await self.bot.say("There are no playlists.")

    async def load_playlist(self, msg):
        msg = msg.split(" ")
        if len(msg) == 3:
            _, _, plist = msg
            if os.path.isfile("data/playlists/" + plist + ".txt"):
                self.current_list = await self.load_list("data/playlists/" + plist + ".txt")
                return self.current_list
            else:
                await self.bot.say("There is no playlist with that name. Please make sure you omit the `.txt` from the name")
                return

    def guess_encoding(self, trivia_list):
        with open(trivia_list, "rb") as f:  
            try:
                return chardet.detect(f.read())["encoding"]
            except:
                return "ISO-8859-1"

    async def load_list(self, plist):
        encoding = self.guess_encoding(plist)
        with open(plist, "r", encoding=encoding) as f:
            plist = f.readlines()
        parsed_list = []
        count = 0
        for line in plist:
            if "`" in line:
                line = line.replace("\n","")
                line = line.split("`")
                lineCopy = line[0]
                print(lineCopy)
                parsed_list.append(lineCopy)
                count += 1
        if parsed_list != []:
            await self.bot.say("{} songs were found. Sending them to the queue.".format(count))
            #await self.queue_up_list(parsed_list,count)
            return parsed_list
        else:
            print("nothing in list")
            return None

    async def queue_up_list(self,plist,author):
        channelID = '295918044058746880'
        channel = discord.utils.get(self.bot.get_all_channels(), id=channelID)
        voicechannel = author.voice_channel
        server = author.server
        if not self.bot.is_voice_connected(server):
            await self.bot.join_voice_channel(voicechannel)
        time.sleep(1)
        await self.bot.send_message(channel, "=summon")
        for song in plist:
            song = "=play " + song
            await self.bot.send_message(channel, song)
            time.sleep(0.25)
        await self.bot.voice_client_in(server).disconnect()
        time.sleep(10)
        await self.bot.send_message(channel, "=clean")






async def message_handler(message):
    if message.content == "build":
        print("I reached Here!")

def check_folders():
    folders = ("data", "data/playlists/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)

def setup(bot):
    check_folders()
    if validatorAvailable:
        bot.add_cog(PlaylistManager(bot))
    else:
        raise RuntimeError("You need to run 'pip3 install validators'")
    
