import discord
from discord.ext import commands, tasks
from discord import app_commands, utils
import json, time
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
import chat_exporter, io
from discord import ui 
from config import *
colorama_init()

def prendiruoloticketstaff():
    return staff_role

class ticket_bott(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 2, commands.BucketType.member)
        self.ticket_mod = prendiruoloticketstaff()
    
    @discord.ui.button(label = "Open ticket", style = discord.ButtonStyle.grey, custom_id = "ticket_button_1", emoji="<:bot_ticket:1124252501491851335> ")
    async def apriticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        calldown_status = self.cooldown.get_bucket(interaction.message).update_rate_limit()
        if calldown_status:
            return await interaction.response.send_message(f"Calldown! Wait {round(calldown_status, 1)} seconds!", ephemeral = True)
        check_ticket_esistente = utils.get(interaction.guild.text_channels, name = f"ticket-{interaction.user.name.lower().replace(' ', '-')}-{interaction.user.discriminator}")
        if check_ticket_esistente is not None:
            await interaction.response.send_message(f"You already have an open ticket {check_ticket_esistente.mention}!", ephemeral = True)
        else:
            if type(self.ticket_mod) is not discord.Role: 
                self.ticket_mod = interaction.guild.get_role(self.ticket_mod)
            perms_ticket = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
                interaction.user: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
                interaction.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True), 
                self.ticket_mod: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
            }
            categoria = discord.utils.get(interaction.guild.categories, name=ticketcategoryname)
            if categoria is None:
                categoria = await interaction.guild.create_category(ticketcategoryname)
            try:
                ticket_creato = await interaction.guild.create_text_channel(name = f"ticket-{interaction.user.name}-{interaction.user.discriminator}", topic = f'{interaction.user.id}', overwrites = perms_ticket, reason = f"Ticket per {interaction.user} - https://github.com/itsmat", category=categoria)
            except Exception as errore:
                print(f"[Ticket Log] {Fore.LIGHTRED_EX}Error creating ticket! [@{interaction.user} - #{interaction.channel}] {errore}{Style.RESET_ALL}")
                return await interaction.response.send_message("Errore permessi", ephemeral = True)
            embed=discord.Embed(title=f"", description=f"{interaction.user.mention} opened the ticket!", color=embedcolor)
            embed.set_author(name=ticketauthor, icon_url=f'{logoticket}')
            embed.set_footer(text=ticketauthor, icon_url=f'{logoticket}')
            await ticket_creato.send(f"<@&{staff_role}>", embed=embed, view = opzionistaff())
            await interaction.response.send_message(f"Ticket: {ticket_creato.mention}!", ephemeral = True)
            print(f"[Ticket Log] {Fore.LIGHTBLUE_EX}New ticket created [@{interaction.user} #{ticket_creato}] {Style.RESET_ALL}")

class confirm(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label = "Confirm", style = discord.ButtonStyle.red, custom_id = "confirm")
    async def confirm_button(self, interaction, button):
        transcript = await chat_exporter.export(interaction.channel)
        if transcript is None:
            return
        transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                       filename=f"transcript-{interaction.channel.name}.html")
        transcript_filelog = discord.File(io.BytesIO(transcript.encode()),
                                       filename=f"transcript-{interaction.channel.name}.html")
        user = await interaction.guild.query_members(user_ids=[interaction.channel.topic])
        canalelog = interaction.guild.get_channel(logticket)
        embed=discord.Embed(color=embedcolor)
        embed.set_author(name=authorname, icon_url=f"{logoticket}")
        embed.set_thumbnail(url=logoticket)
        embed.add_field(name="<:greenv:1124252496416755762> Open from:", value=f"<@{interaction.channel.topic}>", inline=True)
        embed.add_field(name="<:bot_padlock:1124252499520528495> Closed from:", value=f"<@{interaction.user.id}>", inline=True)
        embed.add_field(name="<:bot_ticket:1124252501491851335> Ticket", value=f"{interaction.channel.name}", inline=True)
        testocategoria = f'{interaction.channel.category}'.replace("</TICKETS ", '')
        testocategoria = testocategoria.replace(">", '')
        embed.add_field(name="<:bot_ann:1124252503815503963> Category", value=f"{testocategoria}", inline=True)
        embed.set_footer(text=ticketfooterdev, icon_url=f'{logoticket}')
        try:
            await user[0].send(embed=embed, file=transcript_file)
        except:
            print(f"[ERRORE Ticket Log] {Fore.LIGHTRED_EX}Errore nell'invio del messaggio all'utente [{interaction.channel.topic}] {Style.RESET_ALL}")
        await canalelog.send(embed=embed, file=transcript_filelog)
        print(f"[Ticket Log] {Fore.LIGHTBLUE_EX}Ticket closed [@{interaction.user} #{interaction.channel.name}] {Style.RESET_ALL}")
        try:
            await interaction.channel.delete()
        except:
            await interaction.response.send_message("Errore permessi", ephemeral = True)
        
