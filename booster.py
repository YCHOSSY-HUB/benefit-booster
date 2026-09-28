import os
import discord
from discord.ext import commands

from database import (
    get_booster_role,
    save_booster_role,
    delete_booster_role
)


# =========================================================
# CONFIG
# =========================================================

# ID ROLE DONATUR
# Railway Variable:
# DONATUR_ROLE_ID=123456789012345678

DONATUR_ROLE_ID = int(
    os.getenv("DONATUR_ROLE_ID", "0")
)


# ID CHANNEL TEMPAT PANEL
# Railway Variable:
# BOOSTER_CHANNEL_ID=123456789012345678

BOOSTER_CHANNEL_ID = int(
    os.getenv("BOOSTER_CHANNEL_ID", "0")
)


# =========================================================
# WARNA
# =========================================================

COLORS = {
    "Hitam": discord.Colour.from_rgb(0, 0, 0),
    "Putih": discord.Colour.from_rgb(255, 255, 255),
    "Merah": discord.Colour.from_rgb(237, 66, 69),
    "Biru": discord.Colour.from_rgb(52, 152, 219),
    "Hijau": discord.Colour.from_rgb(46, 204, 113),
    "Kuning": discord.Colour.from_rgb(241, 196, 15),
    "Ungu": discord.Colour.from_rgb(155, 89, 182),
    "Pink": discord.Colour.from_rgb(255, 105, 180),
    "Orange": discord.Colour.from_rgb(230, 126, 34),
    "Cyan": discord.Colour.from_rgb(26, 188, 156),
}


# =========================================================
# HELPER
# =========================================================

def get_color(name: str):

    return COLORS.get(
        name,
        discord.Colour.default()
    )


def is_booster(member: discord.Member):

    return member.premium_since is not None


def get_donatur_role(guild: discord.Guild):

    if DONATUR_ROLE_ID == 0:
        return None

    return guild.get_role(
        DONATUR_ROLE_ID
    )


# =========================================================
# CREATE ROLE MODAL
# =========================================================

