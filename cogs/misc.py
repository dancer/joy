import asyncio
import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch_token = None
        self.session = aiohttp.ClientSession()

    async def get_twitch_token(self):
        try:
            async with self.session.post(
                'https://id.twitch.tv/oauth2/token',
                params={
                    'client_id': TWITCH_CLIENT_ID,
                    'client_secret': TWITCH_CLIENT_SECRET,
                    'grant_type': 'client_credentials'
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['access_token']
        except Exception:
            pass
        return None

    async def get_twitch_user(self, username: str):
        if not self.twitch_token:
            self.twitch_token = await self.get_twitch_token()
            if not self.twitch_token:
                return None
        headers = {
            'Client-ID': TWITCH_CLIENT_ID,
            'Authorization': f'Bearer {self.twitch_token}'
        }
        try:
            async with self.session.get(
                f'https://api.twitch.tv/helix/users?login={username.lower()}',
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data['data']:
                        return None
                    user = data['data'][0]
                    try:
                        async with self.session.get(
                            f'https://api.twitch.tv/helix/channels/followers?broadcaster_id={user["id"]}',
                            headers=headers
                        ) as follows_response:
                            if follows_response.status == 200:
                                follows_data = await follows_response.json()
                                user['followers'] = follows_data.get('total', 0)
                            else:
                                user['followers'] = 0
                    except Exception:
                        user['followers'] = 0
                    try:
                        async with self.session.get(
                            f'https://api.twitch.tv/helix/streams?user_login={username.lower()}',
                            headers=headers
                        ) as stream_response:
                            if stream_response.status == 200:
                                stream_data = await stream_response.json()
                                is_live = bool(stream_data.get('data', []))
                                stream_info = stream_data['data'][0] if is_live else None
                            else:
                                is_live = False
                                stream_info = None
                    except Exception:
                        is_live = False
                        stream_info = None
                    return {'user': user, 'is_live': is_live, 'stream_info': stream_info}
                elif response.status == 401:
                    self.twitch_token = await self.get_twitch_token()
                    if self.twitch_token:
                        return await self.get_twitch_user(username)
        except Exception:
            pass
        return None

    @commands.hybrid_command(description="Get info about a Twitch streamer")
    async def twitch(self, ctx, username: str):
        async with ctx.typing():
            if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
                embed = discord.Embed(title="♡ Error", description="Twitch API credentials are not configured!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            data = await self.get_twitch_user(username)
            if not data:
                embed = discord.Embed(title="♡ Error", description=f"Could not find Twitch user: {username}", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            user = data['user']
            is_live = data['is_live']
            stream_info = data['stream_info']
            embed = discord.Embed(
                title=f"♡ About {user['display_name']}",
                description="Information about this Twitch channel",
                color=self.bot.theme['accent']
            )
            embed.set_thumbnail(url=user['profile_image_url'])
            channel_stats = []
            channel_stats.append(f"Status: {('Live Now!' if is_live else 'Offline')}")
            channel_stats.append(f"Followers: {user['followers']:,}")
            if user['broadcaster_type']:
                channel_stats.append(f"Type: {user['broadcaster_type'].title()}")
            embed.add_field(name="Channel Stats", value="\n".join(channel_stats), inline=False)
            if is_live and stream_info:
                stream_details = [
                    f"Title: {stream_info['title']}",
                    f"Game: {stream_info['game_name']}",
                    f"Current Viewers: {stream_info['viewer_count']:,}"
                ]
                embed.add_field(name="Stream Stats", value="\n".join(stream_details), inline=False)
            embed.add_field(
                name="Channel Link",
                value=f"[Watch on Twitch](https://twitch.tv/{username})",
                inline=False
            )
            embed.set_footer(text=f"Account Created: {user['created_at'][:10]}")
            await ctx.send(embed=embed)

    async def get_twitch_team(self, team_name: str):
        if not self.twitch_token:
            self.twitch_token = await self.get_twitch_token()
            if not self.twitch_token:
                return None
        headers = {
            'Client-ID': TWITCH_CLIENT_ID,
            'Authorization': f'Bearer {self.twitch_token}'
        }
        try:
            async with self.session.get(
                f'https://api.twitch.tv/helix/teams?name={team_name.lower()}',
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data['data']:
                        return None
                    return data['data'][0]
                elif response.status == 401:
                    self.twitch_token = await self.get_twitch_token()
                    if self.twitch_token:
                        return await self.get_twitch_team(team_name)
        except Exception:
            pass
        return None

    @commands.hybrid_command(description="Get info about a Twitch team")
    async def team(self, ctx, *, team_name: str):
        async with ctx.typing():
            if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
                embed = discord.Embed(title="♡ Error", description="Twitch API credentials are not configured!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            team_data = await self.get_twitch_team(team_name)
            if not team_data:
                embed = discord.Embed(title="♡ Error", description=f"Could not find Twitch team: {team_name}", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            embed = discord.Embed(
                title=f"♡ Team {team_data['team_display_name']}",
                description=team_data['info'],
                color=self.bot.theme['accent']
            )
            if team_data.get('thumbnail_url'):
                embed.set_thumbnail(url=team_data['thumbnail_url'])
            embed.add_field(name="Team Name", value=team_data['team_name'], inline=True)
            created_at = datetime.strptime(team_data['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            embed.add_field(name="Created", value=created_at.strftime("%B %d, %Y"), inline=True)
            if team_data.get('users'):
                members = [f"{user['user_name']}" for user in team_data['users'][:10]]
                remaining = len(team_data['users']) - 10 if len(team_data['users']) > 10 else 0
                member_list = "\n".join(members)
                if remaining > 0:
                    member_list += f"\n*...and {remaining} more members*"
                embed.add_field(
                    name=f"Team Members ({len(team_data['users'])} total)",
                    value=member_list,
                    inline=False
                )
            embed.add_field(
                name="Team Link",
                value=f"[Team Page](https://www.twitch.tv/team/{team_data['team_name']})",
                inline=False
            )
            if team_data.get('banner'):
                embed.set_image(url=team_data['banner'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Get the invite link for Joy")
    async def invite(self, ctx):
        embed = discord.Embed(
            title="♡ Invite Joy",
            description="Click the link below to add Joy to your server!",
            color=self.bot.theme['primary']
        )
        embed.add_field(
            name="Invite Link",
            value="[Click here to invite Joy](https://discord.com/oauth2/authorize?client_id=1342178836673990697&permissions=8&integration_type=0&scope=bot)",
            inline=False
        )
        embed.set_footer(text="Thank you for sharing Joy with others! ♡")
        await ctx.send(embed=embed)

    def cog_unload(self):
        if self.session:
            asyncio.create_task(self.session.close())


async def setup(bot):
    await bot.add_cog(Misc(bot))