class Aggiungi(ui.Modal, title='Add user'):
        utente = ui.TextInput(label='Enter the user id')
        
        async def on_submit(self, interaction: discord.Interaction):
            cane = f'{self.utente}'
            user = interaction.guild.get_member(int(cane)) 
            await interaction.channel.set_permissions(user, send_messages=True, read_messages=True, view_channel=True)
            await interaction.response.send_message(f'Added {user.mention} to the ticket')
            
            canalelog = interaction.guild.get_channel(logticket)
            embed=discord.Embed(title="", description=f"**Utente:** {interaction.user.mention}\n**Azione:** Adding user to ticket\n**Channel:** {interaction.channel.mention}\n**User**: {user.mention}", color=embedcolor)
            embed.set_author(name='Log Bot', icon_url=f'{logoticket}')
            embed.set_footer(text=ticketfooterdev, icon_url=f'{logoticket}')
            await canalelog.send(embed=embed)
            print(f"[Ticket Log] {Fore.LIGHTBLUE_EX}User added [@{interaction.user} #{interaction.channel.name} | Added: @{user}] {Style.RESET_ALL}")

class Rimuovi(ui.Modal, title='Remove user'):
        utente = ui.TextInput(label='Enter the user id')
        
        async def on_submit(self, interaction: discord.Interaction):
            cane = f'{self.utente}'
            user = interaction.guild.get_member(int(cane)) 
            await interaction.channel.set_permissions(user, send_messages=False, read_messages=False, view_channel=False)
            await interaction.response.send_message(f'Removed {user.mention} to the ticket')
            canalelog = interaction.guild.get_channel(logticket)
            embed=discord.Embed(title="", description=f"**Utente:** {interaction.user.mention}\n**Azione:** Removing user to ticket\n**Channel:** {interaction.channel.mention}\n**User**: {user.mention}", color=embedcolor)
            embed.set_author(name='Log Bot', icon_url=f'{logoticket}')
            embed.set_footer(text=ticketfooterdev, icon_url=f'{logoticket}')
            await canalelog.send(embed=embed)
            print(f"[Ticket Log] {Fore.LIGHTBLUE_EX}User removed [@{interaction.user} #{interaction.channel.name} | Removed: @{user}] {Style.RESET_ALL}")

class menustaff(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label = "Add user", style = discord.ButtonStyle.grey,custom_id = "aggiungiutente")
    async def aggiungiutente(self, interaction, button):
        await interaction.response.send_modal(Aggiungi())
    
    @discord.ui.button(label = "Remove user", style = discord.ButtonStyle.grey,custom_id = "rimuoviutente")
    async def rimuoviutente(self, interaction, button):
        await interaction.response.send_modal(Rimuovi())

    @discord.ui.button(label = "Close", style = discord.ButtonStyle.red,custom_id = "chiuditicket")
    async def chiuditicket(self, interaction, button):
        embed = discord.Embed(title = "Are you sure you want to close the ticket?", color = embedcolor)
        await interaction.response.send_message(embed = embed, view = confirm(), ephemeral = True)

class opzionistaff(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label = "Staff options", style = discord.ButtonStyle.red, emoji = '<:botmod:1124254955340050542>',custom_id = "opzionistaff")
    async def staffopzioni(self, interaction, button):
        ruolostaff = discord.utils.get(interaction.guild.roles, id=prendiruoloticketstaff())
        if ruolostaff in interaction.user.roles:
            embed = discord.Embed(title = "", description=f":arrow_double_down:" ,color = embedcolor)
            embed.set_author(name=authorname, icon_url=f"{logoticket}")
            embed.set_thumbnail(url=logoticket)
            embed.set_footer(text=ticketfooterdev, icon_url=f'{logoticket}')
            await interaction.response.send_message(embed = embed, view = menustaff(), ephemeral = True)
            print(f"[Ticket Log] {Fore.LIGHTBLUE_EX}Opened staff menu [@{interaction.user} #{interaction.channel.name}] {Style.RESET_ALL}")
        else:
            await interaction.response.send_message("You cannot access this menu!", ephemeral = True)
    
class Ticket(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ticket_mod = prendiruoloticketstaff()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[Ticket] {Fore.LIGHTGREEN_EX}Online!{Style.RESET_ALL}")

    @commands.hybrid_command(name = 'ticket', with_app_command = True, description='Ticket message') 
    @app_commands.default_permissions(manage_guild = True)
    @app_commands.checks.cooldown(3, 60, key = lambda i: (i.guild_id))
    @app_commands.checks.bot_has_permissions(manage_channels = True)
    async def ticketing(self, ctx):
        if ctx.guild is None:
            ctx.send(error_dm)
        else:
            await ctx.send("Attendi", ephemeral = True)
            canale = ctx.message.channel
            embed = discord.Embed(title ='', description='''**To create a ticket press the buttons below!**''', color = embedcolor)
            embed.set_author(name=ticketauthor, icon_url=f"{logoticket}")
            embed.set_footer(text=ticketfooterdev, icon_url=f'{logoticket}')
            await canale.send(embed = embed, view = ticket_bott())
            print(f"[Ticket Log] {Fore.LIGHTGREEN_EX}Ticket message created! [@{ctx.message.author} - #{canale}]{Style.RESET_ALL}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ticket(bot))
