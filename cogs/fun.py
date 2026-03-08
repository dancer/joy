import discord
from discord.ext import commands
import random


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hearts = ['♡', '♥']
        self.positive_messages = [
            "You're amazing!",
            "Keep spreading joy!",
            "Your smile brightens everyone's day!",
            "You make the world a better place!",
            "Stay wonderful!",
            "You're doing great!"
        ]

    @commands.hybrid_command(description="Give someone a virtual hug")
    async def hug(self, ctx, member: discord.Member):
        heart = random.choice(self.hearts)
        embed = discord.Embed(
            title=f"{heart} Virtual Hug!",
            description=f"{ctx.author.mention} gave {member.mention} a big warm hug!",
            color=self.bot.theme['accent']
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Get an inspiring message")
    async def inspire(self, ctx):
        message = random.choice(self.positive_messages)
        heart = random.choice(self.hearts)
        embed = discord.Embed(
            title=f"{heart} Your Daily Dose of Joy",
            description=message,
            color=self.bot.theme['primary']
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Roll a dice")
    async def roll(self, ctx, sides: int = 6):
        result = random.randint(1, sides)
        embed = discord.Embed(
            title="♡ Dice Roll",
            description=f"You rolled a {result} (1-{sides})!",
            color=self.bot.theme['secondary']
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Choose between multiple options")
    async def choose(self, ctx, *, choices: str):
        options = [option.strip() for option in choices.split(',')]
        if len(options) < 2:
            embed = discord.Embed(
                title="♡ Error",
                description="Please provide at least 2 options separated by commas!",
                color=self.bot.theme['error']
            )
        else:
            choice = random.choice(options)
            embed = discord.Embed(
                title="♡ I Choose...",
                description=f"I pick: **{choice}**!",
                color=self.bot.theme['accent']
            )
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Get information about supporting Joy")
    async def donate(self, ctx):
        embed = discord.Embed(
            title="♡ Support Joy",
            description="We aren't accepting donations at the moment, but you can support Joy by spreading the word and adding the bot owner on Discord!",
            color=self.bot.theme['primary']
        )
        embed.add_field(
            name="Contact the Owner",
            value="Add Truthless on Discord: <@1334895494832590870>",
            inline=False
        )
        embed.add_field(
            name="Other Ways to Support",
            value="Invite Joy to your servers\nShare feedback and suggestions\nReport bugs to help improve Joy\nSpread the word about Joy to others!",
            inline=False
        )
        embed.set_footer(text="Thank you for your interest in supporting Joy! ♡")
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Report a bug to the bot owner")
    async def bug(self, ctx, *, bug_report: str):
        uses_left, time_left = self.bot.get_remaining_uses("bug", ctx.author.id)
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
                description=f"You can only send 3 bug reports per day!\nPlease try again in {', '.join(timeformat)}.",
                color=self.bot.theme['error']
            )
            await ctx.send(embed=embed)
            return
        try:
            owner = await self.bot.fetch_user(1334895494832590870)
            if not owner:
                embed = discord.Embed(title="♡ Error", description="Could not find the bot owner.", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            bug_embed = discord.Embed(
                title="♡ New Bug Report",
                description=bug_report,
                color=self.bot.theme['error']
            )
            bug_embed.add_field(name="Reporter", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            if ctx.guild:
                bug_embed.add_field(name="Server", value=f"{ctx.guild.name} ({ctx.guild.id})", inline=True)
                bug_embed.add_field(name="Channel", value=f"#{ctx.channel.name} ({ctx.channel.id})", inline=True)
            try:
                await owner.send(embed=bug_embed)
                self.bot.update_cooldown("bug", ctx.author.id)
                confirm_embed = discord.Embed(
                    title="♡ Bug Report Sent",
                    description=f"Your bug report has been sent!\nYou have {uses_left - 1} bug reports remaining today.",
                    color=self.bot.theme['primary']
                )
                await ctx.send(embed=confirm_embed)
            except discord.Forbidden:
                embed = discord.Embed(title="♡ Error", description="Could not send the bug report.", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"An error occurred: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Fun(bot))
