import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mute", help="Muta un utente")
    @commands.has_permissions(mute_members=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        await member.edit(mute=True)
        await ctx.send(f"{member.mention} è stato mutato. Motivo: {reason}")

    @commands.command(name="unmute", help="Smutta un utente")
    @commands.has_permissions(mute_members=True)
    async def unmute(self, ctx, member: discord.Member):
        await member.edit(mute=False)
        await ctx.send(f"{member.mention} è stato smutato.")

    @commands.command(name="warn", help="Avvisa un utente")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        await ctx.send(f"{member.mention} è stato avvisato. Motivo: {reason}")

    @commands.command(name="slowmode", help="Imposta la modalità lenta su un canale")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Modalità lenta impostata su {seconds} secondi.")

    @commands.command(name="lock", help="Blocca un canale")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("Il canale è stato bloccato.")

    @commands.command(name="unlock", help="Sblocca un canale")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("Il canale è stato sbloccato.")

def setup(bot):
    bot.add_cog(Moderation(bot))
