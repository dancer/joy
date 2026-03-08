import discord
from discord.ext import commands
import json
import os


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'data/welcome.json'
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

    def get_guild_data(self, guild_id):
        gid = str(guild_id)
        if gid not in self.data:
            self.data[gid] = {"welcome": {}, "leave": {}}
        return self.data[gid]

    def format_message(self, template, member):
        return template.replace("{user}", member.mention).replace("{server}", member.guild.name).replace("{name}", member.name)

    @commands.hybrid_group(invoke_without_command=True, fallback="show")
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx):
        guild_data = self.get_guild_data(ctx.guild.id)
        config = guild_data.get("welcome", {})
        if not config.get("channel_id"):
            embed = discord.Embed(
                title="♡ Welcome Messages",
                description="Welcome messages are not configured.\nUse `welcome channel <channel>` and `welcome message <text>` to set up.",
                color=self.bot.theme['primary']
            )
            await ctx.send(embed=embed)
            return
        channel = ctx.guild.get_channel(config["channel_id"])
        embed = discord.Embed(
            title="♡ Welcome Messages",
            color=self.bot.theme['primary']
        )
        embed.add_field(name="Channel", value=channel.mention if channel else "Channel not found", inline=False)
        embed.add_field(name="Message", value=config.get("message", "Not set"), inline=False)
        embed.set_footer(text="Placeholders: {user} {server} {name}")
        await ctx.send(embed=embed)

    @welcome.command(name="channel", description="Set the welcome message channel")
    @commands.has_permissions(manage_guild=True)
    async def welcome_channel(self, ctx, channel: discord.TextChannel):
        guild_data = self.get_guild_data(ctx.guild.id)
        if "welcome" not in guild_data:
            guild_data["welcome"] = {}
        guild_data["welcome"]["channel_id"] = channel.id
        self.save_data()
        embed = discord.Embed(title="♡ Welcome Channel Set", description=f"Welcome messages will be sent to {channel.mention}.", color=self.bot.theme['primary'])
        await ctx.send(embed=embed)

    @welcome.command(name="message", description="Set the welcome message text")
    @commands.has_permissions(manage_guild=True)
    async def welcome_message(self, ctx, *, text: str):
        guild_data = self.get_guild_data(ctx.guild.id)
        if "welcome" not in guild_data:
            guild_data["welcome"] = {}
        guild_data["welcome"]["message"] = text
        self.save_data()
        embed = discord.Embed(title="♡ Welcome Message Set", description=f"Message: {text}", color=self.bot.theme['primary'])
        embed.set_footer(text="Placeholders: {user} {server} {name}")
        await ctx.send(embed=embed)

    @welcome.command(name="disable", description="Disable welcome messages")
    @commands.has_permissions(manage_guild=True)
    async def welcome_disable(self, ctx):
        guild_data = self.get_guild_data(ctx.guild.id)
        guild_data["welcome"] = {}
        self.save_data()
        embed = discord.Embed(title="♡ Welcome Disabled", description="Welcome messages have been disabled.", color=self.bot.theme['primary'])
        await ctx.send(embed=embed)

    @commands.hybrid_group(invoke_without_command=True, fallback="show")
    @commands.has_permissions(manage_guild=True)
    async def leave(self, ctx):
        guild_data = self.get_guild_data(ctx.guild.id)
        config = guild_data.get("leave", {})
        if not config.get("channel_id"):
            embed = discord.Embed(
                title="♡ Leave Messages",
                description="Leave messages are not configured.\nUse `leave channel <channel>` and `leave message <text>` to set up.",
                color=self.bot.theme['primary']
            )
            await ctx.send(embed=embed)
            return
        channel = ctx.guild.get_channel(config["channel_id"])
        embed = discord.Embed(
            title="♡ Leave Messages",
            color=self.bot.theme['primary']
        )
        embed.add_field(name="Channel", value=channel.mention if channel else "Channel not found", inline=False)
        embed.add_field(name="Message", value=config.get("message", "Not set"), inline=False)
        embed.set_footer(text="Placeholders: {user} {server} {name}")
        await ctx.send(embed=embed)

    @leave.command(name="channel", description="Set the leave message channel")
    @commands.has_permissions(manage_guild=True)
    async def leave_channel(self, ctx, channel: discord.TextChannel):
        guild_data = self.get_guild_data(ctx.guild.id)
        if "leave" not in guild_data:
            guild_data["leave"] = {}
        guild_data["leave"]["channel_id"] = channel.id
        self.save_data()
        embed = discord.Embed(title="♡ Leave Channel Set", description=f"Leave messages will be sent to {channel.mention}.", color=self.bot.theme['primary'])
        await ctx.send(embed=embed)

    @leave.command(name="message", description="Set the leave message text")
    @commands.has_permissions(manage_guild=True)
    async def leave_message(self, ctx, *, text: str):
        guild_data = self.get_guild_data(ctx.guild.id)
        if "leave" not in guild_data:
            guild_data["leave"] = {}
        guild_data["leave"]["message"] = text
        self.save_data()
        embed = discord.Embed(title="♡ Leave Message Set", description=f"Message: {text}", color=self.bot.theme['primary'])
        embed.set_footer(text="Placeholders: {user} {server} {name}")
        await ctx.send(embed=embed)

    @leave.command(name="disable", description="Disable leave messages")
    @commands.has_permissions(manage_guild=True)
    async def leave_disable(self, ctx):
        guild_data = self.get_guild_data(ctx.guild.id)
        guild_data["leave"] = {}
        self.save_data()
        embed = discord.Embed(title="♡ Leave Disabled", description="Leave messages have been disabled.", color=self.bot.theme['primary'])
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_data = self.get_guild_data(member.guild.id)
        config = guild_data.get("welcome", {})
        if config.get("channel_id") and config.get("message"):
            channel = member.guild.get_channel(config["channel_id"])
            if channel:
                try:
                    text = self.format_message(config["message"], member)
                    embed = discord.Embed(description=text, color=self.bot.theme['primary'])
                    await channel.send(embed=embed)
                except discord.HTTPException:
                    pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_data = self.get_guild_data(member.guild.id)
        config = guild_data.get("leave", {})
        if config.get("channel_id") and config.get("message"):
            channel = member.guild.get_channel(config["channel_id"])
            if channel:
                try:
                    text = self.format_message(config["message"], member)
                    embed = discord.Embed(description=text, color=self.bot.theme['primary'])
                    await channel.send(embed=embed)
                except discord.HTTPException:
                    pass


async def setup(bot):
    await bot.add_cog(Welcome(bot))
