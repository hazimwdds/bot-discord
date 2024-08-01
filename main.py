import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import string
import os
from config import TOKEN, REPORT_CHANNEL_ID, ROLE_TO_ADD, ROLE_TO_REMOVE, STAFF_ROLE_ID, SUGGESTION_CHANNEL_ID, TICKET_CHANNEL_ID, LOG_CHANNEL_ID

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

report_data = {}
suggestion_data = {}
active_captchas = {}

# Funzioni di utilità
def generate_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_unique_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Funzione per inviare un messaggio al canale di log
async def log_event(message: str):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(message)

@bot.event
async def on_ready():
    print(f'Siamo entrati come {bot.user}')
    await bot.tree.sync()
    print('Comandi slash sincronizzati')

@bot.event
async def on_member_join(member: discord.Member):
    log_message = f"**MEMBER JOIN**: {member.mention} ({member.id}) si è unito al server. Data di creazione: {member.created_at.strftime('%d/%m/%Y %H:%M:%S')}"
    await log_event(log_message)

@bot.event
async def on_member_remove(member: discord.Member):
    log_message = f"**MEMBER LEAVE**: {member.mention} ({member.id}) ha lasciato il server."
    await log_event(log_message)

@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.author.bot:
        return
    log_message = f"**MESSAGE EDIT**: Messaggio di {before.author.mention} modificato nel canale {before.channel.mention}. \nPrima: {before.content}\nDopo: {after.content}"
    await log_event(log_message)

@bot.event
async def on_message_delete(message: discord.Message):
    if message.author.bot:
        return
    log_message = f"**MESSAGE DELETE**: Messaggio di {message.author.mention} eliminato nel canale {message.channel.mention}. Contenuto: {message.content}"
    await log_event(log_message)

@bot.event
async def on_channel_create(channel: discord.abc.GuildChannel):
    log_message = f"**CHANNEL CREATE**: Nuovo canale creato: {channel.mention} ({channel.id})"
    await log_event(log_message)

@bot.event
async def on_channel_delete(channel: discord.abc.GuildChannel):
    log_message = f"**CHANNEL DELETE**: Canale eliminato: {channel.name} ({channel.id})"
    await log_event(log_message)

@bot.event
async def on_command(ctx: commands.Context):
    log_message = f"**COMMAND USAGE**: Comando '{ctx.command}' usato da {ctx.author.mention} nel canale {ctx.channel.mention}."
    await log_event(log_message)

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    log_message = f"**COMMAND ERROR**: Errore nel comando '{ctx.command}' usato da {ctx.author.mention} nel canale {ctx.channel.mention}. Errore: {error}"
    await log_event(log_message)

# Comandi slash
@bot.tree.command(name="verify", description="Verifica il tuo account con CAPTCHA")
async def verify(interaction: discord.Interaction):
    user = interaction.user
    captcha_code = generate_captcha()
    active_captchas[user.id] = captcha_code

    await interaction.response.send_message(
        f"Per verificare il tuo account, rispondi a questo messaggio con il codice CAPTCHA: {captcha_code}. Hai 5 minuti per completare la verifica.",
        ephemeral=True
    )

    def check(m):
        return m.author == user and m.channel == interaction.channel and m.content == captcha_code

    try:
        msg = await bot.wait_for('message', check=check, timeout=300)
        await user.add_roles(discord.Object(id=ROLE_TO_ADD))
        await user.remove_roles(discord.Object(id=ROLE_TO_REMOVE))
        await interaction.followup.send("Verifica completata con successo!", ephemeral=True)
        log_message = f"**VERIFICATION PASSED**: {user.mention} ha completato la verifica con successo. Codice CAPTCHA: {captcha_code}."
        await log_event(log_message)
    except asyncio.TimeoutError:
        await interaction.followup.send("Tempo scaduto. Verifica non completata.", ephemeral=True)
    finally:
        if user.id in active_captchas:
            del active_captchas[user.id]

@bot.tree.command(name="kick", description="Espelle un utente")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    await member.kick(reason=reason)
    await interaction.response.send_message(f'{member} è stato espulso. Motivo: {reason}')

@bot.tree.command(name="ban", description="Banna un utente")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    await member.ban(reason=reason)
    await interaction.response.send_message(f'{member} è stato bannato. Motivo: {reason}')

@bot.tree.command(name="clear", description="Elimina un certo numero di messaggi")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f'{amount} messaggi sono stati eliminati.')

