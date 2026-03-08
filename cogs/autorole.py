import discord
from discord.ext import commands
import json
import os


class Autorole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'data/autorole.json'
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

    @commands.hybrid_group(invoke_without_command=True, fallback="show")
    @commands.has_permissions(manage_roles=True)
    async def autorole(self, ctx):
        guild_id = str(ctx.guild.id)
        if guild_id not in self.data:
            embed = discord.Embed(
                title="♡ Auto Role",
                description="No auto role configured for this server.\nUse `autorole set <role>` to set one.",
                color=self.bot.theme['primary']
            )
            await ctx.send(embed=embed)
            return
        role = ctx.guild.get_role(self.data[guild_id])
        if not role:
            embed = discord.Embed(
                title="♡ Auto Role",
                description="The configured role no longer exists.\nUse `autorole set <role>` to set a new one.",
                color=self.bot.theme['error']
            )
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(
            title="♡ Auto Role",
            description=f"New members will receive {role.mention} on join.",
            color=self.bot.theme['primary']
        )
        await ctx.send(embed=embed)

    @autorole.command(name="set", description="Set the auto role for new members")
    @commands.has_permissions(manage_roles=True)
    async def autorole_set(self, ctx, role: discord.Role):
        self.data[str(ctx.guild.id)] = role.id
        self.save_data()
        embed = discord.Embed(
            title="♡ Auto Role Set",
            description=f"New members will now receive {role.mention} on join.",
            color=self.bot.theme['primary']
        )
        await ctx.send(embed=embed)

    @autorole.command(name="remove", description="Remove the auto role")
    @commands.has_permissions(manage_roles=True)
    async def autorole_remove(self, ctx):
        guild_id = str(ctx.guild.id)
        if guild_id not in self.data:
            embed = discord.Embed(title="♡ Error", description="No auto role is configured!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
            return
        del self.data[guild_id]
        self.save_data()
        embed = discord.Embed(title="♡ Auto Role Removed", description="Auto role has been disabled.", color=self.bot.theme['primary'])
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        if guild_id in self.data:
            role = member.guild.get_role(self.data[guild_id])
            if role:
                try:
                    await member.add_roles(role)
                except discord.HTTPException:
                    pass


async def setup(bot):
    await bot.add_cog(Autorole(bot))
