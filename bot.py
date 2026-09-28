import os
import inspect
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database import init_database
from booster import Booster, BoosterPanelView


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "❌ DISCORD_TOKEN belum ditemukan di environment variables."
    )


# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.default()

intents.guilds = True
intents.members = True
intents.message_content = True


# =========================================================
# BOT
# =========================================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


# =========================================================
# DATABASE
# =========================================================

def setup_database():
    try:
        init_database()
        print("✅ Database berhasil diinisialisasi.")
    except Exception as e:
        print(f"❌ Database Error: {e}")


# =========================================================
# LOAD BOOSTER COG
# =========================================================

async def setup_booster():

    try:
        print("🔄 Memuat Booster Custom Role...")

        # -------------------------------------------------
        # Tambahkan Cog
        # -------------------------------------------------

        result = bot.add_cog(
            Booster(bot)
        )

        # Kompatibel dengan discord.py maupun Pycord
        if inspect.isawaitable(result):
            await result

        print("✅ Booster Custom Role berhasil dimuat.")

        # -------------------------------------------------
        # Persistent View
        # -------------------------------------------------

        try:
            bot.add_view(
                BoosterPanelView()
            )

            print("✅ Booster Panel persistent view berhasil dimuat.")

        except Exception as e:
            print(
                f"⚠️ Persistent view gagal dimuat: {e}"
            )

    except Exception as e:

        print(
            f"❌ Gagal memuat Booster Custom Role: {e}"
        )

        raise


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    print("")
    print("=" * 60)
    print("🤖 YOBLOX BOOSTER BOT")
    print("=" * 60)

    print(
        f"🤖 Bot       : {bot.user}"
    )

    print(
        f"🆔 Bot ID    : {bot.user.id}"
    )

    print(
        f"🌐 Server    : {len(bot.guilds)}"
    )

    print("=" * 60)

    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    setup_database()

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="YOBLOX Booster"
    )

    try:

        await bot.change_presence(
            status=discord.Status.online,
            activity=activity
        )

        print("✅ Status bot berhasil diatur.")

    except Exception as e:

        print(
            f"⚠️ Gagal mengatur status bot: {e}"
        )

    print("=" * 60)
    print("🟢 BOT ONLINE")
    print("=" * 60)


# =========================================================
# COMMAND ERROR
# =========================================================

@bot.event
async def on_command_error(
    ctx,
    error
):

    # Command tidak ditemukan
    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return

    # Permission error
    if isinstance(
        error,
        commands.MissingPermissions
    ):

        try:

            await ctx.send(
                "❌ Kamu tidak memiliki permission untuk menggunakan command ini.",
                delete_after=5
            )

        except Exception:
            pass

        return

    print(
        f"❌ Command Error: {error}"
    )


# =========================================================
# START
# =========================================================

async def main():

    # -----------------------------------------------------
    # Setup Booster sebelum login
    # -----------------------------------------------------

    await setup_booster()

    # -----------------------------------------------------
    # Jalankan bot
    # -----------------------------------------------------

    print("🔄 Menghubungkan bot ke Discord...")

    await bot.start(
        TOKEN
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "🛑 Bot dihentikan."
        )

    except Exception as e:

        print(
            f"❌ Fatal Error: {e}"
        )
