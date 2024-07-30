import discord
from discord import app_commands
from discord.ext import commands
from utils import generate_unique_id, report_data, suggestion_data
from config import REPORT_CHANNEL_ID, SUGGESTION_CHANNEL_ID

def config(bot):
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
