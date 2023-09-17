import discord
import aiohttp
from discord import app_commands
from discord.ext import commands
from config import *
from cogs.ticket import opzionistaff, menustaff, ticket_bott

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all(), case_insensitive=True)
        self.script_necessari = ['cogs.ticket']
        self.bottoni_dacaricare = [opzionistaff, menustaff, ticket_bott]
        self.startato = False

    async def setup_hook(self):
        self.sessione = aiohttp.ClientSession()
        for file in self.script_necessari: 
            await self.load_extension(file)
        await self.tree.sync()
        print(f"Syncato con {self.user}!")

    async def close(self):
        await super().close()
        await self.sessione.close()

    async def on_ready(self):
        print(f'{self.user} connesso! - https://github.com/itsmat')
        if not self.startato:
            for bottone in self.bottoni_dacaricare: 
                self.add_view(bottone())
            self.startato = True
            await bot.change_presence(activity=discord.Game(name=f"Ticket Bot - github.com/itsmat"))

    async def on_message(self, message):
        pass

bot = Bot()
bot.remove_command('help')
bot.run(token)
