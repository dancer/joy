import discord
from discord.ext import commands
import platform
from datetime import datetime
import pyfiglet
import psutil
import asyncio


class ServerListView(discord.ui.View):
    def __init__(self, servers, per_page=10):
        super().__init__(timeout=60)
        self.servers = servers
        self.per_page = per_page
        self.current_page = 0
        self.total_pages = ((len(self.servers) - 1) // self.per_page) + 1
        self.message = None

    def get_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        current_servers = self.servers[start:end]
        embed = discord.Embed(
            title="♡ Server List",
            description="List of servers Joy is in",
            color=0xE6E6FA
        )
        for guild in current_servers:
            embed.add_field(
                name=guild.name,
                value=f"ID: {guild.id}\nMembers: {guild.member_count}",
                inline=False
            )
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}")
        return embed

    @discord.ui.button(label="<", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label=">", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    async def on_timeout(self):
        if self.message:
            for item in self.children:
                item.disabled = True
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Check bot latency")
    async def ping(self, ctx):
        embed = discord.Embed(
            title="♡ Pong!",
            description=f"Latency: {round(self.bot.latency * 1000)}ms",
            color=self.bot.theme['primary']
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Get server information")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(
            title=f"♡ {guild.name}'s Information",
            color=self.bot.theme['secondary']
        )
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Created On", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Member Count", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Get user information")
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(
            title=f"♡ {member.name}'s Information",
            color=self.bot.theme['accent']
        )
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Convert text to ASCII art")
    async def ascii(self, ctx, *, text: str):
        try:
            ascii_art = pyfiglet.figlet_format(text)
            if len(ascii_art) > 1994:
                embed = discord.Embed(title="♡ Error", description="The ASCII art is too long! Try shorter text.", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            await ctx.send(f"```{ascii_art}```")
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to create ASCII art: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Display information about Joy")
    async def botinfo(self, ctx):
        try:
            try:
                if self.bot.owner_id:
                    bot_owner = await self.bot.fetch_user(self.bot.owner_id)
                    owner_text = f"Built with ♡ by {bot_owner.name}"
                else:
                    owner_text = "Built with ♡"
            except discord.HTTPException:
                owner_text = "Built with ♡"
            embed = discord.Embed(
                title="♡ About Joy",
                description="A cheerful Discord bot designed to spread joy and help manage your server!",
                color=self.bot.theme['primary']
            )
            embed.add_field(name="Creator", value=owner_text, inline=True)
            embed.add_field(name="Created On", value=discord.utils.format_dt(self.bot.user.created_at, style='D'), inline=True)
            embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
            embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
            embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)
            embed.add_field(name="Commands", value=str(len(self.bot.commands)), inline=True)
            if self.bot.user.avatar:
                embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.add_field(
                name="GitHub",
                value="[github.com/dancer/joy](https://github.com/dancer/joy)",
                inline=True
            )
            embed.set_footer(
                text="Thank you for using Joy! ♡",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"An error occurred: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="bot", description="View detailed bot statistics")
    @commands.is_owner()
    async def botstats(self, ctx):
        try:
            total_members = sum(guild.member_count for guild in self.bot.guilds)
            total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024
            total_commands = len(self.bot.commands)
            hidden_commands = len([cmd for cmd in self.bot.commands if cmd.hidden])
            uptime = datetime.now() - self.bot.launch_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            embed = discord.Embed(
                title="♡ Bot Statistics",
                description="Detailed information about Joy",
                color=self.bot.theme['primary']
            )
            embed.add_field(name="Server Stats", value=f"Servers: {len(self.bot.guilds)}\nTotal Members: {total_members}\nTotal Channels: {total_channels}", inline=False)
            embed.add_field(name="Command Stats", value=f"Total Commands: {total_commands}\nHidden Commands: {hidden_commands}", inline=False)
            embed.add_field(name="System Stats", value=f"Memory Usage: {memory_usage:.2f} MB\nPython Version: {platform.python_version()}\nDiscord.py Version: {discord.__version__}", inline=False)
            embed.add_field(name="Uptime", value=f"{days}d {hours}h {minutes}m {seconds}s", inline=False)
            embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"An error occurred: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Submit a feature request")
    async def feature(self, ctx, *, message: str):
        uses_left, time_left = self.bot.get_remaining_uses("feature", ctx.author.id)
        if uses_left <= 0:
            hours, remainder = divmod(int(time_left), 3600)
            minutes, seconds = divmod(remainder, 60)
            timeformat = []
            if hours > 0:
                timeformat.append(f"{hours} hours")
            if minutes > 0:
                timeformat.append(f"{minutes} minutes")
            if seconds > 0:
                timeformat.append(f"{seconds} seconds")
            embed = discord.Embed(
                title="♡ Slow Down",
                description=f"You can only send 3 feature requests per day!\nPlease try again in {', '.join(timeformat)}.",
                color=self.bot.theme['error']
            )
            await ctx.send(embed=embed)
            return
        try:
            owner = await self.bot.fetch_user(self.bot.owner_id)
            if not owner:
                embed = discord.Embed(title="♡ Error", description="Could not find the bot owner.", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            feature_embed = discord.Embed(
                title="♡ New Feature Request",
                description=message,
                color=self.bot.theme['accent']
            )
            feature_embed.set_footer(text=f"Sent by {ctx.author} (ID: {ctx.author.id})")
            try:
                await owner.send(embed=feature_embed)
                self.bot.update_cooldown("feature", ctx.author.id)
                confirm_embed = discord.Embed(
                    title="♡ Feature Request Sent",
                    description=f"Your feature request has been sent!\nYou have {uses_left - 1} requests remaining today.",
                    color=self.bot.theme['primary']
                )
                await ctx.send(embed=confirm_embed)
            except discord.Forbidden:
                embed = discord.Embed(title="♡ Error", description="Could not send the feature request.", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"An error occurred: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="List all servers the bot is in")
    @commands.is_owner()
    async def servers(self, ctx):
        try:
            all_servers = sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=True)
            if not all_servers:
                embed = discord.Embed(title="♡ Server List", description="I'm not in any servers yet!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            view = ServerListView(all_servers)
            view.message = await ctx.send(embed=view.get_embed(), view=view)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"An error occurred: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Clear bot messages in DMs")
    @commands.is_owner()
    async def cc(self, ctx, amount: int = None):
        if not isinstance(ctx.channel, discord.DMChannel):
            embed = discord.Embed(title="♡ Error", description="This command can only be used in DMs!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
            return
        try:
            if amount is None:
                amount = 100
            amount = min(amount, 100)
            messages = []
            async for msg in ctx.channel.history(limit=100):
                if len(messages) >= amount:
                    break
                if msg.author == self.bot.user:
                    messages.append(msg)
            for msg in messages:
                await msg.delete()
            embed = discord.Embed(title="♡ Messages Cleared", description=f"Deleted {len(messages)} messages!", color=self.bot.theme['primary'])
            confirm_msg = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await confirm_msg.delete()
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to clear messages: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))
