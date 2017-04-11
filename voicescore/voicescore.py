import discord
import os
from discord.ext import commands
from cogs.utils.dataIO import dataIO
from copy import deepcopy
import time
import asyncio
import datetime


class VoiceScore:

	def __init__(self,bot):
		self.bot=bot
		self.settings_path = "data/voicescore/settings.json"
		self.settings = dataIO.load_json(self.settings_path)
		self.scores_path = "data/voicescore/scores.json"
		self.scores = dataIO.load_json(self.scores_path)
		self.eligibleChannels_path = "data/voicescore/channels.json"
		self.activeVCUsers = {}
		self.eligibleChannels = {}
		self.activeVClist = []
		self.payoutMembers = []
		self.timeLast = int(time.time())
		self._setupdefaults()

	@commands.command(pass_context=True)
	async def setchannel(self,ctx):
		""" This sets the channel which you send the command to as the text channel for announcements"""
		channel=ctx.message.channel
		server = ctx.message.server
		self.settings[server.id]["ChannelID"] = channel.id
		self.settings[server.id]["ChannelName"] = channel.name
		self.save_settings()
		await self.bot.say("Set this channel for all Voice state Announcements")
		await self._getchannel(ctx)

	@commands.command(pass_context=True)
	async def getchannel(self,ctx):
		server = ctx.message.server
		"""Returns the set announcement channel. Try using setchannel first."""
		await self._getchannel(ctx, server)

	@commands.command(pass_context=True)
	async def setpayoutscore(self,ctx, message:int):
		"""Sets the payout for when a user crosses the score threshold"""
		channel=ctx.message.channel
		server = ctx.message.server
		self.settings[server.id]["CreditsPerScore"] = message
		self.save_settings()
		await self.bot.say("New Payout set to {}".format(self.settings[server.id]["CreditsPerScore"]))

	@commands.command(pass_context=True)
	async def getpayoutscore(self,ctx):
		"""Returns the current payout for when a user crosses the score threshold."""
		await self.bot.say("Payout set to {}".format(self.settings[server.id]["CreditsPerScore"]))


	@commands.command(pass_context = True)
	async def get_all_vcmembers(self,ctx):
		await self.bot.say("***Current users active in Voice Channels:*** \n ```{}```".format(await self.voice_state(ctx.message.author,ctx.message.author)))

	@commands.command(pass_context = True)
	async def get_score(self,ctx):
		member = ctx.message.author
		server = ctx.message.server
		if server.id in self.scores:
			if member.id in self.scores[server.id]:
				output = self.scores[server.id][member.id]
				await self.bot.say("{}, your score is {}".format(member.mention, output))
			else:
				await self.bot.say("{}, you have no score yet! Connect to a voice channel to earn some.".format(member.mention))
		else:
			await self.bot.say("{}, you have no score yet! Connect to a voice channel to earn some.".format(member.mention))

	@commands.command(pass_context=True)
	async def unixtime(self,ctx):
		print("Unix Time: {}".format(time.time()))
		print("DateTime: {}".format(time.time()))
		printtime = datetime.datetime.fromtimestamp(int(time.time()))
		await self.bot.say("Unix Time:{} \nDate Time: {}".format(time.time(),printtime))

	async def _setupdefaults(self):

		for server in self.bot.servers:
			sid = server.id
			if sid not in self.settings:
				self.settings[sid] = {"ChannelID": 0, "ChannelName": "none", "CreditsPerScore": 250, "ScoreThreshold": 1800}

			



	async def _getchannel(self,ctx,server):
		channelID = self.settings[server.id]["ChannelID"]
		channelName = self.settings[server.id]["ChannelName"]

		await self.bot.say("Name: {} \nID: {}".format(channelName,channelID))

	async def voice_state_message_primer(self,message):
		author = message.author
		await asyncio.sleep(5)
		await self.voice_state(author,author)
		return

	async def voice_state(self,userbefore,userafter):
		server = userbefore.server
		sid = server.id
		afkChannel = userbefore.server.afk_channel
		timeNow = int(time.time())
		if sid not in self.activeVCUsers.keys():
			self.activeVCUsers[sid] = {}
		if sid not in self.eligibleChannels.keys():
			self.eligibleChannels[sid] = {}
		if sid not in self.scores.keys():
			self.scores[sid] = {}
		if sid not in self.scores.keys():
			self.scores[sid] = {}

		vcMembers = 0
		ovcMembers = 0
		eligibleChannel = False
		# for loop that checks each channels eligability for score and assings the json true or not.
		# needs to be here for updating.
		# doesnt actually need to save to json. Did that for figurings
		tempEligible = []
		for currServer in self.bot.servers:
			sid = currServer.id
			if sid not in self.activeVCUsers.keys():
				self.activeVCUsers[sid] = {}
			if sid not in self.eligibleChannels.keys():
				self.eligibleChannels[sid] = {}
			if sid not in self.scores.keys():
				self.scores[sid] = {}
			if sid not in self.scores.keys():
				self.scores[sid] = {}
			for channel in currServer.channels:
				vcMembers = len(channel.voice_members)
				ovcMembers = vcMembers - 1
				if ovcMembers > 0:
					if channel != afkChannel:
						tempEligible.append("{}".format(channel))

		sid = server.id
		
		self.saveChannels()
		# for loop to check conditions of eligibility of member. not deafened, not single channel afk,
		# not afk channel. if works, update the active voice client list.
		tempVClist = []
		for member in server.members:
			if member.voice_channel is not None:
				vcID = member.voice.voice_channel.id
				if self._finditem(self.eligibleChannels, vcID):
					if not member.self_deaf and not member.is_afk and not member.bot:
						tempVClist.append(member)

		self.activeVClist = tempVClist
		totalVCmembers = len(self.activeVClist)

		tempNameList = []
		timeBetween = timeNow - self.timeLast
		adjustAmount = int(timeBetween/10)
		adjustAmount = adjustAmount * totalVCmembers
		adjustedScore = timeBetween + adjustAmount

		for member in self.activeVClist:
			if member.id not in self.scores[sid]:
				self.scores[sid][member.id] = 0
			self.scores[sid][member.id] += adjustedScore
			finalScore = self.checkScores(server, member)
			self.scores[sid][member.id] = finalScore
			tempNameList.append(member.name)

		timestamp = datetime.datetime.fromtimestamp(int(time.time()))
		scoreGiven = "Score given: {} \nMembers: {}".format(adjustedScore, tempNameList)
		eligChannels = "Eligible Channels: {}".format(tempEligible)

		if len(self.payoutMembers) > 0:
			payOutMems = "Payed out members: {}".format(self.payoutMembers)
			with open("data/voicescore/log.txt", "a") as log_file:
				log_file.write("\nTime: \n{} \n{} \n{}".format(timestamp, scoreGiven,eligChannels,payOutMems))
		else:
			with open("data/voicescore/log.txt", "a") as log_file:
				log_file.write("\nTime: \n{} \n{} \n{} \n{}".format(timestamp, scoreGiven,eligChannels,"No Members payed out"))

		vcMembers = 0
		ovcMembers = 0
		eligibleChannel = False
		tempEligible = []
		for currServer in self.bot.servers:
			for channel in currServer.channels:
				vcMembers = len(channel.voice_members)
				ovcMembers = vcMembers - 1
				if ovcMembers > 0:
					if channel != afkChannel:
						self.eligibleChannels[currServer.id][channel.id] = True
						tempEligible.append("{}".format(channel))
					else:
						print("{} users now AFK".format(vcMembers))
				else:
					self.eligibleChannels[currServer.id][channel.id] = False
			

		self.saveChannels()
		self.saveScores()
		self.timeLast = int(time.time())
		self.payoutMembers = []
		return(tempNameList)

	def checkScores(self, server, member):
		currScore = self.scores[server.id][member.id]
		threshold = int(self.settings[server.id]["ScoreThreshold"])
		if currScore >= threshold:
			currScore -= threshold
			self.payOut(member, server.id)
			return currScore
		else:
			return currScore

	def payOut(self, member,sid):
		#payout method with bank access. check coupon cog for help. coupon redeem
		econ = self.bot.get_cog('Economy')
		if econ == None:
			print("Error loading economy cog.")
			return
		basePot = self.settings[sid]["CreditsPerScore"]
		if econ.bank.account_exists(member):
			econ.bank.deposit_credits(member, basePot)
			self.payoutMembers.append(member.name)
		else:
			print("User {} has no account, failed to pay".format(member.name))

	def saveChannels(self):
		dataIO.save_json(self.eligibleChannels_path, self.eligibleChannels)

	def saveScores(self):
		dataIO.save_json(self.scores_path, self.scores)

	def save_settings(self):
		dataIO.save_json(self.settings_path, self.settings)

	def _finditem(self, mydict, key):
		if key in mydict: 
			return mydict[key]
		for k, v in mydict.items():
			if isinstance(v,dict):
				return self._finditem(v, key)

def check_folders():
	if not os.path.exists("data/voicescore"): 
		print("Creating voicescore default directory")
		os.makedirs("data/voicescore")
	else:
		print("Voicescore Folder found successfully")


def check_files():
	f = "data/voicescore/settings.json"
	if not dataIO.is_valid_json(f):
		print("Creating default settings.json...")
		dataIO.save_json(f, {})
	else:
		current = dataIO.load_json(f)
		print("Settings found successfully")

	f = "data/voicescore/scores.json"
	if not dataIO.is_valid_json(f):
		print("Creating default scores.json...")
		dataIO.save_json(f, {})
	else:
		current = dataIO.load_json(f)
		print("Scores found successfully")


def setup(bot):
	check_folders()
	check_files()
	n = VoiceScore(bot)
	bot.add_listener(n.voice_state, "on_voice_state_update")
	bot.add_cog(n)
