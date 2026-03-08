import discord
from discord.ext import commands
from typing import Dict


class HelpView(discord.ui.View):
    def __init__(self, embeds: Dict[str, discord.Embed]):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.message = None

    @discord.ui.button(label="Home", style=discord.ButtonStyle.secondary, row=0)
    async def home_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.embeds["main"], view=self)

    @discord.ui.button(label="Mod", style=discord.ButtonStyle.secondary, row=0)
    async def mod_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.embeds["Moderation"], view=self)

    @discord.ui.button(label="Fun", style=discord.ButtonStyle.secondary, row=0)
    async def fun_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.embeds["Fun"], view=self)

    @discord.ui.button(label="Game", style=discord.ButtonStyle.secondary, row=1)
    async def games_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.embeds["Games"], view=self)

    @discord.ui.button(label="Util", style=discord.ButtonStyle.secondary, row=1)
    async def util_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.embeds["Utility"], view=self)

    @discord.ui.button(label="Misc", style=discord.ButtonStyle.secondary, row=1)
    async def misc_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.embeds["Misc"], view=self)

    async def on_timeout(self):
        if self.message:
            for item in self.children:
                item.disabled = True
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cog_groups = {
            "Moderation": "Server management commands",
            "Fun": "Entertainment and interactive commands",
            "Utility": "Helpful utility commands",
            "Games": "Play games and earn JoyCoins",
            "Misc": "Additional useful commands"
        }
        self.related_cogs = {
            "Utility": ["Utility", "Webhooks", "Verification"],
        }

    def get_command_help_embed(self, command, ctx) -> discord.Embed:
        prefix = self.bot.prefixes.get(str(ctx.guild.id), "j!") if ctx.guild else "j!"
        embed = discord.Embed(
            title=f"♡ Command: {command.name}",
            color=self.bot.theme['secondary']
        )
        embed.add_field(
            name="Description",
            value=command.description or "No description available.",
            inline=False
        )
        params = []
        for key, value in command.params.items():
            if key not in ['self', 'ctx']:
                if value.default == value.empty:
                    params.append(f'<{key}>')
                else:
                    params.append(f'[{key}]')
        usage = ' '.join([f'{prefix}{command.name}'] + params)
        embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
        return embed

    def get_cog_help_embed(self, cog_name, ctx) -> discord.Embed:
        prefix = self.bot.prefixes.get(str(ctx.guild.id), "j!") if ctx.guild else "j!"
        embed = discord.Embed(
            title=f"♡ {cog_name} Commands",
            description=self.cog_groups.get(cog_name, "Various commands"),
            color=self.bot.theme['primary']
        )
        excluded = ['help', 'moderation', 'fun', 'utility', 'game', 'misc']
        cog_names = self.related_cogs.get(cog_name, [cog_name])
        for cn in cog_names:
            cog = self.bot.get_cog(cn)
            if not cog:
                continue
            for command in cog.get_commands():
                if command.checks:
                    is_owner = any(
                        check.__qualname__.startswith('is_owner')
                        for check in command.checks
                    )
                    if is_owner:
                        continue
                if command.name in excluded:
                    continue
                embed.add_field(
                    name=f"**{prefix}{command.name}**",
                    value=command.description or "No description available.",
                    inline=False
                )
        return embed

    @commands.hybrid_command(description="Show help information")
    async def help(self, ctx, category: str = None):
        prefix = self.bot.prefixes.get(str(ctx.guild.id), "j!") if ctx.guild else "j!"

        if category:
            cog_names = {k.lower(): k for k in self.cog_groups}
            if category.lower() in cog_names:
                real_name = cog_names[category.lower()]
                embed = self.get_cog_help_embed(real_name, ctx)
                await ctx.send(embed=embed)
                return

            command = self.bot.get_command(category)
            if command:
                embed = self.get_command_help_embed(command, ctx)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="♡ Error",
                    description=f"Command or category `{category}` not found!",
                    color=self.bot.theme['error']
                )
                await ctx.send(embed=embed)
            return

        help_embeds = {}
        main_embed = discord.Embed(
            title="♡ Joy's Help Menu",
            description="Welcome to Joy's help menu! Click the buttons below to view different command categories.",
            color=self.bot.theme['primary']
        )
        for cog_name, description in self.cog_groups.items():
            main_embed.add_field(name=cog_name, value=description, inline=False)
        main_embed.set_footer(
            text=f"Use {prefix}help <command> for detailed information about a specific command!")
        help_embeds["main"] = main_embed

        for cog_name in self.cog_groups:
            help_embeds[cog_name] = self.get_cog_help_embed(cog_name, ctx)

        view = HelpView(help_embeds)
        view.message = await ctx.send(embed=help_embeds["main"], view=view)

    @commands.hybrid_command(description="Show moderation commands")
    async def moderation(self, ctx):
        await self.help(ctx, "Moderation")

    @commands.hybrid_command(name="fun", description="Show fun commands")
    async def fun_cmd(self, ctx):
        await self.help(ctx, "Fun")

    @commands.hybrid_command(description="Show utility commands")
    async def utility(self, ctx):
        await self.help(ctx, "Utility")

    @commands.hybrid_command(description="Show misc commands")
    async def misc(self, ctx):
        await self.help(ctx, "Misc")


async def setup(bot):
    await bot.add_cog(Help(bot))