@bot.tree.command(name="tempban", description="Banna temporaneamente un utente")
@app_commands.checks.has_permissions(ban_members=True)
async def tempban(interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = None):
    await member.ban(reason=reason)
    await interaction.response.send_message(f'{member} è stato bannato per {duration} secondi. Motivo: {reason}')
    await asyncio.sleep(duration)
    await interaction.guild.unban(member)
    await interaction.channel.send(f'{member} è stato sbannato.')

@bot.tree.command(name="say", description="Invia un messaggio a un canale specifico")
async def say(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    await channel.send(message)
    await interaction.response.send_message(f'Messaggio inviato a {channel.mention}')

@bot.tree.command(name="partnership", description="Crea una partnership")
async def partnership(interaction: discord.Interaction, manager: discord.Member, cliente: discord.Member, channel: discord.TextChannel):
    await interaction.response.send_message('Inserisci la descrizione della partnership:')
    
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    description_msg = await bot.wait_for('message', check=check)
    
    partnership_message = f'Partnership creata da: {manager.mention}\nCliente: {cliente.mention}\nDescrizione: {description_msg.content}'
    await channel.send(partnership_message)
    await interaction.response.send_message(f'Partnership inviata a {channel.mention}')

@bot.tree.command(name="sync_roles", description="Sincronizza i permessi dei canali con quelli della loro categoria")
@app_commands.checks.has_permissions(administrator=True)
async def sync_roles(interaction: discord.Interaction):
    guild = interaction.guild
    
    if not guild:
        await interaction.response.send_message("Il comando può essere eseguito solo all'interno di un server.", ephemeral=True)
        return
    
    # Mappa per memorizzare i permessi dei canali e delle categorie
    category_permissions = {}
    
    # Ottieni tutte le categorie e salva i permessi
    for category in guild.categories:
        category_permissions[category.id] = {
            'default': category.overwrites_for(guild.default_role),
            'overwrites': {role.id: category.overwrites_for(role) for role in guild.roles}
        }
    
    # Sincronizza i permessi dei canali con quelli della categoria
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel) and channel.category:
            category_id = channel.category.id
            category_perm = category_permissions.get(category_id)
            
            if category_perm:
                overwrites = category_perm['overwrites']
                overwrites[guild.default_role.id] = category_perm['default']
                try:
                    await channel.edit(overwrites=overwrites)
                except Exception as e:
                    await interaction.response.send_message(f"Errore nella sincronizzazione del canale {channel.name}: {str(e)}", ephemeral=True)
                    return
    
    await interaction.response.send_message("Sincronizzazione dei permessi completata.", ephemeral=True)

@bot.tree.command(name="suggest", description="Invia un suggerimento")
async def suggest(interaction: discord.Interaction, suggestion: str):
    suggestion_id = generate_unique_id()
    suggestion_channel = bot.get_channel(SUGGESTION_CHANNEL_ID)
    if suggestion_channel:
        suggestion_data[suggestion_id] = {
            "suggestion": suggestion,
            "user": interaction.user
        }
        await suggestion_channel.send(f"**Suggerimento:**\n{suggestion}\n\n**ID:** {suggestion_id}\n**Inviato da:** {interaction.user.mention}")
        await interaction.response.send_message(f"Il tuo suggerimento è stato inviato con ID: {suggestion_id}")
    else:
        await interaction.response.send_message("Canale per i suggerimenti non trovato.")

@bot.tree.command(name="report", description="Segnala un problema o comportamento")
async def report(interaction: discord.Interaction, user: discord.User, reason: str):
    report_id = generate_unique_id()
    report_channel = bot.get_channel(REPORT_CHANNEL_ID)
    if report_channel:
        report_data[report_id] = {
            "user": user,
            "reason": reason,
            "reporter": interaction.user
        }
        await report_channel.send(f"**Segnalazione:**\n**Utente:** {user.mention}\n**Motivo:** {reason}\n**ID:** {report_id}\n\n**Inviato da:** {interaction.user.mention}")
        await interaction.response.send_message(f"La tua segnalazione è stata inviata con ID: {report_id}")
    else:
        await interaction.response.send_message("Canale per le segnalazioni non trovato.")

@bot.tree.command(name="respond", description="Rispondi a una segnalazione o suggerimento")
@app_commands.checks.has_permissions(administrator=True)
async def respond(interaction: discord.Interaction, unique_id: str, response: str, *, explanation: str = None):
    if unique_id in report_data:
        report = report_data.pop(unique_id)
        user = report["reporter"]
        if response.lower() == "si":
            await user.send(f"La tua segnalazione con ID {unique_id} è stata accettata.")
        elif response.lower() == "no":
            await user.send(f"La tua segnalazione con ID {unique_id} è stata respinta. Motivo: {explanation}")
        else:
            await interaction.response.send_message("La risposta deve essere 'si' o 'no'.")
            return
    elif unique_id in suggestion_data:
        suggestion = suggestion_data.pop(unique_id)
        user = suggestion["user"]
        if response.lower() == "si":
            await user.send(f"Il tuo suggerimento con ID {unique_id} è stato accettato.")
        elif response.lower() == "no":
            await user.send(f"Il tuo suggerimento con ID {unique_id} è stato respinto. Motivo: {explanation}")
        else:
            await interaction.response.send_message("La risposta deve essere 'si' o 'no'.")
            return
    else:
        await interaction.response.send_message("ID non trovato.")
        return
    await interaction.response.send_message(f"Risposta inviata per ID {unique_id}.")


