import os
import requests
import sqlite3

import discord
from dotenv import load_dotenv
from riotwatcher import LolWatcher, RiotWatcher


load_dotenv()

TOKEN      = os.getenv("DISCORD_TOKEN")
RIOT_KEY   = os.getenv("LEAGUE_TOKEN")
GUILD_IDS  = [os.getenv("GUILD_1"), os.getenv("GUILD_2")]
REGION     = "na1"
AMERICAS   = "americas"

lol_watcher  = LolWatcher(RIOT_KEY)
riot_watcher = RiotWatcher(RIOT_KEY)


db = sqlite3.connect("leagueAcc.db")
cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        discord_id INTEGER PRIMARY KEY,
        riot_name  TEXT UNIQUE,
        riot_tag   TEXT,
        summ_lvl   INT
    )
""")
db.commit()


def get_puuid(riot_name: str, riot_tag: str) -> str | None:
    url = f"https://{AMERICAS}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riot_name}/{riot_tag}"
    res = requests.get(url, params={"api_key": RIOT_KEY})
    return res.json().get("puuid")


def get_summoner(puuid: str) -> dict | None:
    url = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    res = requests.get(url, params={"api_key": RIOT_KEY})
    return res.json() if res.ok else None


def get_current_patch() -> str:
    res = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    return res.json()[0]


def get_ranked_stats(puuid: str) -> list:
    return lol_watcher.league.by_puuid(REGION, puuid)


def get_champion_mastery(puuid: str) -> list:
    url = f"https://{REGION}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
    return requests.get(url, params={"api_key": RIOT_KEY}).json()


def get_champion_map(patch: str) -> dict[int, str]:
    url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json"
    data = requests.get(url).json()["data"]
    return {int(info["key"]): name for name, info in data.items()}


def parse_riot_id(raw: str) -> tuple[str, str] | None:
    """Parse 'Riot Name #TAG' into (name, tag). Returns None on bad format."""
    if "#" not in raw:
        return None
    name, _, tag = raw.rpartition("#")
    return name.strip(), tag.strip()


def base_embed(title: str, description: str) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=discord.Color.nitro_pink())
    embed.set_author(name="Blitz and Crank")
    return embed


intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.slash_command(guild_ids=GUILD_IDS, name="test", description="Ping the bot")
async def cmd_test(ctx):
    await ctx.respond("Hello!")


@bot.slash_command(guild_ids=GUILD_IDS, name="register", description="Link your Discord to a League account")
async def cmd_register(ctx, riot_name: str, riot_tag: str):
    discord_id = ctx.author.id

    cursor.execute("SELECT discord_id FROM users WHERE riot_name = ? AND riot_tag = ?", (riot_name, riot_tag))
    if cursor.fetchone():
        await ctx.respond(f"**{riot_name}#{riot_tag}** is already registered to someone.")
        return

    cursor.execute("SELECT riot_name, riot_tag FROM users WHERE discord_id = ?", (discord_id,))
    if cursor.fetchone():
        await ctx.respond("You already have a linked account. Use `/unregister` first.")
        return

    puuid = get_puuid(riot_name, riot_tag)
    if not puuid:
        await ctx.respond("Couldn't find that Riot account. Double-check the name and tag.")
        return

    summoner = get_summoner(puuid)
    if not summoner:
        await ctx.respond("Found the Riot account but couldn't fetch summoner data.")
        return

    cursor.execute(
        "INSERT INTO users (discord_id, riot_name, riot_tag, summ_lvl) VALUES (?, ?, ?, ?)",
        (discord_id, riot_name, riot_tag, summoner["summonerLevel"])
    )
    db.commit()
    await ctx.respond(f"Registered **{riot_name}#{riot_tag}** to your Discord!")


@bot.slash_command(guild_ids=GUILD_IDS, name="unregister", description="Unlink your League account")
async def cmd_unregister(ctx):
    discord_id = ctx.author.id
    cursor.execute("SELECT riot_name, riot_tag FROM users WHERE discord_id = ?", (discord_id,))
    result = cursor.fetchone()

    if not result:
        await ctx.respond("You don't have a linked account.")
        return

    riot_name, riot_tag = result
    cursor.execute("DELETE FROM users WHERE discord_id = ?", (discord_id,))
    db.commit()
    await ctx.respond(f"Unlinked **{riot_name}#{riot_tag}** from your Discord.")


@bot.slash_command(guild_ids=GUILD_IDS, name="leaderboard", description="Top 5 users by account level")
async def cmd_leaderboard(ctx):
    cursor.execute("SELECT riot_name, riot_tag, summ_lvl FROM users ORDER BY summ_lvl DESC LIMIT 5")
    rows = cursor.fetchall()

    if not rows:
        await ctx.respond("No users registered yet!")
        return

    lines = "\n".join(f"{i+1}. {name} #{tag} — Lvl {lvl}" for i, (name, tag, lvl) in enumerate(rows))
    embed = base_embed("Current Leaderboard", f"**BY ACCOUNT LEVEL**\n{lines}")
    await ctx.respond(embed=embed)


@bot.slash_command(guild_ids=GUILD_IDS, name="solo_rank", description="Show ranked stats for a player")
async def cmd_solo_rank(ctx, riot_id: str):
    parsed = parse_riot_id(riot_id)
    if not parsed:
        await ctx.respond("Please use the format: `Riot Name #TAG`")
        return

    riot_name, riot_tag = parsed

    puuid = get_puuid(riot_name, riot_tag)
    if not puuid:
        await ctx.respond("Summoner not found. Check the Riot ID and try again.")
        return

    summoner = get_summoner(puuid)
    if not summoner:
        await ctx.respond("Couldn't retrieve summoner data.")
        return

    patch     = get_current_patch()
    icon_url  = f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/profileicon/{summoner['profileIconId']}.png"
    summ_lvl  = summoner["summonerLevel"]
    stats     = get_ranked_stats(puuid)

    # Unranked player: show top 3 champion masteries
    if not stats:
        mastery     = get_champion_mastery(puuid)
        champ_map   = get_champion_map(patch)
        top_champs  = "\n".join(
            f"{champ_map.get(m['championId'], 'Unknown')}: {m['championPoints']:,} pts"
            for m in mastery[:3]
        )
        desc  = f"**Account Level** — {summ_lvl}\n**Unranked**\n\n{top_champs}"
        embed = base_embed(f"{riot_name}'s Stats", desc)
        embed.set_image(url=icon_url)
        await ctx.respond(embed=embed)
        return

    # Ranked player
    entry      = stats[0]
    tier       = entry["tier"].capitalize()
    division   = entry["rank"]
    lp         = entry["leaguePoints"]
    wins       = entry["wins"]
    losses     = entry["losses"]
    total      = wins + losses
    winrate    = round(wins / total * 100) if total else 0

    extra = ""
    if wins == losses:
        extra = " Perfectly balanced. :3"
    elif wins < losses:
        extra = " Maybe take a break?"
    if riot_name.lower() == "heavens door":
        extra += " **THIS USER IS TALL RICH AND HANDSOME**"

    desc = (
        f"**Account Level** — {summ_lvl}\n"
        f"**Rank** — {tier} {division} ({lp} LP)\n"
        f"**Ranked Record** — {wins}W / {losses}L ({winrate}% WR){extra}"
    )
    embed = base_embed(f"{riot_name}'s Stats", desc)
    embed.set_image(url=icon_url)
    await ctx.respond(embed=embed)



bot.run(TOKEN)