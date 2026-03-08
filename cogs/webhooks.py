import discord
from discord.ext import commands
import aiohttp


class Webhooks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(invoke_without_command=True, fallback="info")
    @commands.has_permissions(manage_webhooks=True)
    async def webhook(self, ctx):
        prefix = self.bot.prefixes.get(str(ctx.guild.id), "j!") if ctx.guild else "j!"
        embed = discord.Embed(
            title="♡ Webhook Commands",
            description="Here are the available webhook commands:",
            color=self.bot.theme['primary']
        )
        embed.add_field(name=f"{prefix}webhook create <name>", value="Create a new webhook", inline=False)
        embed.add_field(name=f"{prefix}webhook connect <name>", value="Connect to an existing webhook", inline=False)
        embed.add_field(name=f"{prefix}webhook list", value="List all webhooks", inline=False)
        embed.add_field(name=f"{prefix}webhook select <name>", value="Select a webhook to use", inline=False)
        embed.add_field(name=f"{prefix}webhook send <title> | <message> | [color]", value="Send an embed through the selected webhook", inline=False)
        embed.add_field(name=f"{prefix}webhook delete", value="Delete the current webhook", inline=False)
        await ctx.send(embed=embed)

    @webhook.command(name="create", description="Create a new webhook")
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_create(self, ctx, name: str):
        try:
            wh = await ctx.channel.create_webhook(name=name)
            channel_id = str(ctx.channel.id)
            self.bot.webhook_data["webhooks"][channel_id] = {
                "id": str(wh.id), "token": wh.token, "name": wh.name
            }
            self.bot.webhook_data["selected"][channel_id] = str(wh.id)
            self.bot.save_webhooks()
            embed = discord.Embed(
                title="♡ Webhook Created",
                description=f"Successfully created webhook `{name}`!\nThis webhook has been automatically selected.",
                color=self.bot.theme['primary']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to create webhook: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @webhook.command(name="connect", description="Connect to an existing webhook")
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_connect(self, ctx, name: str):
        try:
            webhooks = await ctx.channel.webhooks()
            wh = discord.utils.get(webhooks, name=name)
            if not wh:
                embed = discord.Embed(title="♡ Error", description=f"No webhook found with name `{name}`!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            channel_id = str(ctx.channel.id)
            self.bot.webhook_data["webhooks"][channel_id] = {
                "id": str(wh.id), "token": wh.token, "name": wh.name
            }
            self.bot.webhook_data["selected"][channel_id] = str(wh.id)
            self.bot.save_webhooks()
            embed = discord.Embed(
                title="♡ Webhook Connected",
                description=f"Successfully connected to webhook `{name}`!",
                color=self.bot.theme['primary']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to connect: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @webhook.command(name="list", description="List all webhooks in this channel")
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_list(self, ctx):
        try:
            webhooks = await ctx.channel.webhooks()
            if not webhooks:
                embed = discord.Embed(title="♡ Webhooks", description="No webhooks found in this channel!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            embed = discord.Embed(title="♡ Available Webhooks", description="Webhooks in this channel:", color=self.bot.theme['primary'])
            channel_id = str(ctx.channel.id)
            selected_id = self.bot.webhook_data["selected"].get(channel_id)
            for wh in webhooks:
                is_selected = selected_id and str(wh.id) == selected_id
                name_display = f"**{wh.name}**" if is_selected else wh.name
                status = "Currently selected" if is_selected else f"Use `webhook connect {wh.name}` to connect"
                embed.add_field(name=name_display, value=status, inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to list webhooks: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @webhook.command(name="select", description="Select a webhook to use")
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_select(self, ctx, *, name: str):
        try:
            webhooks = await ctx.channel.webhooks()
            selected = None
            for wh in webhooks:
                if wh.name.lower() == name.lower():
                    selected = wh
                    break
            if not selected:
                embed = discord.Embed(title="♡ Error", description=f"No webhook found with name `{name}`!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            channel_id = str(ctx.channel.id)
            if channel_id not in self.bot.webhook_data["webhooks"]:
                self.bot.webhook_data["webhooks"][channel_id] = {
                    "id": str(selected.id), "token": selected.token, "name": selected.name
                }
            self.bot.webhook_data["selected"][channel_id] = str(selected.id)
            self.bot.save_webhooks()
            embed = discord.Embed(title="♡ Webhook Selected", description=f"Selected webhook `{selected.name}`!", color=self.bot.theme['primary'])
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to select webhook: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @webhook.command(name="delete", description="Delete the channel webhook")
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_delete(self, ctx):
        try:
            channel_id = str(ctx.channel.id)
            if channel_id not in self.bot.webhook_data["webhooks"]:
                embed = discord.Embed(title="♡ Error", description="No webhook found for this channel!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            try:
                wh_data = self.bot.webhook_data["webhooks"][channel_id]
                async with aiohttp.ClientSession() as session:
                    wh = discord.Webhook.from_url(
                        f"https://discord.com/api/webhooks/{wh_data['id']}/{wh_data['token']}",
                        session=session
                    )
                    await wh.delete()
            except (discord.NotFound, discord.HTTPException):
                pass
            del self.bot.webhook_data["webhooks"][channel_id]
            if channel_id in self.bot.webhook_data["selected"]:
                del self.bot.webhook_data["selected"][channel_id]
            self.bot.save_webhooks()
            embed = discord.Embed(title="♡ Webhook Deleted", description="Successfully deleted the webhook!", color=self.bot.theme['primary'])
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to delete webhook: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @webhook.command(name="send", description="Send an embed through the webhook")
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_send(self, ctx, *, content: str):
        try:
            channel_id = str(ctx.channel.id)
            if channel_id not in self.bot.webhook_data["webhooks"] or channel_id not in self.bot.webhook_data["selected"]:
                embed = discord.Embed(title="♡ Error", description="No webhook selected! Use `webhook list` to see available webhooks.", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            parts = [part.strip() for part in content.split("|")]
            if len(parts) < 2:
                embed = discord.Embed(title="♡ Error", description="Invalid format! Use: `webhook send Title | Message | #Color`\nColor is optional.", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            title = parts[0]
            message = parts[1].replace("\\n", "\n")
            color = int(parts[2].strip("#"), 16) if len(parts) > 2 else self.bot.theme['primary']
            wh_data = self.bot.webhook_data["webhooks"][channel_id]
            async with aiohttp.ClientSession() as session:
                wh = discord.Webhook.from_url(
                    f"https://discord.com/api/webhooks/{wh_data['id']}/{wh_data['token']}",
                    session=session
                )
                embed = discord.Embed(title=title, description=message, color=color)
                await wh.send(embed=embed, username=wh_data['name'])
        except ValueError as e:
            if "invalid literal for int() with base 16" in str(e):
                embed = discord.Embed(title="♡ Error", description="Invalid color format! Use hex (e.g., #FF0000)", color=self.bot.theme['error'])
            else:
                embed = discord.Embed(title="♡ Error", description=str(e), color=self.bot.theme['error'])
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="♡ Error", description=f"Failed to send: {e}", color=self.bot.theme['error'])
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Webhooks(bot))