@bot.tree.command(name="userinfo", description="Mostra informazioni su un utente")
async def userinfo(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title=f"Informazioni su {member.display_name}", color=0x00ff00)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Creato il", value=member.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.add_field(name="Entrato il", value=member.joined_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.add_field(name="Ruoli", value=", ".join([role.mention for role in member.roles[1:]]), inline=False)
    embed.set_thumbnail(url=member.avatar_url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Mostra informazioni sul server")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"Informazioni su {guild.name}", color=0x00ff00)
    embed.add_field(name="ID", value=guild.id, inline=False)
    embed.add_field(name="Creato il", value=guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.add_field(name="Membri", value=guild.member_count, inline=False)
    embed.add_field(name="Ruoli", value=len(guild.roles), inline=False)
    embed.set_thumbnail(url=guild.icon_url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Controlla il ping del bot")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! Il ping è di {latency}ms")

@bot.tree.command(name="avatar", description="Mostra l'avatar di un utente")
async def avatar(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(member.avatar_url)

@bot.tree.command(name="servericon", description="Mostra l'icona del server")
async def servericon(interaction: discord.Interaction):
    await interaction.response.send_message(interaction.guild.icon_url)

@bot.tree.command(name="poll", description="Crea un sondaggio")
async def poll(interaction: discord.Interaction, question: str, option1: str = None, option2: str = None, option3: str = None, option4: str = None, option5: str = None, option6: str = None, option7: str = None, option8: str = None, option9: str = None, option10: str = None):
    options = [option1, option2, option3, option4, option5, option6, option7, option8, option9, option10]
    options = [opt for opt in options if opt is not None]
    
    if len(options) < 2:
        await interaction.response.send_message("Devi specificare almeno due opzioni per il sondaggio.")
        return
    
    embed = discord.Embed(title="📊 | Sondaggio", description=question, color=0x00ff00)
    
    for idx, option in enumerate(options, 1):
        embed.add_field(name=f"Opzione {idx}", value=option, inline=False)
    
    message = await interaction.channel.send(embed=embed)
    
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    for idx in range(len(options)):
        await message.add_reaction(reactions[idx])
    
    await interaction.response.send_message("Sondaggio creato con successo.")



@bot.tree.command(name="remind", description="Imposta un promemoria")
async def remind(interaction: discord.Interaction, time: int, *, message: str):
    await interaction.response.send_message(f"Promemoria impostato per {time} minuti.")
    await asyncio.sleep(time * 60)
    await interaction.user.send(f"Promemoria: {message}")

@bot.tree.command(name="dice", description="Lancia un dado")
async def dice(interaction: discord.Interaction, sides: int):
    result = random.randint(1, sides)
    await interaction.response.send_message(f"Hai lanciato un dado da {sides} facce e hai ottenuto {result}.")

@bot.tree.command(name="joke", description="Racconta una barzelletta")
async def joke(interaction: discord.Interaction):
    jokes = [
        "Perché il caffè non è andato a scuola? Perché era troppo macchiato!",
        "Come si chiama un cane senza zampe? Non ha importanza, tanto non viene comunque!",
        "Perché il computer è andato dal medico? Perché aveva il virus!"
    ]
    await interaction.response.send_message(random.choice(jokes))

@bot.tree.command(name="quote", description="Mostra una citazione casuale")
async def quote(interaction: discord.Interaction):
    quotes = [
        "La vita è quello che accade mentre sei occupato a fare altri piani.",
        "Non contare i giorni, fa che i giorni contino.",
        "Non è mai troppo tardi per essere quello che avresti potuto essere."
    ]
    await interaction.response.send_message(random.choice(quotes))


@bot.tree.command(name="mute", description="Muta un utente per un periodo specificato")
@app_commands.checks.has_permissions(manage_roles=True)
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int):
    role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not role:
        role = await interaction.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False))
        for channel in interaction.guild.channels:
            await channel.set_permissions(role, send_messages=False)
    await member.add_roles(role)
    await interaction.response.send_message(f"{member.mention} è stato mutato per {duration} minuti.")
    await asyncio.sleep(duration * 60)
    await member.remove_roles(role)
    await interaction.channel.send(f"{member.mention} non è più mutato.")