class CreateRoleModal(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="Buat Custom Role"
        )

        self.role_name = discord.ui.TextInput(
            label="Nama Role",
            placeholder="Isi nama role yang ingin dibuat",
            required=True,
            min_length=1,
            max_length=100
        )

        self.add_item(
            self.role_name
        )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        member = interaction.user
        guild = interaction.guild

        # -------------------------------------------------
        # CEK SERVER
        # -------------------------------------------------

        if guild is None:

            await interaction.response.send_message(
                "❌ Fitur ini hanya bisa digunakan di server.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CEK MEMBER
        # -------------------------------------------------

        if not isinstance(
            member,
            discord.Member
        ):

            await interaction.response.send_message(
                "❌ Member tidak ditemukan.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CEK BOOSTER
        # -------------------------------------------------

        if not is_booster(member):

            await interaction.response.send_message(
                "❌ Kamu harus menjadi **Server Booster YOBLOX** terlebih dahulu.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CEK ROLE LAMA
        # -------------------------------------------------

        existing = get_booster_role(
            guild.id,
            member.id
        )

        if existing:

            existing_role = guild.get_role(
                int(existing["role_id"])
            )

            if existing_role:

                await interaction.response.send_message(
                    (
                        "❌ Kamu sudah memiliki Custom Role: "
                        f"{existing_role.mention}"
                    ),
                    ephemeral=True
                )

                return

            # Data database ada,
            # tetapi role Discord sudah tidak ada.

            delete_booster_role(
                guild.id,
                member.id
            )

        # -------------------------------------------------
        # CEK BOT
        # -------------------------------------------------

        me = guild.me

        if me is None:

            await interaction.response.send_message(
                "❌ Bot tidak dapat membaca informasi server.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CEK MANAGE ROLE
        # -------------------------------------------------

        if not me.guild_permissions.manage_roles:

            await interaction.response.send_message(
                "❌ Bot membutuhkan permission **Manage Roles**.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # NAMA ROLE
        # -------------------------------------------------

        role_name = self.role_name.value.strip()

        if not role_name:

            await interaction.response.send_message(
                "❌ Nama role tidak boleh kosong.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # FILTER NAMA
        # -------------------------------------------------

        forbidden_words = [

            "admin",
            "administrator",
            "moderator",
            "mod",
            "staff",
            "owner",
            "developer",
            "dev",
            "management",
            "security",
            "support"

        ]

        lower_name = role_name.lower()

        for word in forbidden_words:

            if word in lower_name:

                await interaction.response.send_message(
                    "❌ Nama role tersebut tidak diperbolehkan.",
                    ephemeral=True
                )

                return

        # -------------------------------------------------
        # COLOR SELECTION
        # -------------------------------------------------

        await interaction.response.send_message(

            content=(
                f"**Nama Role:** {role_name}\n\n"
                "🎨 **Pilih Warna Pertama**\n"
                "🎨 **Pilih Warna Kedua**\n\n"
                "Silakan pilih kedua warna, "
                "kemudian tekan **Submit**."
            ),

            view=ColorSelectionView(
                member=member,
                role_name=role_name
            ),

            ephemeral=True
        )


# =========================================================
# COLOR SELECT
# =========================================================

class ColorSelect(
    discord.ui.Select
):

    def __init__(
        self,
        placeholder,
        select_id
    ):

        options = []

        for name in COLORS:

            options.append(
                discord.SelectOption(
                    label=name,
                    value=name
                )
            )

        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options,
            custom_id=select_id
        )


# =========================================================
# COLOR SELECTION VIEW
# =========================================================

class ColorSelectionView(
    discord.ui.View
):

    def __init__(
        self,
        member: discord.Member,
        role_name: str
    ):

        super().__init__(
            timeout=300
        )

        self.member = member
        self.role_name = role_name

        self.color_1 = None
        self.color_2 = None

        # -------------------------------------------------
        # SELECT WARNA 1
        # -------------------------------------------------

        self.first_select = ColorSelect(
            "Pilih Warna Pertama",
            "booster_color_first"
        )

        # -------------------------------------------------
        # SELECT WARNA 2
        # -------------------------------------------------

        self.second_select = ColorSelect(
            "Pilih Warna Kedua",
            "booster_color_second"
        )

        # -------------------------------------------------
        # CALLBACK
        # -------------------------------------------------

        self.first_select.callback = (
            self.first_color_callback
        )

        self.second_select.callback = (
            self.second_color_callback
        )

        # -------------------------------------------------
        # ADD SELECT
        # -------------------------------------------------

        self.add_item(
            self.first_select
        )

        self.add_item(
            self.second_select
        )

    # =====================================================
    # WARNA PERTAMA
    # =====================================================

    async def first_color_callback(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.member.id:

            await interaction.response.send_message(
                "❌ Menu ini bukan milik kamu.",
                ephemeral=True
            )

            return

        self.color_1 = (
            self.first_select.values[0]
        )

        await interaction.response.defer()

    # =====================================================
    # WARNA KEDUA
    # =====================================================

    async def second_color_callback(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.member.id:

            await interaction.response.send_message(
                "❌ Menu ini bukan milik kamu.",
                ephemeral=True
            )

            return

        self.color_2 = (
            self.second_select.values[0]
        )

        await interaction.response.defer()

    # =====================================================
    # SUBMIT
    #
    # PENTING:
    # Pycord menggunakan:
    #
    # self, button, interaction
    #
    # bukan:
    #
    # self, interaction, button
    # =====================================================

    @discord.ui.button(
        label="Submit",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="booster_submit_color"
    )
    async def submit(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):

        # -------------------------------------------------
        # CEK USER
        # -------------------------------------------------

        if interaction.user.id != self.member.id:

            await interaction.response.send_message(
                "❌ Menu ini bukan milik kamu.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CEK WARNA
        # -------------------------------------------------

        if not self.color_1 or not self.color_2:

            await interaction.response.send_message(
                "❌ Silakan pilih **kedua warna** terlebih dahulu.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CEK GUILD
        # -------------------------------------------------

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ Server tidak ditemukan.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CEK MEMBER
        # -------------------------------------------------

        member = guild.get_member(
            self.member.id
        )

        if member is None:

            await interaction.response.send_message(
                "❌ Member tidak ditemukan.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CEK BOOSTER LAGI
        # -------------------------------------------------

        if not is_booster(member):

            await interaction.response.send_message(
                "❌ Kamu sudah tidak menjadi Server Booster.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CEK ROLE DATABASE
        # -------------------------------------------------

        existing = get_booster_role(
            guild.id,
            member.id
        )

        if existing:

            existing_role = guild.get_role(
                int(existing["role_id"])
            )

            if existing_role:

                await interaction.response.send_message(
                    (
                        "❌ Kamu sudah memiliki Custom Role: "
                        f"{existing_role.mention}"
                    ),
                    ephemeral=True
                )

                return

        # -------------------------------------------------
        # CEK BOT
        # -------------------------------------------------

        me = guild.me

        if me is None:

            await interaction.response.send_message(
                "❌ Bot tidak ditemukan.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # MANAGE ROLE
        # -------------------------------------------------

        if not me.guild_permissions.manage_roles:

            await interaction.response.send_message(
                "❌ Bot tidak memiliki permission **Manage Roles**.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CREATE ROLE
        # -------------------------------------------------

        try:

            color_1 = get_color(
                self.color_1
            )

            color_2 = get_color(
                self.color_2
            )

            # -------------------------------------------------
            # Discord saat ini menggunakan satu warna utama
            # untuk role biasa.
            #
            # Kita gunakan warna pertama sebagai warna utama.
            # Warna kedua tetap disimpan sebagai pilihan user.
            # -------------------------------------------------

            final_color = color_1

            role = await guild.create_role(

                name=self.role_name,

                colour=final_color,

                reason=(
                    "Booster Custom Role - "
                    f"{member} ({member.id})"
                )

            )

            # -------------------------------------------------
            # POSISI ROLE
            # -------------------------------------------------

            donatur_role = get_donatur_role(
                guild
            )

            if donatur_role:

                target_position = (
                    donatur_role.position + 1
                )

                if (
                    target_position
                    < me.top_role.position
                ):

                    await role.edit(

                        position=target_position,

                        reason=(
                            "Booster Custom Role Position"
                        )

                    )

            else:

                target_position = max(
                    1,
                    me.top_role.position - 1
                )

                if (
                    target_position
                    < me.top_role.position
                ):

                    await role.edit(

                        position=target_position,

                        reason=(
                            "Booster Custom Role Position"
                        )

                    )

            # -------------------------------------------------
            # TAMBAHKAN ROLE
            # -------------------------------------------------

            await member.add_roles(

                role,

                reason=(
                    "Booster Custom Role"
                )

            )

            # -------------------------------------------------
            # SIMPAN DATABASE
            #
            # database.py kamu menerima:
            #
            # save_booster_role(
            #     guild_id,
            #     user_id,
            #     role_id
            # )
            #
            # Jadi jangan kirim role_name/color di sini.
            # -------------------------------------------------

            save_booster_role(

                guild.id,

                member.id,

                role.id

            )

            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            await interaction.response.edit_message(

                content=(

                    "## ✅ Custom Role Berhasil Dibuat!\n\n"

                    f"🎨 **Nama:** {role.mention}\n"

                    f"🔹 **Warna 1:** {self.color_1}\n"

                    f"🔹 **Warna 2:** {self.color_2}\n\n"

                    "Role sudah diberikan kepada kamu."

                ),

                view=None

            )

        # -------------------------------------------------
        # PERMISSION ERROR
        # -------------------------------------------------

        except discord.Forbidden:

            await interaction.response.send_message(

                (
                    "❌ Bot tidak memiliki permission "
                    "yang cukup untuk membuat atau "
                    "mengatur role."
                ),

                ephemeral=True

            )

        # -------------------------------------------------
        # DISCORD ERROR
        # -------------------------------------------------

        except discord.HTTPException as e:

            print(
                f"❌ Discord HTTP Error: {e}"
            )

            await interaction.response.send_message(

                "❌ Terjadi kesalahan saat membuat Custom Role.",

                ephemeral=True

            )

        # -------------------------------------------------
        # ERROR LAIN
        # -------------------------------------------------

        except Exception as e:

            print(
                f"❌ Create Role Error: {e}"
            )

            await interaction.response.send_message(

                "❌ Terjadi kesalahan internal.",

                ephemeral=True

            )


# =========================================================
# BOOSTER PANEL
# =========================================================

class BoosterPanelView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    # =====================================================
    # BUAT ROLE
    #
    # PENTING:
    # Pycord:
    # self, button, interaction
    # =====================================================

    @discord.ui.button(
        label="Buat Role",
        emoji="🎨",
        style=discord.ButtonStyle.success,
        custom_id="booster_create_role"
    )
    async def create_role(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):

        member = interaction.user
        guild = interaction.guild

        # -------------------------------------------------
        # CEK SERVER
        # -------------------------------------------------

        if guild is None:

            await interaction.response.send_message(
                "❌ Hanya bisa digunakan di server.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CEK MEMBER
        # -------------------------------------------------

        if not isinstance(
            member,
            discord.Member
        ):

            await interaction.response.send_message(
                "❌ Member tidak ditemukan.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # BOOSTER CHECK
        # -------------------------------------------------

        if not is_booster(member):

            await interaction.response.send_message(
                (
                    "❌ Fitur ini hanya untuk "
                    "**Server Booster YOBLOX**."
                ),
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CEK ROLE EXISTING
        # -------------------------------------------------

        existing = get_booster_role(
            guild.id,
            member.id
        )

        if existing:

            existing_role = guild.get_role(
                int(existing["role_id"])
            )

            if existing_role:

                await interaction.response.send_message(

                    (
                        "❌ Kamu sudah memiliki Custom Role: "
                        f"{existing_role.mention}"
                    ),

                    ephemeral=True

                )

                return

            # Database ada,
            # role Discord sudah hilang.

            delete_booster_role(
                guild.id,
                member.id
            )

        # -------------------------------------------------
        # OPEN MODAL
        # -------------------------------------------------

        await interaction.response.send_modal(
            CreateRoleModal()
        )

    # =====================================================
    # HAPUS ROLE
    # =====================================================

    @discord.ui.button(
        label="Hapus Role",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        custom_id="booster_delete_role"
    )
    async def delete_role(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):

        member = interaction.user
        guild = interaction.guild

        # -------------------------------------------------
        # CEK SERVER
        # -------------------------------------------------

        if guild is None:

            await interaction.response.send_message(
                "❌ Hanya bisa digunakan di server.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CEK DATABASE
        # -------------------------------------------------

        existing = get_booster_role(
            guild.id,
            member.id
        )

        if not existing:

            await interaction.response.send_message(
                "❌ Kamu tidak memiliki Custom Role.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # DELETE
        # -------------------------------------------------

        try:

            role = guild.get_role(
                int(existing["role_id"])
            )

            if role:

                # -------------------------------------------------
                # CEK POSISI ROLE
                # -------------------------------------------------

                if (
                    guild.me
                    and role >= guild.me.top_role
                ):

                    await interaction.response.send_message(

                        (
                            "❌ Bot tidak bisa menghapus "
                            "role tersebut karena posisi "
                            "role terlalu tinggi."
                        ),

                        ephemeral=True

                    )

                    return

                # -------------------------------------------------
                # HAPUS ROLE DISCORD
                # -------------------------------------------------

                await role.delete(

                    reason=(

                        "Booster Custom Role deleted by "

                        f"{member}"

                    )

                )

            # -------------------------------------------------
            # HAPUS DATABASE
            # -------------------------------------------------

            delete_booster_role(

                guild.id,

                member.id

            )

            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            await interaction.response.send_message(

                "✅ Custom Role kamu berhasil dihapus.",

                ephemeral=True

            )

        # -------------------------------------------------
        # FORBIDDEN
        # -------------------------------------------------

        except discord.Forbidden:

            await interaction.response.send_message(

                (
                    "❌ Bot tidak memiliki permission "
                    "untuk menghapus role tersebut."
                ),

                ephemeral=True

            )

        # -------------------------------------------------
        # ERROR
        # -------------------------------------------------

        except Exception as e:

            print(
                f"❌ Delete Role Error: {e}"
            )

            await interaction.response.send_message(

                (
                    "❌ Terjadi kesalahan "
                    "saat menghapus role."
                ),

                ephemeral=True

            )


# =========================================================
# BOOSTER COG
# =========================================================

class Booster(
    commands.Cog
):

    def __init__(
        self,
        bot: commands.Bot
    ):

        self.bot = bot

    # =====================================================
    # SETUP BOOSTER PANEL
    # =====================================================

    @commands.command(
        name="setupbooster"
    )
    @commands.has_permissions(
        administrator=True
    )
    async def setupbooster(
        self,
        ctx: commands.Context
    ):

        # -------------------------------------------------
        # EMBED
        # -------------------------------------------------

        embed = discord.Embed(

            title="🚀 Booster Custom Role",

            description=(

                "Sebagai bentuk apresiasi untuk kamu "
                "yang telah membantu support **YOBLOX** "
                "dengan melakukan Boost Server, kamu "
                "mendapatkan akses untuk membuat "
                "Custom Role sendiri.\n\n"

                "✨ **FITUR**\n"

                "• Buat role dengan nama pilihanmu\n"

                "• Pilih dua warna untuk Custom Role\n"

                "• Custom Role khusus Server Booster\n"

                "• Bisa menghapus role sendiri\n"

                "• 1 member hanya dapat memiliki "
                "1 Custom Role\n\n"

                "📜 **KETENTUAN**\n"

                "1. Custom Role hanya tersedia selama "
                "kamu menjadi **Server Booster YOBLOX**.\n\n"

                "2. Dilarang menggunakan nama yang "
                "mengandung unsur **SARA, penghinaan, "
                "seksual, atau provokasi**.\n\n"

                "3. Dilarang membuat role yang menyerupai "
                "**Admin, Moderator, atau Staff YOBLOX**.\n\n"

                "4. Dilarang menggunakan Custom Role "
                "untuk kegiatan **jual beli atau "
                "perdagangan**.\n\n"

                "⚠️ Role yang melanggar ketentuan dapat "
                "**dihapus tanpa pemberitahuan**.\n\n"

                "💎 Terima kasih sudah support "
                "**YOBLOX** dengan Boost Server!"

            ),

            colour=discord.Colour.gold()

        )

        # -------------------------------------------------
        # FOOTER
        # -------------------------------------------------

        embed.set_footer(

            text=(
                "YOBLOX • Booster Custom Role"
            )

        )

        # -------------------------------------------------
        # SEND PANEL
        # -------------------------------------------------

        await ctx.send(

            embed=embed,

            view=BoosterPanelView()

        )

        # -------------------------------------------------
        # HAPUS COMMAND
        # -------------------------------------------------

        try:

            await ctx.message.delete()

        except Exception:

            pass

    # =====================================================
    # COMMAND ERROR
    # =====================================================

    @setupbooster.error
    async def setupbooster_error(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            await ctx.send(

                (
                    "❌ Kamu harus memiliki "
                    "**Administrator**."
                ),

                delete_after=5

            )

        else:

            print(
                f"❌ setupbooster error: {error}"
            )


# =========================================================
# EXTENSION SETUP
# =========================================================

async def setup(
    bot
):

    result = bot.add_cog(
        Booster(bot)
    )

    # Kompatibel jika add_cog mengembalikan coroutine
    if hasattr(
        result,
        "__await__"
    ):

        await result

    # Persistent Panel
    bot.add_view(
        BoosterPanelView()
    )

    print(
        "✅ Booster Custom Role aktif."
    )
