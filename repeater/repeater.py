import discord
import os
from discord.ext import commands
from cogs.utils.dataIO import dataIO
from copy import deepcopy



class Repeater:

	def __init__(self,bot):
		self.bot=bot
		self.settings_path = "data/repeater/settings.json"
		self.settings = dataIO.load_json("data/repeater/settings.json")

	@commands.command(pass_context=True)
	async def repeater(self,ctx):
		"""I will repeat anything you say until you say exit"""
		author = ctx.message.author
		channel = ctx.message.channel
		await self.bot.say("...yes? I'm listening... go on... (say exit to quit)")
		while True:
			response = await self.bot.wait_for_message(author = ctx.message.author)
			print(response)
			reply = response.content
			if "exit" in reply:
				break
				return
			await self.bot.delete_message(response)
			await self.bot.send_message(channel, reply, tts=True)

	@commands.command(pass_context=True)
	async def setchannel(self,ctx):
		""" This sets the channel which you send the command to as the text channel for announcements"""
		channel=ctx.message.channel

		self.settings["ChannelID"] = channel.id
		self.settings["ChannelName"] = channel.name
		self.save_settings()
		await self.bot.say("Set this channel for all Voice state Announcements")
		await self._getchannel(ctx)

	@commands.command(pass_context=True)
	async def getchannel(self,ctx):
		"""Returns the set announcement channel"""
		await self._getchannel(ctx)

	async def _getchannel(self,ctx):
		channelID = self.settings["ChannelID"]
		channelName = self.settings["ChannelName"]

		await self.bot.say("Name: {} \nID: {}".format(channelName,channelID))

	async def voice_state(self,userbefore,userafter):
		afkChannel = userbefore.server.afk_channel
		channel = discord.utils.get(self.bot.get_all_channels(), id=self.settings["ChannelID"])
		if userafter.voice.voice_channel != userbefore.voice.voice_channel:
			if userafter.voice.voice_channel != afkChannel:
				print("Changed detected: {} from {} to {}".format(userafter, userbefore.voice.voice_channel,userafter.voice.voice_channel))
				await self.bot.send_message(channel, "Changed detected: {} from {} to {}".format(userafter, userbefore.voice.voice_channel,userafter.voice.voice_channel))
			else:
				print("User {} is now in AFK channel {}".format(userafter,afkChannel))

		if userafter.voice.voice_channel != afkChannel:
			self.sc



	def save_settings(self):
		dataIO.save_json(self.settings_path, self.settings)

def check_folders():
    if not os.path.exists("data/repeater"): 
        print("Creating repeater default directory")
        os.makedirs("data/repeater")
    else:
    	print("Repeater Folder found successfully")


def check_files():
    default = {"ChannelID": 0, "ChannelName": "none"}

    f = "data/repeater/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, default)
    else:
        current = dataIO.load_json(f)
        print("Settings found successfully")


def setup(bot):
	check_folders()
	check_files()
	n = Repeater(bot)
	bot.add_listener(n.voice_state, "on_voice_state_update")
	bot.add_cog(Repeater(bot))