@bot.tree.command(name="unmute", description="Sdemuta un utente")
@app_commands.checks.has_permissions(manage_roles=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    role = discord.utils.get(interaction.guild.roles, name="Muted")
    if role:
        await member.remove_roles(role)
        await interaction.response.send_message(f"{member.mention} non è più mutato.")
    else:
        await interaction.response.send_message("Ruolo 'Muted' non trovato.")

@bot.tree.command(name="daily", description="Imposta un messaggio giornaliero")
@app_commands.checks.has_permissions(administrator=True)
async def daily(interaction: discord.Interaction, *, message: str):
    await interaction.response.send_message("Messaggio giornaliero impostato.")
    while True:
        await interaction.channel.send(message)
        await asyncio.sleep(86400)  # 86400 secondi = 1 giorno

@bot.tree.command(name="play", description="Riproduce un file audio")
async def play(interaction: discord.Interaction, url: str):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        vc = await channel.connect()
        vc.play(discord.FFmpegPCMAudio(url))
        await interaction.response.send_message(f"In riproduzione: {url}")
    else:
        await interaction.response.send_message("Devi essere in un canale vocale per usare questo comando.")

@bot.tree.command(name="stop", description="Ferma la riproduzione audio")
async def stop(interaction: discord.Interaction):
    if interaction.voice_client:
        interaction.voice_client.stop()
        await interaction.voice_client.disconnect()
        await interaction.response.send_message("Riproduzione fermata.")
    else:
        await interaction.response.send_message("Nessun audio in riproduzione.")

@bot.tree.command(name="kickall", description="Espelle tutti gli utenti tranne gli amministratori")
@app_commands.checks.has_permissions(administrator=True)
async def kickall(interaction: discord.Interaction):
    for member in interaction.guild.members:
        if not any(role.permissions.administrator for role in member.roles):
            await member.kick()
            await interaction.channel.send(f"{member} è stato espulso.")
    await interaction.response.send_message("Tutti gli utenti non amministratori sono stati espulsi.")

@bot.tree.command(name="roleinfo", description="Mostra informazioni su un ruolo")
async def roleinfo(interaction: discord.Interaction, role: discord.Role):
    embed = discord.Embed(title=f"Informazioni su {role.name}", color=role.color)
    embed.add_field(name="ID", value=role.id, inline=False)
    embed.add_field(name="Creato il", value=role.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.add_field(name="Membri con questo ruolo", value=len(role.members), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="edit", description="Modifica il messaggio specificato")
@app_commands.checks.has_permissions(manage_messages=True)
async def edit(interaction: discord.Interaction, message_id: int, *, new_content: str):
    message = await interaction.channel.fetch_message(message_id)
    await message.edit(content=new_content)
    await interaction.response.send_message("Messaggio modificato.")

@bot.tree.command(name="invite", description="Crea un invito temporaneo")
async def invite(interaction: discord.Interaction, channel: discord.TextChannel, expires_in: int):
    invite = await channel.create_invite(max_age=expires_in)
    await interaction.response.send_message(f"Invito creato: {invite.url}")

@bot.tree.command(name="top", description="Mostra i top 5 membri con più messaggi")
async def top(interaction: discord.Interaction):
    messages_count = {}
    async for message in interaction.channel.history(limit=1000):
        if message.author not in messages_count:
            messages_count[message.author] = 0
        messages_count[message.author] += 1

    top_members = sorted(messages_count.items(), key=lambda x: x[1], reverse=True)[:5]
    embed = discord.Embed(title="Top 5 membri con più messaggi", color=0x00ff00)
    for member, count in top_members:
        embed.add_field(name=member.display_name, value=f"{count} messaggi", inline=False)
    
    await interaction.response.send_message(embed=embed)


@bot.event
async def on_member_join(member: discord.Member):
    role = discord.Object(id=ROLE_TO_REMOVE)
    await member.add_roles(role)

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # Controllo anti-raid
    if message.channel.id == TICKET_CHANNEL_ID:
        staff_role = discord.utils.get(message.guild.roles, id=STAFF_ROLE_ID)
        if staff_role and staff_role not in message.author.roles:
            await message.delete()
            log_channel = discord.utils.get(message.guild.text_channels, name='log')
            if log_channel:
                await log_channel.send(f'**ATTENZIONE**: Messaggio di {message.author.mention} bloccato nel canale {message.channel.mention}. Potenziale attacco di raid.')


bot.run(TOKEN)
