```bash
> what is joy?

  a discord bot built to spread joy and manage servers
  moderation, games, fun commands, verification, webhooks
  works with both prefix (j!) and slash (/) commands

> install?

  git clone https://github.com/dancer/joy
  cd joy
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt

> setup?

  cp .env.example .env
  # add your discord token, owner id, and twitch keys
  python3 dawn.py

> hot reload?

  python3 run.py
  # auto restarts on file changes

> commands?

  moderation:
    kick, ban, unban, mute, unmute
    clear, warn, role, lock, unlock
    slowmode, lockdown, msg, prefix

  fun:
    hug, inspire, roll, choose
    donate, bug

  games:
    daily, balance, coinflip
    slots, blackjack, leaderboard

  utility:
    ping, serverinfo, userinfo
    ascii, botinfo, feature
    servers, cc

  webhooks:
    webhook create, webhook connect
    webhook list, webhook select
    webhook send, webhook delete

  verification:
    verify, verifylist, verifyremove
    textverify

  misc:
    twitch, team, invite

> server config?

  autorole set <role>       # auto assign role on join
  autorole remove           # disable auto role
  welcome channel <channel> # set welcome channel
  welcome message <text>    # set welcome message
  welcome disable           # disable welcome
  leave channel <channel>   # set leave channel
  leave message <text>      # set leave message
  leave disable             # disable leave
  modlog set <channel>      # log mod actions
  modlog disable            # disable logging

> message placeholders?

  {user}    # mentions the user
  {server}  # server name
  {name}    # username

> economy?

  j!daily                   # claim 100 joycoins daily
  j!coinflip <amount>       # 60% win rate
  j!slots <amount>          # slot machine with multipliers
  j!blackjack <amount>      # play blackjack
  j!leaderboard             # top 10 players

> env variables?

  DISCORD_TOKEN             # bot token
  OWNER_ID                  # your discord id
  GUILD_ID                  # your server id
  TWITCH_CLIENT_ID          # twitch api
  TWITCH_CLIENT_SECRET      # twitch api

> stack?

  python 3.13
  discord.py 2.7
  hybrid commands (prefix + slash)

> structure?

  dawn.py                   # bot entry point
  run.py                    # hot reload wrapper
  cogs/
    moderation.py           # server management
    fun.py                  # entertainment
    game.py                 # economy and games
    utility.py              # info and tools
    misc.py                 # twitch and extras
    help.py                 # help system
    webhooks.py             # webhook management
    verification.py         # role verification
    autorole.py             # auto role on join
    welcome.py              # welcome/leave messages
    modlog.py               # mod action logging
  data/                     # json storage (auto created)

> license?

  mit
```
