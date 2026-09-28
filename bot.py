import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from database import init_database


# =========================================================
# LOAD ENV
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
# LOAD EXTENSIONS
# =========================================================

async def load_extensions():

    print("=" * 50)
    print("🔄 Memuat extension...")
    print("=" * 50)

    try:

        await bot.load_extension("booster")

        print(
            "✅ booster.py berhasil dimuat."
        )

    except Exception as e:

        print(
            "❌ GAGAL memuat booster.py!"
        )

        print(
            f"❌ Error: {type(e).__name__}: {e}"
        )

        raise


    # =====================================================
    # CEK COMMAND YANG TERDAFTAR
    # =====================================================

    print("=" * 50)
    print("📋 COMMAND YANG TERDAFTAR")
    print("=" * 50)

    if not bot.commands:

        print(
            "⚠️ TIDAK ADA COMMAND YANG TERDAFTAR!"
        )

    else:

        for command in bot.commands:

            print(
                f"   !{command.name}"
            )

    print("=" * 50)


# =========================================================
# ON MESSAGE
# =========================================================
#
# Kita proses command prefix secara manual.
#
# !setupbooster
#
# akan diproses oleh:
#
# bot.process_commands(message)
# =========================================================

@bot.event
async def on_message(
    message: discord.Message
):

    # Jangan proses pesan dari bot

    if message.author.bot:
        return


    # =====================================================
    # DEBUG MESSAGE
    # =====================================================

    print(
        f"📩 Message masuk | "
        f"{message.author} | "
        f"{message.content}"
    )


    # =====================================================
    # PROCESS PREFIX COMMAND
    # =====================================================

    await bot.process_commands(
        message
    )


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    print()
    print("=" * 50)
    print("🤖 BOT ONLINE")
    print("=" * 50)

    print(
        f"🤖 Bot       : {bot.user}"
    )

    print(
        f"🆔 Bot ID    : {bot.user.id}"
    )

    print(
        f"🌐 Server    : {len(bot.guilds)}"
    )

    print(
        f"📋 Commands  : {len(bot.commands)}"
    )

    print("=" * 50)


    # =====================================================
    # DATABASE
    # =====================================================

    try:

        init_database()

        print(
            "✅ Database berhasil diinisialisasi."
        )

    except Exception as e:

        print(
            f"❌ Database Error: {e}"
        )


    # =====================================================
    # STATUS BOT
    # =====================================================

    activity = discord.Activity(

        type=discord.ActivityType.watching,

        name="YOBLOX Booster"

    )


    await bot.change_presence(

        status=discord.Status.online,

        activity=activity

    )


# =========================================================
# COMMAND ERROR
# =========================================================

@bot.event
async def on_command_error(
    ctx: commands.Context,
    error
):

    # =====================================================
    # COMMAND TIDAK DITEMUKAN
    # =====================================================

    if isinstance(
        error,
        commands.CommandNotFound
    ):

        print(
            f"⚠️ Command tidak ditemukan: "
            f"{ctx.message.content}"
        )

        return


    # =====================================================
    # TIDAK PUNYA PERMISSION
    # =====================================================

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        print(
            f"⚠️ Tidak memiliki permission: "
            f"{ctx.author}"
        )

        await ctx.send(
            "❌ Kamu tidak memiliki permission untuk menggunakan command ini.",
            delete_after=5
        )

        return


    # =====================================================
    # ERROR COMMAND
    # =====================================================

    print(
        f"❌ Command Error: "
        f"{type(error).__name__}: {error}"
    )


# =========================================================
# START BOT
# =========================================================

async def main():

    async with bot:

        await load_extensions()

        print(
            "🚀 Menjalankan bot..."
        )

        await bot.start(
            TOKEN
        )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    import asyncio

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "🛑 Bot dihentikan."
        )