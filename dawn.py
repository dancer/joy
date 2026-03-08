import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timezone
import sys
import json

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('joy.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


def get_prefix(bot, message):
    if message.guild is None:
        return "j!"
    return bot.prefixes.get(str(message.guild.id), "j!")


class JoyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.reactions = True

        os.makedirs('data', exist_ok=True)
        self.webhooks_file = 'data/webhooks.json'
        self.cooldowns_file = 'data/cooldowns.json'
        self.load_webhooks()
        self.load_cooldowns()

        self.prefixes = {}

        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="spreading joy ♡"
            ),
            status=discord.Status.idle
        )

        self.owner_id = int(os.getenv('OWNER_ID', '0'))
        self.remove_command('help')

        self.theme = {
            'primary': 0xFFFFFF,
            'secondary': 0xFAFAFA,
            'accent': 0xE6E6FA,
            'error': 0xFFE4E1
        }

        self.launch_time = datetime.now()
        self.synced = False
        self.invite_link = None

    async def setup_hook(self):
        extensions = [
            'cogs.moderation', 'cogs.fun', 'cogs.utility',
            'cogs.game', 'cogs.misc', 'cogs.help',
            'cogs.webhooks', 'cogs.verification',
            'cogs.autorole', 'cogs.welcome', 'cogs.modlog'
        ]
        for ext in extensions:
            await self.load_extension(ext)
        logging.info("Joy's extensions loaded successfully!")

    async def on_ready(self):
        if not self.synced:
            await self.tree.sync()
            self.synced = True
            logging.info("Command tree synced")

        self.invite_link = f"https://discord.com/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot%20applications.commands"
        logging.info(f'Joy is ready! Logged in as {self.user} (ID: {self.user.id})')
        logging.info(f'Invite link: {self.invite_link}')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title="♡ Oops!",
                description="I couldn't find that command. Try `j!help` to see what I can do!",
                color=self.theme['error']
            )
        elif isinstance(error, commands.CommandOnCooldown):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            command = ctx.command
            params = []
            for key, value in command.params.items():
                if key not in ['self', 'ctx']:
                    if value.default == value.empty:
                        params.append(f'<{key}>')
                    else:
                        params.append(f'[{key}]')
            usage = ' '.join([f'j!{command.name}'] + params)
            embed = discord.Embed(
                title="♡ Missing Information",
                description=f"You're missing some information for this command!\n\n**Usage:**\n`{usage}`",
                color=self.theme['error']
            )
            if command.help:
                embed.add_field(name="Description", value=command.help)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="♡ Missing Permissions",
                description="You don't have permission to use this command!",
                color=self.theme['error']
            )
        else:
            embed = discord.Embed(
                title="♡ Something went wrong",
                description=str(error),
                color=self.theme['error']
            )
        await ctx.send(embed=embed)

    def load_webhooks(self):
        try:
            if os.path.exists(self.webhooks_file):
                with open(self.webhooks_file, 'r') as f:
                    self.webhook_data = json.load(f)
            else:
                self.webhook_data = {"webhooks": {}, "selected": {}}
                self.save_webhooks()
        except Exception:
            self.webhook_data = {"webhooks": {}, "selected": {}}

    def save_webhooks(self):
        try:
            with open(self.webhooks_file, 'w') as f:
                json.dump(self.webhook_data, f, indent=4)
        except Exception:
            pass

    def load_cooldowns(self):
        try:
            os.makedirs('data', exist_ok=True)
            if os.path.exists(self.cooldowns_file):
                with open(self.cooldowns_file, 'r') as f:
                    self.cooldowns = json.load(f)
            else:
                self.cooldowns = {"bug": {}, "feature": {}}
                self.save_cooldowns()
        except Exception:
            self.cooldowns = {"bug": {}, "feature": {}}

    def save_cooldowns(self):
        try:
            with open(self.cooldowns_file, 'w') as f:
                json.dump(self.cooldowns, f, indent=4)
        except Exception:
            pass

    def get_remaining_uses(self, command: str, user_id: str) -> tuple[int, float]:
        current_time = datetime.now(timezone.utc).timestamp()
        user_cooldowns = self.cooldowns.get(command, {}).get(
            str(user_id), {"uses": 0, "reset_time": current_time})
        if current_time > user_cooldowns["reset_time"]:
            return 3, 0
        uses_left = 3 - user_cooldowns["uses"]
        time_left = user_cooldowns["reset_time"] - current_time
        return uses_left, max(0, time_left)

    def update_cooldown(self, command: str, user_id: str):
        current_time = datetime.now(timezone.utc).timestamp()
        if command not in self.cooldowns:
            self.cooldowns[command] = {}
        if str(user_id) not in self.cooldowns[command]:
            self.cooldowns[command][str(user_id)] = {
                "uses": 1,
                "reset_time": current_time + 86400
            }
        else:
            user_cooldowns = self.cooldowns[command][str(user_id)]
            if current_time > user_cooldowns["reset_time"]:
                user_cooldowns["uses"] = 1
                user_cooldowns["reset_time"] = current_time + 86400
            else:
                user_cooldowns["uses"] += 1
        self.save_cooldowns()


def main():
    bot = JoyBot()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
