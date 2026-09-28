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

DONATUR_ROLE_ID = int(
    os.getenv("DONATUR_ROLE_ID", "0")
)

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


def can_use_custom_role(member: discord.Member):
    """
    Custom Role bisa digunakan oleh:
    - Server Booster
    - Administrator
    """

    return (
        member.premium_since is not None
        or member.guild_permissions.administrator
    )


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

    # =====================================================
    # PYCORD MODAL CALLBACK
    # =====================================================

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        member = interaction.user
        guild = interaction.guild

        # =================================================
        # CEK SERVER
        # =================================================

        if guild is None:

            await interaction.response.send_message(
                "❌ Fitur ini hanya bisa digunakan di server.",
                ephemeral=True
            )

            return

        # =================================================
        # CEK MEMBER
        # =================================================

        if not isinstance(
            member,
            discord.Member
        ):

            await interaction.response.send_message(
                "❌ Member tidak ditemukan.",
                ephemeral=True
            )

            return

        # =================================================
        # CEK AKSES
        # BOOSTER ATAU ADMIN
        # =================================================

        if not can_use_custom_role(member):

            await interaction.response.send_message(
                (
                    "❌ Fitur ini hanya dapat digunakan oleh "
                    "**Server Booster atau Administrator**."
                ),
                ephemeral=True
            )

            return

        # =================================================
        # CEK ROLE LAMA
        # =================================================

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

            # Database masih punya data,
            # tetapi role Discord sudah hilang.

            delete_booster_role(
                guild.id,
                member.id
            )

        # =================================================
        # CEK BOT
        # =================================================

        me = guild.me

        if me is None:

            await interaction.response.send_message(
                "❌ Bot tidak dapat membaca informasi server.",
                ephemeral=True
            )

            return

        # =================================================
        # MANAGE ROLES
        # =================================================

        if not me.guild_permissions.manage_roles:

            await interaction.response.send_message(
                (
                    "❌ Bot membutuhkan permission "
                    "**Manage Roles**."
                ),
                ephemeral=True
            )

            return

        # =================================================
        # NAMA ROLE
        # =================================================

        role_name = self.role_name.value.strip()

        if not role_name:

            await interaction.response.send_message(
                "❌ Nama role tidak boleh kosong.",
                ephemeral=True
            )

            return

        # =================================================
        # FILTER NAMA
        # =================================================

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

        # =================================================
        # PEMILIHAN WARNA
        # =================================================

        await interaction.response.send_message(

            content=(
                f"## 🎨 Custom Role\n\n"
                f"**Nama Role:** `{role_name}`\n\n"
                "Pilih **dua warna** untuk membuat gradient.\n\n"
                "🌈 **Warna 1** → warna awal gradient\n"
                "🌈 **Warna 2** → warna akhir gradient\n\n"
                "Setelah memilih keduanya, tekan **Submit**."
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

        # =================================================
        # COLOR SELECT 1
        # =================================================

        self.first_select = ColorSelect(
            "🌈 Pilih Warna Pertama",
            "booster_color_first"
        )

        # =================================================
        # COLOR SELECT 2
        # =================================================

        self.second_select = ColorSelect(
            "🌈 Pilih Warna Kedua",
            "booster_color_second"
        )

        # =================================================
        # CALLBACK
        # =================================================

        self.first_select.callback = (
            self.first_color_callback
        )

        self.second_select.callback = (
            self.second_color_callback
        )

        # =================================================
        # ADD SELECT
        # =================================================

        self.add_item(
            self.first_select
        )

        self.add_item(
            self.second_select
        )

    # =====================================================
    # WARNA 1
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
    # WARNA 2
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
    # PYCORD:
    # self, button, interaction
    # =====================================================

    @discord.ui.button(
        label="Submit",
        emoji="🌈",
        style=discord.ButtonStyle.success,
        custom_id="booster_submit_color"
    )
    async def submit(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):

        # =================================================
        # CEK USER
        # =================================================

        if interaction.user.id != self.member.id:

            await interaction.response.send_message(
                "❌ Menu ini bukan milik kamu.",
                ephemeral=True
            )

            return

        # =================================================
        # CEK WARNA
        # =================================================

        if not self.color_1:

            await interaction.response.send_message(
                "❌ Silakan pilih **Warna 1** terlebih dahulu.",
                ephemeral=True
            )

            return

        if not self.color_2:

            await interaction.response.send_message(
                "❌ Silakan pilih **Warna 2** terlebih dahulu.",
                ephemeral=True
            )

            return

        # =================================================
        # SERVER
        # =================================================

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ Server tidak ditemukan.",
                ephemeral=True
            )

            return

        # =================================================
        # MEMBER
        # =================================================

        member = guild.get_member(
            self.member.id
        )

        if member is None:

            await interaction.response.send_message(
                "❌ Member tidak ditemukan.",
                ephemeral=True
            )

            return

        # =================================================
        # CEK AKSES LAGI
        # =================================================

        if not can_use_custom_role(member):

            await interaction.response.send_message(
                (
                    "❌ Kamu harus menjadi "
                    "**Server Booster atau Administrator**."
                ),
                ephemeral=True
            )

            return

        # =================================================
        # CEK ROLE EXISTING
        # =================================================

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

            delete_booster_role(
                guild.id,
                member.id
            )

        # =================================================
        # BOT
        # =================================================

        me = guild.me

        if me is None:

            await interaction.response.send_message(
                "❌ Bot tidak ditemukan.",
                ephemeral=True
            )

            return

        # =================================================
        # MANAGE ROLES
        # =================================================

        if not me.guild_permissions.manage_roles:

            await interaction.response.send_message(
                (
                    "❌ Bot tidak memiliki permission "
                    "**Manage Roles**."
                ),
                ephemeral=True
            )

            return

        # =================================================
        # CREATE GRADIENT ROLE
        # =================================================

        try:

            primary_color = get_color(
                self.color_1
            )

            secondary_color = get_color(
                self.color_2
            )

            # =================================================
            # GRADIENT
            #
            # Pycord menggunakan RoleColours:
            #
            # primary   = warna pertama
            # secondary = warna kedua
            # =================================================

            gradient_colors = discord.RoleColours(
                primary=primary_color,
                secondary=secondary_color
            )

            # =================================================
            # CREATE ROLE
            # =================================================

            role = await guild.create_role(

                name=self.role_name,

                colors=gradient_colors,

                reason=(
                    "Booster Custom Gradient Role - "
                    f"{member} ({member.id})"
                )

            )

            # =================================================
            # POSISI ROLE
            # =================================================

            donatur_role = get_donatur_role(
                guild
            )

            if donatur_role:

                target_position = (
                    donatur_role.position + 1
                )

                # Bot harus berada di atas role
                if (
                    target_position
                    < me.top_role.position
                ):

                    await role.edit(

                        position=target_position,

                        reason=(
                            "Custom Gradient Role Position"
                        )

                    )

            else:

                # Jika Donatur Role tidak ditemukan,
                # letakkan di bawah role tertinggi bot.

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
                            "Custom Gradient Role Position"
                        )

                    )

            # =================================================
            # TAMBAHKAN KE MEMBER
            # =================================================

            await member.add_roles(

                role,

                reason=(
                    "Booster Custom Gradient Role"
                )

            )

            # =================================================
            # SIMPAN DATABASE
            #
            # Database kamu sekarang menggunakan:
            # guild_id, user_id, role_id
            # =================================================

            save_booster_role(

                guild.id,

                member.id,

                role.id

            )

            # =================================================
            # SUCCESS
            # =================================================

            await interaction.response.edit_message(

                content=(

                    "## 🌈 Custom Gradient Role Berhasil!\n\n"

                    f"🎨 **Role:** {role.mention}\n\n"

                    f"🟣 **Warna 1:** {self.color_1}\n"

                    f"🟢 **Warna 2:** {self.color_2}\n\n"

                    "✨ Role kamu sekarang menggunakan "
                    "**Gradient Style**.\n\n"

                    "Role sudah diberikan kepada kamu."

                ),

                view=None

            )

        # =================================================
        # PERMISSION / ENHANCED ROLE STYLE ERROR
        # =================================================

        except discord.Forbidden:

            await interaction.response.send_message(

                (
                    "❌ Discord menolak pembuatan Gradient Role.\n\n"
                    "Pastikan bot memiliki **Manage Roles** "
                    "dan server sudah mengaktifkan "
                    "**Enhanced Role Styles**."
                ),

                ephemeral=True

            )

        # =================================================
        # HTTP ERROR
        # =================================================

        except discord.HTTPException as e:

            print(
                f"❌ Discord HTTP Error: {e}"
            )

            await interaction.response.send_message(

                (
                    "❌ Gradient Role gagal dibuat.\n\n"
                    "Pastikan **Enhanced Role Styles** "
                    "sudah aktif di server."
                ),

                ephemeral=True

            )

        # =================================================
        # ERROR LAIN
        # =================================================

        except Exception as e:

            print(
                f"❌ Gradient Role Error: {e}"
            )

            await interaction.response.send_message(

                (
                    "❌ Terjadi kesalahan saat membuat "
                    "Gradient Role."
                ),

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

        # =================================================
        # SERVER
        # =================================================

        if guild is None:

            await interaction.response.send_message(
                "❌ Hanya bisa digunakan di server.",
                ephemeral=True
            )

            return

        # =================================================
        # MEMBER
        # =================================================

        if not isinstance(
            member,
            discord.Member
        ):

            await interaction.response.send_message(
                "❌ Member tidak ditemukan.",
                ephemeral=True
            )

            return

        # =================================================
        # AKSES
        # =================================================

        if not can_use_custom_role(member):

            await interaction.response.send_message(
                (
                    "❌ Fitur ini hanya untuk "
                    "**Server Booster atau Administrator**."
                ),
                ephemeral=True
            )

            return

        # =================================================
        # CEK ROLE EXISTING
        # =================================================

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

            delete_booster_role(
                guild.id,
                member.id
            )

        # =================================================
        # BUKA MODAL
        # =================================================

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

        # =================================================
        # SERVER
        # =================================================

        if guild is None:

            await interaction.response.send_message(
                "❌ Hanya bisa digunakan di server.",
                ephemeral=True
            )

            return

        # =================================================
        # AKSES
        # =================================================

        if not can_use_custom_role(member):

            await interaction.response.send_message(
                (
                    "❌ Fitur ini hanya untuk "
                    "**Server Booster atau Administrator**."
                ),
                ephemeral=True
            )

            return

        # =================================================
        # DATABASE
        # =================================================

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

        # =================================================
        # DELETE
        # =================================================

        try:

            role = guild.get_role(
                int(existing["role_id"])
            )

            if role:

                # =================================================
                # HIERARCHY
                # =================================================

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

                # =================================================
                # DELETE ROLE
                # =================================================

                await role.delete(

                    reason=(
                        "Custom Gradient Role deleted by "
                        f"{member}"
                    )

                )

            # =================================================
            # DELETE DATABASE
            # =================================================

            delete_booster_role(

                guild.id,

                member.id

            )

            # =================================================
            # SUCCESS
            # =================================================

            await interaction.response.send_message(

                "✅ Custom Role kamu berhasil dihapus.",

                ephemeral=True

            )

        # =================================================
        # FORBIDDEN
        # =================================================

        except discord.Forbidden:

            await interaction.response.send_message(

                (
                    "❌ Bot tidak memiliki permission "
                    "untuk menghapus role tersebut."
                ),

                ephemeral=True

            )

        # =================================================
        # ERROR
        # =================================================

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
    # SETUP PANEL
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

        # =================================================
        # EMBED
        # =================================================

        embed = discord.Embed(

            title="🚀 Booster Custom Role",

            description=(

                "Sebagai bentuk apresiasi untuk kamu "
                "yang telah membantu support **YOBLOX** "
                "dengan melakukan Boost Server, kamu "
                "mendapatkan akses untuk membuat "
                "Custom Role sendiri.\n\n"

                "✨ **FITUR**\n"

                "• Buat Custom Role\n"
                "• Gradient dua warna 🌈\n"
                "• Pilih warna pertama\n"
                "• Pilih warna kedua\n"
                "• Server Booster dapat menggunakan fitur\n"
                "• Administrator dapat menggunakan fitur\n"
                "• Hapus Custom Role sendiri\n"
                "• 1 member hanya dapat memiliki 1 role\n\n"

                "📜 **KETENTUAN**\n"

                "1. Custom Role tersedia untuk "
                "**Server Booster dan Administrator**.\n\n"

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

                "🌈 Gunakan dua warna untuk membuat "
                "**Gradient Role** yang unik!"

            ),

            colour=discord.Colour.gold()

        )

        # =================================================
        # FOOTER
        # =================================================

        embed.set_footer(

            text=(
                "YOBLOX • Booster Custom Role"
            )

        )

        # =================================================
        # SEND
        # =================================================

        await ctx.send(

            embed=embed,

            view=BoosterPanelView()

        )

        # =================================================
        # DELETE COMMAND
        # =================================================

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

    # Kompatibel dengan Pycord
    # maupun environment yang membuat
    # add_cog menjadi coroutine.

    if hasattr(
        result,
        "__await__"
    ):

        await result

    # =================================================
    # PERSISTENT VIEW
    # =================================================

    bot.add_view(
        BoosterPanelView()
    )

    print(
        "✅ Booster Custom Role aktif."
    )
