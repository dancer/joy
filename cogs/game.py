import discord
from discord.ext import commands
import json
import os
import random
from datetime import datetime, timedelta, timezone


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'data/game_data.json'
        self.data = self.load_data()
        self.daily_amount = 100
        self.card_suits = ['♡', '♢', '♤', '♧']
        self.card_values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.blackjack_games = {}

    def load_data(self):
        try:
            os.makedirs('data', exist_ok=True)
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return {"users": {}}
        except Exception:
            return {"users": {}}

    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception:
            pass

    def get_user_data(self, user_id: str):
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "coins": 0, "last_daily": None, "games_won": 0, "games_played": 0
            }
        return self.data["users"][user_id]

    def create_deck(self):
        deck = [(value, suit) for suit in self.card_suits for value in self.card_values]
        random.shuffle(deck)
        return deck

    def calculate_hand_value(self, hand):
        value = 0
        aces = 0
        for card in hand:
            card_value = card[0]
            if card_value in ['J', 'Q', 'K']:
                value += 10
            elif card_value == 'A':
                aces += 1
            else:
                value += int(card_value)
        for _ in range(aces):
            if value + 11 <= 21:
                value += 11
            else:
                value += 1
        return value

    def format_hand(self, hand, hide_second=False):
        if hide_second:
            return f"{hand[0][0]}{hand[0][1]} ??"
        return " ".join(f"{card[0]}{card[1]}" for card in hand)

    @commands.hybrid_group(invoke_without_command=True, fallback="list")
    async def game(self, ctx):
        prefix = self.bot.prefixes.get(str(ctx.guild.id), "j!") if ctx.guild else "j!"
        embed = discord.Embed(
            title="♡ Joy's Games",
            description="Here are all the available game commands:",
            color=self.bot.theme['primary']
        )
        embed.add_field(name=f"{prefix}daily", value="Claim your daily JoyCoins reward", inline=False)
        embed.add_field(name=f"{prefix}balance", value="Check your JoyCoins balance", inline=False)
        embed.add_field(name=f"{prefix}coinflip <amount>", value="Bet your JoyCoins on a coin flip", inline=False)
        embed.add_field(name=f"{prefix}slots <amount>", value="Play the slot machine", inline=False)
        embed.add_field(name=f"{prefix}blackjack <amount>", value="Play blackjack with JoyCoins", inline=False)
        embed.set_footer(text="More games coming soon! ♡")
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Claim your daily JoyCoins reward")
    async def daily(self, ctx):
        user_data = self.get_user_data(str(ctx.author.id))
        now = datetime.now(timezone.utc)
        last_daily = user_data["last_daily"]
        if last_daily and (now - datetime.fromisoformat(last_daily)).total_seconds() < 86400:
            next_daily = datetime.fromisoformat(last_daily) + timedelta(days=1)
            embed = discord.Embed(
                title="♡ Daily Reward",
                description=f"You've already claimed your daily reward!\nNext reward available: {discord.utils.format_dt(next_daily, style='R')}",
                color=self.bot.theme['error']
            )
        else:
            user_data["coins"] += self.daily_amount
            user_data["last_daily"] = now.isoformat()
            self.save_data()
            embed = discord.Embed(
                title="♡ Daily Reward",
                description=f"You've received {self.daily_amount} JoyCoins!\nCurrent balance: {user_data['coins']} JoyCoins",
                color=self.bot.theme['primary']
            )
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Check your JoyCoins balance")
    async def balance(self, ctx):
        user_data = self.get_user_data(str(ctx.author.id))
        embed = discord.Embed(
            title="♡ JoyCoins Balance",
            description=f"Balance: {user_data['coins']} JoyCoins\nGames Won: {user_data['games_won']}\nGames Played: {user_data['games_played']}",
            color=self.bot.theme['primary']
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Bet JoyCoins on a coin flip")
    async def coinflip(self, ctx, amount: int):
        user_data = self.get_user_data(str(ctx.author.id))
        if amount <= 0:
            embed = discord.Embed(title="♡ Error", description="Please bet a positive amount!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
            return
        if amount > user_data["coins"]:
            embed = discord.Embed(title="♡ Error", description="You don't have enough JoyCoins!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
            return
        win = random.random() < 0.60
        user_data["games_played"] += 1
        if win:
            user_data["coins"] += amount
            user_data["games_won"] += 1
            embed = discord.Embed(title="♡ Coin Flip - You Won!", description=f"You won {amount} JoyCoins!\nNew balance: {user_data['coins']} JoyCoins", color=self.bot.theme['primary'])
        else:
            user_data["coins"] -= amount
            embed = discord.Embed(title="♡ Coin Flip - You Lost", description=f"You lost {amount} JoyCoins!\nNew balance: {user_data['coins']} JoyCoins", color=self.bot.theme['error'])
        self.save_data()
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Play the slot machine")
    async def slots(self, ctx, amount: int):
        user_data = self.get_user_data(str(ctx.author.id))
        if amount <= 0:
            embed = discord.Embed(title="♡ Error", description="Please bet a positive amount!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
            return
        if amount > user_data["coins"]:
            embed = discord.Embed(title="♡ Error", description="You don't have enough JoyCoins!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
            return
        symbols = ["♡", "♢", "♤", "♧", "★"]
        multipliers = {"♡": 5, "★": 3, "any": 2}
        result = [random.choice(symbols) for _ in range(3)]
        user_data["games_played"] += 1
        if all(s == "♡" for s in result):
            winnings = amount * multipliers["♡"]
            win_type = "JACKPOT"
        elif all(s == "★" for s in result):
            winnings = amount * multipliers["★"]
            win_type = "STAR POWER"
        elif len(set(result)) == 1:
            winnings = amount * multipliers["any"]
            win_type = "THREE OF A KIND"
        else:
            winnings = 0
            win_type = None
        if winnings > 0:
            user_data["coins"] += winnings - amount
            user_data["games_won"] += 1
            color = self.bot.theme['primary']
            result_text = f"You won {winnings} JoyCoins! ({win_type})"
        else:
            user_data["coins"] -= amount
            color = self.bot.theme['error']
            result_text = "You lost!"
        self.save_data()
        embed = discord.Embed(
            title="♡ Slot Machine",
            description=f"[ {' | '.join(result)} ]\n\n{result_text}\nNew balance: {user_data['coins']} JoyCoins",
            color=color
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Play a game of blackjack")
    async def blackjack(self, ctx, amount: int):
        user_data = self.get_user_data(str(ctx.author.id))
        if amount <= 0:
            embed = discord.Embed(title="♡ Error", description="Please bet a positive amount!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
            return
        if amount > user_data["coins"]:
            embed = discord.Embed(title="♡ Error", description="You don't have enough JoyCoins!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
            return
        if ctx.author.id in self.blackjack_games:
            embed = discord.Embed(title="♡ Error", description="You already have an active blackjack game!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
            return
        deck = self.create_deck()
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        self.blackjack_games[ctx.author.id] = {
            'deck': deck, 'player_hand': player_hand,
            'dealer_hand': dealer_hand, 'bet': amount, 'status': 'playing'
        }
        player_value = self.calculate_hand_value(player_hand)
        if player_value == 21:
            dealer_value = self.calculate_hand_value(dealer_hand)
            if dealer_value == 21:
                del self.blackjack_games[ctx.author.id]
                embed = discord.Embed(
                    title="♡ Blackjack - Push!",
                    description=f"Both you and the dealer got blackjack!\n\n**Your Hand:**\n```{self.format_hand(player_hand)}```\n\n**Dealer's Hand:**\n```{self.format_hand(dealer_hand)}```",
                    color=self.bot.theme['primary']
                )
                await ctx.send(embed=embed)
                return
            else:
                winnings = int(amount * 1.5)
                user_data["coins"] += winnings
                user_data["games_won"] += 1
                user_data["games_played"] += 1
                self.save_data()
                del self.blackjack_games[ctx.author.id]
                embed = discord.Embed(
                    title="♡ Blackjack - You Won!",
                    description=f"Blackjack! You won {winnings} JoyCoins!\n\n**Your Hand:**\n```{self.format_hand(player_hand)}```\n\n**Dealer's Hand:**\n```{self.format_hand(dealer_hand)}```\n\nNew balance: {user_data['coins']} JoyCoins",
                    color=self.bot.theme['primary']
                )
                await ctx.send(embed=embed)
                return
        view = BlackjackView(self, ctx)
        visible_card_value = 10 if dealer_hand[0][0] in ['J', 'Q', 'K'] else (
            11 if dealer_hand[0][0] == 'A' else int(dealer_hand[0][0]))
        embed = discord.Embed(
            title="♡ Blackjack",
            description=f"**Your Hand:**\n```{self.format_hand(player_hand)}``` (Value: {player_value})\n\n**Dealer's Hand:**\n```{self.format_hand(dealer_hand, hide_second=True)}``` (Value: {visible_card_value})\n\nChoose your action:",
            color=self.bot.theme['primary']
        )
        view.message = await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(description="Give coins to a user")
    @commands.is_owner()
    async def coins(self, ctx, amount: int, user_id: int):
        try:
            target_user = await self.bot.fetch_user(user_id)
            if not target_user:
                embed = discord.Embed(title="♡ Error", description="Could not find that user!", color=self.bot.theme['error'])
                await ctx.send(embed=embed)
                return
            user_data = self.get_user_data(str(user_id))
            user_data["coins"] += amount
            self.save_data()
            embed = discord.Embed(
                title="♡ Coins Added",
                description=f"Added {amount} JoyCoins to {target_user.name}'s balance!\nNew balance: {user_data['coins']} JoyCoins",
                color=self.bot.theme['primary']
            )
            await ctx.send(embed=embed)
        except discord.NotFound:
            embed = discord.Embed(title="♡ Error", description="Could not find that user!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
        except Exception:
            embed = discord.Embed(title="♡ Error", description="An error occurred while giving coins!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Reset a user's coin balance")
    @commands.is_owner()
    async def resetcoins(self, ctx, user_id: int):
        user_str = str(user_id)
        if user_str not in self.data["users"]:
            embed = discord.Embed(title="♡ Error", description="That user has no game data!", color=self.bot.theme['error'])
            await ctx.send(embed=embed)
            return
        self.data["users"][user_str]["coins"] = 0
        self.save_data()
        try:
            user = await self.bot.fetch_user(user_id)
            name = user.name
        except Exception:
            name = str(user_id)
        embed = discord.Embed(
            title="♡ Coins Reset",
            description=f"Reset {name}'s coin balance to 0.",
            color=self.bot.theme['primary']
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="View the top 10 players")
    async def leaderboard(self, ctx):
        sorted_users = sorted(
            self.data["users"].items(),
            key=lambda x: (x[1]["coins"], x[1]["games_won"]),
            reverse=True
        )[:10]
        embed = discord.Embed(
            title="♡ JoyCoins Leaderboard",
            description="Top 10 players:",
            color=self.bot.theme['primary']
        )
        for i, (uid, data) in enumerate(sorted_users, 1):
            user = await self.bot.fetch_user(int(uid))
            embed.add_field(
                name=f"{i}. {user.name}",
                value=f"JoyCoins: {data['coins']}\nGames Won: {data['games_won']}",
                inline=False
            )
        await ctx.send(embed=embed)


class BlackjackView(discord.ui.View):
    def __init__(self, game_cog, ctx, timeout=30):
        super().__init__(timeout=timeout)
        self.game_cog = game_cog
        self.ctx = ctx
        self.message = None

    async def on_timeout(self):
        if self.ctx.author.id in self.game_cog.blackjack_games:
            game = self.game_cog.blackjack_games[self.ctx.author.id]
            user_data = self.game_cog.get_user_data(str(self.ctx.author.id))
            user_data["coins"] -= game['bet']
            user_data["games_played"] += 1
            self.game_cog.save_data()
            del self.game_cog.blackjack_games[self.ctx.author.id]
            embed = discord.Embed(
                title="♡ Blackjack - Timeout",
                description=f"Game cancelled due to inactivity. You lost {game['bet']} JoyCoins.\nNew balance: {user_data['coins']} JoyCoins",
                color=self.game_cog.bot.theme['error']
            )
            await self.message.edit(embed=embed, view=None)

    @discord.ui.button(label='Hit', style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return
        game = self.game_cog.blackjack_games.get(self.ctx.author.id)
        if not game or game['status'] != 'playing':
            return
        game['player_hand'].append(game['deck'].pop())
        player_value = self.game_cog.calculate_hand_value(game['player_hand'])
        dealer_value = self.game_cog.calculate_hand_value(game['dealer_hand'])
        if player_value > 21:
            user_data = self.game_cog.get_user_data(str(self.ctx.author.id))
            user_data["coins"] -= game['bet']
            user_data["games_played"] += 1
            self.game_cog.save_data()
            del self.game_cog.blackjack_games[self.ctx.author.id]
            embed = discord.Embed(
                title="♡ Blackjack - Bust!",
                description=f"**Your Hand:**\n```{self.game_cog.format_hand(game['player_hand'])}``` (Value: {player_value})\n\n**Dealer's Hand:**\n```{self.game_cog.format_hand(game['dealer_hand'])}``` (Value: {dealer_value})\n\nYou went bust! You lost {game['bet']} JoyCoins.\nNew balance: {user_data['coins']} JoyCoins",
                color=self.game_cog.bot.theme['error']
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return
        embed = discord.Embed(
            title="♡ Blackjack",
            description=f"**Your Hand:**\n```{self.game_cog.format_hand(game['player_hand'])}``` (Value: {player_value})\n\n**Dealer's Hand:**\n```{self.game_cog.format_hand(game['dealer_hand'], hide_second=True)}``` (Value: {dealer_value})\n\nChoose your action:",
            color=self.game_cog.bot.theme['primary']
        )
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label='Stand', style=discord.ButtonStyle.secondary)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return
        game = self.game_cog.blackjack_games.get(self.ctx.author.id)
        if not game or game['status'] != 'playing':
            return
        dealer_hand = game['dealer_hand']
        dealer_value = self.game_cog.calculate_hand_value(dealer_hand)
        while dealer_value < 17:
            dealer_hand.append(game['deck'].pop())
            dealer_value = self.game_cog.calculate_hand_value(dealer_hand)
        player_value = self.game_cog.calculate_hand_value(game['player_hand'])
        user_data = self.game_cog.get_user_data(str(self.ctx.author.id))
        if dealer_value > 21 or player_value > dealer_value:
            user_data["coins"] += game['bet']
            user_data["games_won"] += 1
            result = f"You won {game['bet']} JoyCoins!"
            color = self.game_cog.bot.theme['primary']
        elif dealer_value > player_value:
            user_data["coins"] -= game['bet']
            result = f"You lost {game['bet']} JoyCoins!"
            color = self.game_cog.bot.theme['error']
        else:
            result = "Push! Your bet has been returned."
            color = self.game_cog.bot.theme['primary']
        user_data["games_played"] += 1
        self.game_cog.save_data()
        del self.game_cog.blackjack_games[self.ctx.author.id]
        embed = discord.Embed(
            title="♡ Blackjack - Game Over!",
            description=f"**Your Hand:**\n```{self.game_cog.format_hand(game['player_hand'])}``` (Value: {player_value})\n\n**Dealer's Hand:**\n```{self.game_cog.format_hand(dealer_hand)}``` (Value: {dealer_value})\n\n{result}\nNew balance: {user_data['coins']} JoyCoins",
            color=color
        )
        await interaction.response.edit_message(embed=embed, view=None)


async def setup(bot):
    await bot.add_cog(Games(bot))
