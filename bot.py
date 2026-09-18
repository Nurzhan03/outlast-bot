import os
import aiohttp
import discord
from discord.ext import tasks
from dotenv import load_dotenv


# ==========================================
# НАСТРОЙКИ
# ==========================================

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Steam App ID The Outlast Trials
STEAM_APP_ID = 1304930

# Обновление каждые 2 минуты
UPDATE_INTERVAL = 120


# ==========================================
# DISCORD
# ==========================================

intents = discord.Intents.default()

bot = discord.Client(intents=intents)


# ==========================================
# ПОЛУЧЕНИЕ ОНЛАЙНА STEAM
# ==========================================

async def get_steam_players():

    url = (
        "https://api.steampowered.com/"
        "ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
        f"?appid={STEAM_APP_ID}"
    )

    try:

        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(url) as response:

                if response.status != 200:

                    print(
                        f"[STEAM] HTTP ошибка: "
                        f"{response.status}"
                    )

                    return None

                data = await response.json()

                players = (
                    data
                    .get("response", {})
                    .get("player_count")
                )

                if players is None:

                    print(
                        "[STEAM] Steam не вернул "
                        "количество игроков"
                    )

                    return None

                return int(players)

    except Exception as error:

        print(
            f"[STEAM] Ошибка: {error}"
        )

        return None


# ==========================================
# ОБНОВЛЕНИЕ КАНАЛА
# ==========================================

@tasks.loop(seconds=UPDATE_INTERVAL)
async def update_online():

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:

        print(
            "[DISCORD] Канал не найден!"
        )

        return

    players = await get_steam_players()

    if players is None:

        print(
            "[BOT] Не удалось получить "
            "онлайн Steam."
        )

        return

    formatted_players = f"{players:,}"

    new_name = (
        f"🌐 Онлайн в игре・{formatted_players}"
    )

    if channel.name == new_name:

        print(
            f"[ONLINE] {formatted_players} "
            "игроков"
        )

        return

    try:

        await channel.edit(name=new_name)

        print(
            f"[UPDATE] The Outlast Trials: "
            f"{formatted_players} игроков"
        )

    except discord.Forbidden:

        print(
            "[DISCORD] У бота нет права "
            "«Управление каналами»."
        )

    except Exception as error:

        print(
            f"[DISCORD] Ошибка: {error}"
        )


# ==========================================
# ПОСЛЕ ПОДКЛЮЧЕНИЯ К DISCORD
# ==========================================

@bot.event
async def on_ready():

    print()
    print("====================================")
    print("☣️  OUTLAST TRIALS ONLINE BOT")
    print("====================================")
    print(f"Бот: {bot.user}")
    print(f"ID: {bot.user.id}")
    print("====================================")
    print()

    # Сразу получаем онлайн
    # после запуска бота
    if not update_online.is_running():

        update_online.start()


# ==========================================
# ПРОВЕРКА ТОКЕНА
# ==========================================

if not DISCORD_TOKEN:

    raise ValueError(
        "Не найден DISCORD_TOKEN "
        "в файле .env"
    )


# ==========================================
# ЗАПУСК
# ==========================================

bot.run(DISCORD_TOKEN)