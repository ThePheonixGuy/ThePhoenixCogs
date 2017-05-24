import discord
from discord.ext import commands
import asyncio
import aiohttp
from cogs.utils.dataIO import dataIO
import requests

class Interpretter:
    """API.ai Interpretter Cog"""

    def __init__(self, bot):
        self.bot = bot
        self.API_URL = "https://api.api.ai/v1/"
        self.session = 12345

    @commands.command()
    async def interpret(self, * , query_text):
        """Attempts to interpret a query and provide a response."""
        self._interpret(query_text)


    async def _interpret(self, args):
        headers = {
            'Authorization' : 'Bearer 9e64f7a6a64f4c7fbf3d495319b26851' #TODO change to input-able key
        }

        params = {'query' : args, 'lang' : 'en', 'sessionId' : self.session}

        queryapi = "{}query?v=20150910".format(self.API_URL)
        r = requests.get(queryapi, headers = headers, params = params)
        output = r.json()
        #with aiohttp.get(queryapi, params=params, headers=headers) as response:
        #    r = await response.json()
        
        response = output['result']['fulfillment']['speech']
        print(response)
        return response

    async def checkmention(self, message):
        #if len(message.mentions) > 0:
            #if message.mentions[0].id == self.bot.user.id:
        await self.bot.send_typing(message.channel)
        word_list = message.content.split()
        word_list = word_list[1:]
        args = " ".join(word_list)

        response = await self._interpret(args)
        if len(response) < 2 :
            await self.bot.send_message(message.channel, "Didnt quite catch that... Sorry")
            return

        await self.bot.send_message(message.channel, response)





def setup(bot):
    n = Interpretter(bot)
    bot.add_listener(n.checkmention, "on_message")
    bot.add_cog(n)

