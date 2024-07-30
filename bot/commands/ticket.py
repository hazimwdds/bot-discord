import discord
from discord import app_commands
from discord.ext import commands
from bot.config import STAFF_ROLE_ID, TICKET_CHANNEL_ID

def setup(bot):
    @bot.tree.command(name="setup_ticket", description="Imposta il sistema di ticket nel canale corrente")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ticket(interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 | Ticket!",
            description="Seleziona una reazione per creare un ticket:\n"
                        "🛠️ - **Collaborazioni**\n"
                        "💰 - **Pagamenti**\n"
                        "🔒 - **Account**\n"
                        "🐞 - **Bug**\n"
                        "❓ - **Assistenza**",
            color=0x00ff00
        )
        message = await interaction.channel.send(embed=embed)

        reactions = ['🛠️', '💰', '🔒', '🐞', '❓']
        for reaction in reactions:
            await message.add_reaction(reaction)

        await interaction.response.send_message("Sistema di ticket impostato nel canale.")

    @bot.event
    async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
        if user.bot:
            return

        if reaction.message.channel.id != TICKET_CHANNEL_ID:
            return

        guild = reaction.message.guild
        member = guild.get_member(user.id)

        if reaction.emoji == '🛠️':
            category = 'Collaborazioni'
        elif reaction.emoji == '💰':
            category = 'Pagamenti'
        elif reaction.emoji == '🔒':
            category = 'Account'
        elif reaction.emoji == '🐞':
            category = 'Bug'
        elif reaction.emoji == '❓':
            category = 'Assistenza'
        else:
            return

        staff_role = guild.get_role(STAFF_ROLE_ID)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        category_channel = discord.utils.get(guild.categories, name="Support Tickets")
        if not category_channel:
            category_channel = await guild.create_category("Support Tickets")

        ticket_channel = await guild.create_text_channel(
            name=f"{category}-{member.name}",
            category=category_channel,
            overwrites=overwrites
        )

        await ticket_channel.send(f"{staff_role.mention} Nuovo ticket creato da {member.mention} per {category}.")
        await reaction.message.remove_reaction(reaction, user)
