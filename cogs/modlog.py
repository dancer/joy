import discord
from discord.ext import commands
from datetime import datetime, timezone
import json
import os


class Modlog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'data/modlog.json'
        self.data = self.load_data()

    def load_data(self):
        try:
            os.makedirs('data', exist_ok=True)
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}

    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception:
            pass

    async def log_action(self, guild, action, target, moderator, reason=None):
        guild_id = str(guild.id)
        if guild_id not in self.data:
            return
        channel = guild.get_channel(self.data[guild_id])
        if not channel:
            return
        embed = discord.Embed(
            title=f"♡ {action}",
            color=self.bot.theme['accent'],
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="Target", value=f"{target} ({target.id})", inline=True)
        embed.add_field(name="Moderator", value=f"{moderator} ({moderator.id})", inline=True)
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"ID: {target.id}")
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            pass

    @commands.hybrid_group(invoke_without_command=True, fallback="show")
    @commands.has_permissions(manage_guild=True)
    async def modlog(self, ctx):
        guild_id = str(ctx.guild.id)
        if guild_id not in self.data:
            embed = discord.Embed(
                title="♡ Mod Log",
                description="Mod logging is not configured.\nUse `modlog set <channel>` to enable.",
                color=self.bot.theme['primary']
            )
            await ctx.send(embed=embed)
            return
        channel = ctx.guild.get_channel(self.data[guild_id])
        embed = discord.Embed(
            title="♡ Mod Log",
            description=f"Logging to {channel.mention}" if channel else "Configured channel no longer exists.",
            color=self.bot.theme['primary']
        )
        await ctx.send(embed=embed)

    @modlog.command(name="set", description="Set the mod log channel")
    @commands.has_permissions(manage_guild=True)
    async def modlog_set(self, ctx, channel: discord.TextChannel):
        self.data[str(ctx.guild.id)] = channel.id
        self.save_data()
        embed = discord.Embed(
            title="♡ Mod Log Set",
            description=f"Mod actions will be logged to {channel.mention}.",
            color=self.bot.theme['primary']
        )
        await ctx.send(embed=embed)

    @modlog.command(name="disable", description="Disable mod logging")
    @commands.has_permissions(manage_guild=True)
    async def modlog_disable(self, ctx):
        guild_id = str(ctx.guild.id)
        if guild_id not in self.data:
            embed = discord.Embed(title="♡ Error", description="Mod logging is not enabled!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
            return
        del self.data[guild_id]
        self.save_data()
        embed = discord.Embed(title="♡ Mod Log Disabled", description="Mod logging has been disabled.", color=self.bot.theme['primary'])
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Modlog(bot))
