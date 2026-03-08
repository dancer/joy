import discord
from discord.ext import commands
import json
import os
import asyncio


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'data/reaction_roles.json'
        self.text_verify_file = 'data/text_verify.json'
        self.reaction_roles = {}
        self.text_verifications = {}
        self.load_reaction_roles()
        self.load_text_verifications()

    def load_reaction_roles(self):
        try:
            os.makedirs('data', exist_ok=True)
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.reaction_roles = {int(k): v for k, v in data.items()}
            else:
                self.reaction_roles = {}
        except Exception:
            self.reaction_roles = {}

    def save_reaction_roles(self):
        try:
            os.makedirs('data', exist_ok=True)
            with open(self.data_file, 'w') as f:
                data = {str(k): v for k, v in self.reaction_roles.items()}
                json.dump(data, f, indent=4)
        except Exception:
            pass

    def load_text_verifications(self):
        try:
            os.makedirs('data', exist_ok=True)
            if os.path.exists(self.text_verify_file):
                with open(self.text_verify_file, 'r') as f:
                    self.text_verifications = json.load(f)
            else:
                self.text_verifications = {}
                self.save_text_verifications()
        except Exception:
            self.text_verifications = {}

    def save_text_verifications(self):
        try:
            with open(self.text_verify_file, 'w') as f:
                json.dump(self.text_verifications, f, indent=4)
        except Exception:
            pass

    @commands.hybrid_command(description="Set up reaction role verification")
    @commands.has_permissions(manage_roles=True)
    async def verify(self, ctx, message_id: str, role: str, emoji: str):
        try:
            try:
                message = await ctx.channel.fetch_message(int(message_id))
            except (discord.NotFound, ValueError):
                embed = discord.Embed(title="♡ Error", description="Message not found! Use this command in the same channel as the message.", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            try:
                if role.isdigit():
                    target_role = ctx.guild.get_role(int(role))
                else:
                    target_role = discord.utils.get(ctx.guild.roles, name=role)
                if not target_role:
                    raise ValueError()
            except ValueError:
                embed = discord.Embed(title="♡ Error", description="Role not found! Use the role name or ID.", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            try:
                await message.add_reaction(emoji)
            except discord.HTTPException:
                embed = discord.Embed(title="♡ Error", description="Invalid emoji!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            if message.id not in self.reaction_roles:
                self.reaction_roles[message.id] = {}
            self.reaction_roles[message.id][emoji] = target_role.id
            self.save_reaction_roles()
            embed = discord.Embed(
                title="♡ Verification Setup",
                description=f"Successfully set up verification!\n\nMessage: {message.jump_url}\nRole: {target_role.mention}\nEmoji: {emoji}",
                color=self.bot.theme['primary']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to set up verification: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="List active reaction role verifications")
    @commands.has_permissions(manage_roles=True)
    async def verifylist(self, ctx):
        if not self.reaction_roles:
            embed = discord.Embed(title="♡ Verification List", description="No active verification roles set up.", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title="♡ Active Verifications", color=self.bot.theme['primary'])
        for message_id, reactions in self.reaction_roles.items():
            try:
                message = None
                for channel in ctx.guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        try:
                            message = await channel.fetch_message(message_id)
                            break
                        except discord.NotFound:
                            continue
                if message:
                    for em, role_id in reactions.items():
                        role = ctx.guild.get_role(role_id)
                        if role:
                            embed.add_field(
                                name=f"Message: {message.jump_url}",
                                value=f"Emoji: {em}\nRole: {role.mention}",
                                inline=False
                            )
            except Exception:
                continue
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Remove a verification setup")
    @commands.has_permissions(manage_roles=True)
    async def verifyremove(self, ctx, message_id: str):
        try:
            msg_id = int(message_id)
            if msg_id not in self.reaction_roles:
                embed = discord.Embed(title="♡ Error", description="No verification setup found for this message!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            try:
                message = await ctx.channel.fetch_message(msg_id)
                await message.clear_reactions()
            except discord.NotFound:
                pass
            del self.reaction_roles[msg_id]
            self.save_reaction_roles()
            embed = discord.Embed(title="♡ Verification Removed", description="Successfully removed the verification setup!", color=self.bot.theme['primary'])
            await ctx.send(embed=embed)
        except ValueError:
            embed = discord.Embed(title="♡ Error", description="Invalid message ID!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to remove verification: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Set up text-based verification")
    @commands.has_permissions(manage_roles=True)
    async def textverify(self, ctx, word: str, role: str):
        try:
            try:
                if role.isdigit():
                    target_role = ctx.guild.get_role(int(role))
                else:
                    target_role = discord.utils.get(ctx.guild.roles, name=role)
                if not target_role:
                    raise ValueError()
            except ValueError:
                embed = discord.Embed(title="♡ Error", description="Role not found! Use the role name or ID.", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            channel_id = str(ctx.channel.id)
            self.text_verifications[channel_id] = {
                "word": word,
                "role_id": target_role.id
            }
            self.save_text_verifications()
            embed = discord.Embed(
                title="♡ Verification",
                description=f"Type `{word}` to verify and receive the {target_role.mention} role!",
                color=self.bot.theme['primary']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to set up text verification: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in self.reaction_roles:
            if str(payload.emoji) in self.reaction_roles[payload.message_id]:
                guild = self.bot.get_guild(payload.guild_id)
                if not guild:
                    return
                role_id = self.reaction_roles[payload.message_id][str(payload.emoji)]
                role = guild.get_role(role_id)
                if not role:
                    return
                member = guild.get_member(payload.user_id)
                if not member or member.bot:
                    return
                try:
                    await member.add_roles(role)
                except discord.HTTPException:
                    pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id in self.reaction_roles:
            if str(payload.emoji) in self.reaction_roles[payload.message_id]:
                guild = self.bot.get_guild(payload.guild_id)
                if not guild:
                    return
                role_id = self.reaction_roles[payload.message_id][str(payload.emoji)]
                role = guild.get_role(role_id)
                if not role:
                    return
                member = guild.get_member(payload.user_id)
                if not member or member.bot:
                    return
                try:
                    await member.remove_roles(role)
                except discord.HTTPException:
                    pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        channel_id = str(message.channel.id)
        if channel_id in self.text_verifications:
            verify_data = self.text_verifications[channel_id]
            if message.content.lower() == verify_data["word"].lower():
                try:
                    await message.delete()
                    role = message.guild.get_role(verify_data["role_id"])
                    if role:
                        await message.author.add_roles(role)
                        embed = discord.Embed(
                            title="♡ Verified!",
                            description=f"{message.author.mention} has been verified and received the {role.mention} role!",
                            color=self.bot.theme['primary']
                        )
                        success_msg = await message.channel.send(embed=embed)
                        await asyncio.sleep(5)
                        await success_msg.delete()
                except discord.Forbidden:
                    embed = discord.Embed(title="♡ Error", description="I don't have permission to manage roles!", color=self.bot.theme['error'])
                    await message.channel.send(embed=embed)
                except Exception as e:
                    embed = discord.Embed(title="♡ Error", description=f"Failed to verify user: {e}", color=self.bot.theme['error'])
                    await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Verification(bot))
