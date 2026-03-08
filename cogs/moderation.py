import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import json
import os


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lockdown_status = {}
        self.prefix_file = 'data/prefixes.json'
        self.load_prefixes()

    def load_prefixes(self):
        try:
            os.makedirs('data', exist_ok=True)
            if os.path.exists(self.prefix_file):
                with open(self.prefix_file, 'r') as f:
                    self.bot.prefixes = json.load(f)
            else:
                self.bot.prefixes = {}
                self.save_prefixes()
        except Exception:
            self.bot.prefixes = {}

    def save_prefixes(self):
        try:
            with open(self.prefix_file, 'w') as f:
                json.dump(self.bot.prefixes, f, indent=4)
        except Exception:
            pass

    async def log(self, guild, action, target, moderator, reason=None):
        modlog = self.bot.get_cog('Modlog')
        if modlog:
            await modlog.log_action(guild, action, target, moderator, reason)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        if self.lockdown_status.get(invite.guild.id, False):
            try:
                await invite.delete(reason="Server is in lockdown mode")
            except Exception:
                pass

    @commands.hybrid_command(description="Clear messages from a channel")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        embed = discord.Embed(title="♡ Messages Cleared", description=f"Cleared {amount} messages", color=self.bot.theme['primary'])
        await ctx.send(embed=embed, delete_after=5)

    @commands.hybrid_command(description="Kick a member from the server")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        embed = discord.Embed(
            title="♡ Member Kicked",
            description=f"{member.mention} has been kicked\nReason: {reason}",
            color=self.bot.theme['accent']
        )
        embed.set_footer(text=f"Kicked by {ctx.author}")
        await member.kick(reason=reason)
        await ctx.send(embed=embed)
        await self.log(ctx.guild, "Member Kicked", member, ctx.author, reason)

    @commands.hybrid_command(description="Ban a member from the server")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        embed = discord.Embed(
            title="♡ Member Banned",
            description=f"{member.mention} has been banned\nReason: {reason}",
            color=self.bot.theme['accent']
        )
        embed.set_footer(text=f"Banned by {ctx.author}")
        await member.ban(reason=reason)
        await ctx.send(embed=embed)
        await self.log(ctx.guild, "Member Banned", member, ctx.author, reason)

    @commands.hybrid_command(description="Unban a user by ID")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason="No reason provided"):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
            embed = discord.Embed(
                title="♡ Member Unbanned",
                description=f"{user.mention} has been unbanned\nReason: {reason}",
                color=self.bot.theme['accent']
            )
            embed.set_footer(text=f"Unbanned by {ctx.author}")
            await ctx.send(embed=embed)
            await self.log(ctx.guild, "Member Unbanned", user, ctx.author, reason)
        except discord.NotFound:
            embed = discord.Embed(title="♡ Error", description="User not found!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to unban: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Mute a member for a duration in minutes")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: int, *, reason: str = None):
        try:
            if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
                embed = discord.Embed(title="♡ Error", description="You cannot mute someone with a higher or equal role!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            if duration <= 0:
                embed = discord.Embed(title="♡ Error", description="Duration must be greater than 0!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            mute_end = datetime.now(timezone.utc) + timedelta(minutes=duration)
            await member.timeout(mute_end, reason=f"Muted by {ctx.author}: {reason}" if reason else f"Muted by {ctx.author}")
            embed = discord.Embed(
                title="♡ Member Muted",
                description=f"{member.mention} has been muted for {duration} minutes.",
                color=self.bot.theme['accent']
            )
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Expires", value=f"<t:{int(mute_end.timestamp())}:R>", inline=False)
            embed.set_footer(text=f"Muted by {ctx.author}")
            await ctx.send(embed=embed)
            await self.log(ctx.guild, "Member Muted", member, ctx.author, reason)
        except discord.Forbidden:
            embed = discord.Embed(title="♡ Error", description="I don't have permission to mute this member!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to mute: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Unmute a member")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = None):
        try:
            if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
                embed = discord.Embed(title="♡ Error", description="You cannot unmute someone with a higher or equal role!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            if not member.is_timed_out():
                embed = discord.Embed(title="♡ Error", description=f"{member.mention} is not muted!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            await member.timeout(None, reason=f"Unmuted by {ctx.author}: {reason}" if reason else f"Unmuted by {ctx.author}")
            embed = discord.Embed(title="♡ Member Unmuted", description=f"{member.mention} has been unmuted.", color=self.bot.theme['accent'])
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Unmuted by {ctx.author}")
            await ctx.send(embed=embed)
            await self.log(ctx.guild, "Member Unmuted", member, ctx.author, reason)
        except discord.Forbidden:
            embed = discord.Embed(title="♡ Error", description="I don't have permission to unmute this member!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to unmute: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Set channel slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        try:
            if seconds < 0 or seconds > 21600:
                embed = discord.Embed(title="♡ Error", description="Slowmode must be between 0 and 21600 seconds!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            await ctx.channel.edit(slowmode_delay=seconds)
            description = "Slowmode has been disabled!" if seconds == 0 else f"Slowmode set to {seconds} seconds!"
            embed = discord.Embed(title="♡ Slowmode Updated", description=description, color=self.bot.theme['primary'])
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to set slowmode: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Lock a channel")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            embed = discord.Embed(title="♡ Channel Locked", description=f"{channel.mention} has been locked!", color=self.bot.theme['accent'])
            embed.set_footer(text=f"Locked by {ctx.author}")
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to lock channel: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Unlock a channel")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=None)
            embed = discord.Embed(title="♡ Channel Unlocked", description=f"{channel.mention} has been unlocked!", color=self.bot.theme['accent'])
            embed.set_footer(text=f"Unlocked by {ctx.author}")
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to unlock channel: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Warn a member")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        try:
            if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
                embed = discord.Embed(title="♡ Error", description="You cannot warn someone with a higher or equal role!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            embed = discord.Embed(
                title="♡ Member Warned",
                description=f"{member.mention} has been warned\nReason: {reason}",
                color=self.bot.theme['accent']
            )
            embed.set_footer(text=f"Warned by {ctx.author}")
            await ctx.send(embed=embed)
            try:
                warn_dm = discord.Embed(
                    title="♡ Warning Received",
                    description=f"You have been warned in {ctx.guild.name}\nReason: {reason}",
                    color=self.bot.theme['accent']
                )
                await member.send(embed=warn_dm)
            except discord.Forbidden:
                pass
            await self.log(ctx.guild, "Member Warned", member, ctx.author, reason)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to warn: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Add or remove a role from a member")
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member, *, role: discord.Role):
        try:
            if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
                embed = discord.Embed(title="♡ Error", description="You can't manage roles higher than your highest role!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            if role in member.roles:
                await member.remove_roles(role)
                action = "removed from"
            else:
                await member.add_roles(role)
                action = "added to"
            embed = discord.Embed(
                title="♡ Role Updated",
                description=f"Role {role.mention} has been {action} {member.mention}",
                color=self.bot.theme['primary']
            )
            embed.set_footer(text=f"Updated by {ctx.author}")
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to update role: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Toggle server lockdown")
    @commands.has_permissions(manage_guild=True)
    async def lockdown(self, ctx):
        try:
            guild = ctx.guild
            is_locked = self.lockdown_status.get(guild.id, False)
            if not is_locked:
                invites = await guild.invites()
                deleted_count = 0
                for invite in invites:
                    try:
                        await invite.delete(reason=f"Server lockdown by {ctx.author}")
                        deleted_count += 1
                    except Exception:
                        continue
                self.lockdown_status[guild.id] = True
                embed = discord.Embed(
                    title="♡ Server Lockdown Enabled",
                    description=f"Deleted {deleted_count} existing invites.\nNew invites will be automatically deleted.",
                    color=self.bot.theme['error']
                )
                embed.set_footer(text=f"Locked down by {ctx.author}")
            else:
                self.lockdown_status[guild.id] = False
                embed = discord.Embed(
                    title="♡ Server Lockdown Disabled",
                    description="Server invites can be created again!",
                    color=self.bot.theme['primary']
                )
                embed.set_footer(text=f"Lockdown lifted by {ctx.author}")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(title="♡ Error", description="I don't have permission to manage invites!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to toggle lockdown: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Send a message through the bot")
    @commands.has_permissions(administrator=True)
    async def msg(self, ctx, *, message: str):
        try:
            if ctx.interaction is None:
                await ctx.message.delete()
            message = message.replace("\\n", "\n")
            await ctx.channel.send(message)
            if ctx.interaction:
                await ctx.send("Message sent!", ephemeral=True)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to send message: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="View or change server prefix")
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, new_prefix: str = None):
        if new_prefix is None:
            current_prefix = self.bot.prefixes.get(str(ctx.guild.id), "j!")
            embed = discord.Embed(title="♡ Current Prefix", description=f"The current prefix is `{current_prefix}`", color=self.bot.theme['primary'])
            await ctx.send(embed=embed)
            return
        try:
            if len(new_prefix) > 5:
                embed = discord.Embed(title="♡ Error", description="Prefix cannot be longer than 5 characters!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            self.bot.prefixes[str(ctx.guild.id)] = new_prefix
            self.save_prefixes()
            embed = discord.Embed(
                title="♡ Prefix Updated",
                description=f"Server prefix has been changed to `{new_prefix}`\nExample: `{new_prefix}help`",
                color=self.bot.theme['primary']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to update prefix: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
