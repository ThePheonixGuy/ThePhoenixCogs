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
		self.activeVCUsers = {}

	@commands.command(pass_context=True)
	async def repeater(self,ctx):
		"""I will repeat anything you say until you say exit"""
		author = ctx.message.author
		channel = ctx.message.channel
		ttsProperty = None

		try:
			ttsProperty = self.settings["TTS"]
		except KeyError:
			self.settings["TTS"] = False

		if ttsProperty is None:
			ttsProperty = False
		await self.bot.say("...yes? I'm listening... go on... (say exit to quit)")
		while True:
			response = await self.bot.wait_for_message(author = ctx.message.author)
			reply = response.content
			if "exit" in reply:
				await self.bot.say("Fine... I won't spew your bigotries any further")
				break
				return
			await self.bot.delete_message(response)
			await self.bot.send_message(channel, reply, tts = ttsProperty)

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

	@commands.command(pass_context=True)
	async def set_tts(self,ctx,message):
		"""Sets whether the bot repeats what you said in Text to Speech or not. Accepts only true or false as the operator."""
		print(message)
		if "true" in message:
			self.settings["TTS"] = True
			await self.bot.say("TTS is now active")
		elif "false" in message:
			self.settings["TTS"] = False
			await self.bot.say("TTS is no longer active")
		else:
			await self.bot.say("Please say either true or false.")
		self.save_settings()

	@commands.command(pass_context = True)
	async def get_all_vcmembers(self,ctx):
		servermembers = self.bot.get_all_members()
		server = ctx.message.server
		sid = ctx.message.server.id
		afkChannel = server.afk_channel
		vcMembers = 0
		ovcMembers = 0
		tempVClist = []
		if sid not in self.activeVCUsers.keys():
			self.activeVCUsers[sid] = {}

		for member in servermembers:
			if member.server == server:
				if member.voice_channel is not None:
					if member.voice_channel is not afkChannel:
						if not member.self_deaf:
							if not member.bot:
								print(member.name)
								tempVClist.append(member.name)
								self.activeVCUsers[sid][member.name] = member.id


		await self.bot.say("```Current active Voice Clients: \n{}```".format(tempVClist))


	async def _getchannel(self,ctx):
		channelID = self.settings["ChannelID"]
		channelName = self.settings["ChannelName"]

		await self.bot.say("Name: {} \nID: {}".format(channelName,channelID))

	async def voice_state(self,userbefore,userafter):
		server = userbefore.server
		userBChannel = userbefore.voice.voice_channel
		userAChannel = userafter.voice.voice_channel
		userAVoice = userafter.voice
		userBVoice = userbefore.voice
		afkChannel = userbefore.server.afk_channel
		channel = discord.utils.get(self.bot.get_all_channels(), id=self.settings["ChannelID"])
		if userafter.voice.voice_channel == userbefore.voice.voice_channel:
			print("In-channel changed detected on {}".format(userafter))
			if userAVoice.self_deaf:
				print("User {} deafened.".format(userafter))
			elif not userAVoice.self_deaf and userBVoice.self_deaf:
				print("User {} undeafened.".format(userafter))
		else:
			if userAChannel != afkChannel:
				if userAChannel is not None:
					print("Active User Detected: {}".format(userafter))
					print("Channel: {}, Users in channel: {}".format(userAChannel, len(userAChannel.voice_members)))
				else:
					print("User has left voice channels: {}".format(userafter))
			elif userAChannel == afkChannel:
				print("User is now Inactive: {}".format(userafter))

		vcMembers = 0
		ovcMembers = 0
		eligibleChannel = False
		if userAChannel is not None:
			vcMembers = len(userAChannel.voice_members)
			ovcMembers = vcMembers - 1
		
		if not userAVoice.self_deaf:
			if ovcMembers > 0:
				print("Channel {} and its users are valid for score.".format(userAChannel))
				eligibleChannel = True
			elif userAChannel is None:
				print("User {} removed from active register".format(userafter))
			else:
				print("Not eligible. Only {} in channel".format(userafter))

		if eligibleChannel:
			for user in userAChannel.voice_members:
				if not user.bot:
					print(user.name)

		servermembers = self.bot.get_all_members()

		for member in servermembers:
			if member.voice_channel is not None:
				if not member.self_deaf:
					vcMembers = len(userAChannel.voice_members)
					ovcMembers = vcMembers - 1








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
