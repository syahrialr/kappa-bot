import discord
from discord import app_commands
from discord.errors import Forbidden
import aiohttp
from typing import List, Optional
from datetime import datetime
import asyncio
import os

# =========================
# HELPER: CEK EMBED
# =========================
def embed_contains(embed: discord.Embed, keyword: str) -> bool:
    keyword = keyword.lower()

    if embed.title and keyword in embed.title.lower():
        return True

    if embed.description and keyword in embed.description.lower():
        return True

    # ✅ TAMBAHAN PENTING
    if embed.author and embed.author.name:
        if keyword in embed.author.name.lower():
            return True

    for field in embed.fields:
        if keyword in field.name.lower():
            return True
        if keyword in field.value.lower():
            return True

    if embed.footer and embed.footer.text:
        if keyword in embed.footer.text.lower():
            return True

    return False

# =========================
# HELPER: HAPUS THREAD SETELAH DELAY
# =========================
async def delete_thread_later(thread: discord.Thread, delay: int):
    await asyncio.sleep(delay)
    try:
        await thread.delete()
    except (discord.NotFound, discord.Forbidden):
        pass

async def auto_delete_message(msg, delay):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except (discord.NotFound, discord.Forbidden):
        pass



# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN") 
API_ALL = os.getenv("API_ALL", "https://weao.xyz/api/status/exploits") 
intents = discord.Intents.default()
intents.message_content = True  # ⬅️ WAJIB untuk baca isi chat
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# =========================
# UTIL FUNCTIONS
# =========================
def chunk_list(items: List[str], size: int = 15):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def detection_status(data: dict) -> str:
    clientmods = data.get("clientmods")

    # kalau list dan ada isinya
    if isinstance(clientmods, list) and len(clientmods) > 0:
        return "Client mod bypass"

    # kalau boolean true
    if clientmods is True:
        return "Client mod bypass"

    if data.get("detected") is False:
        return "Undetected"

    return "Detected"



# =========================
# DYNAMIC BUTTON VIEW
# =========================
class ExploitLinkButtons(discord.ui.View):
    def __init__(self, website_url: Optional[str], discord_url: Optional[str]):
        super().__init__(timeout=None)

        if website_url:
            self.add_item(
                discord.ui.Button(
                    label="Website",
                    url=website_url,
                    style=discord.ButtonStyle.link,
                    emoji="🌐"
                )
            )

        if discord_url:
            self.add_item(
                discord.ui.Button(
                    label="Discord",
                    url=discord_url,
                    style=discord.ButtonStyle.link,
                    emoji="💬"
                )
            )


# =========================
# FETCH API (ANTI 403)
# =========================
async def fetch_all_exploits():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Referer": "https://weao.xyz/",
        "Origin": "https://weao.xyz",
    }

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        async with session.get(API_ALL) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(f"API status {resp.status}: {text[:200]}")
            return await resp.json()


# =========================
# BOT READY
# =========================
@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="/status")
    )
    await tree.sync()
    print(f"✅ Bot online sebagai {client.user}")


# =========================
# /status COMMAND
# =========================
@tree.command(name="status", description="Cek status exploit (semua / spesifik)")
@app_commands.describe(exploit="Nama exploit (opsional)")
async def status(interaction: discord.Interaction, exploit: str = None):
    await interaction.response.defer(thinking=True)

    try:
        data_all = await fetch_all_exploits()

        # ==================================================
        # SINGLE EXPLOIT
        # ==================================================
        if exploit:
            exploit = exploit.lower()
            data = next(
                (e for e in data_all if exploit in e.get("title", "").lower()),
                None
            )

            if not data:
                await interaction.followup.send("❌ Exploit tidak ditemukan")
                return

            # ===== STATUS =====
            status_icon = "✅" if data.get("updateStatus") else "❌"
            status_text = "Updated" if data.get("updateStatus") else "Down"

            embed = discord.Embed(
                title=data.get("title", "Unknown"),
                color=discord.Color.green() if data.get("updateStatus") else discord.Color.red()
            )

            # ===== DETAILS (SEJAJAR PAKAI :) =====
            details = (
                f"**Status**      : {status_icon} {status_text}\n"
                f"**Version**     : {data.get('version', '-')}\n"
                f"**Updated**     : {data.get('updatedDate', '-')}\n"
                f"**Cost**        : {'Free' if data.get('free') else 'Paid'}\n"
                f"**Keysystem**   : {'Yes' if data.get('keysystem') else 'No'}\n"
                f"**sUNC**        : {data.get('suncPercentage', 0)}%\n"
                f"**Detection**   : {detection_status(data)}"
            )

            embed.add_field(
                name="",
                value=details,
                inline=False
            )

            # ===== LOGO =====
            logo = data.get("slug", {}).get("logo")
            if logo:
                embed.set_thumbnail(url=logo)

            # ===== FOOTER =====
            now = datetime.now().strftime("%H:%M")
            embed.set_footer(text=f"Powered by weao.xyz • {now}")

            # ===== URL DARI API (SINGLE EXPLOIT SAJA) =====
            website_url = data.get("websitelink")
            discord_url = data.get("discordlink")

            await interaction.followup.send(
                embed=embed,
                view=ExploitLinkButtons(
                    website_url=website_url,
                    discord_url=discord_url
                )
            )
            return


        # ==================================================
        # ALL EXPLOITS (FINAL — NO CONT, ICON BELAKANG)
        # ==================================================
        sections = {
            "🪟 Windows Exploits": [],
            "🤖 Android Exploits": []
        }

        for e in data_all:
            platform = e.get("platform", "").lower()
            etype = e.get("extype", "").lower()

            if platform == "mac":
                continue
            if platform == "windows" and "external" in etype:
                continue

            title = e.get("title", "Unknown")
            version = e.get("version", "-")
            icon = "✅" if e.get("updateStatus") else "❌"

            line = f"**{title}** | `{version}` | {icon}"

            if platform == "windows":
                sections["🪟 Windows Exploits"].append(line)
            elif platform == "android":
                sections["🤖 Android Exploits"].append(line)

        embed = discord.Embed(
            title="WhatExpsAre.Online | Exploit Status",
            color=discord.Color.blurple()
        )

        description_parts = []

        for name, items in sections.items():
            if not items:
                continue
            description_parts.append(f"**{name}**")
            description_parts.extend(items)
            description_parts.append("")

        embed.description = "\n".join(description_parts)

        embed.set_footer(text="Powered by weao.xyz")

        await interaction.followup.send(embed=embed)




    except Exception as e:
        await interaction.followup.send(
            f"❌ Terjadi error\n```{type(e).__name__}: {e}```"
        )

# =========================
# /gemstone (THREAD MODE)
# =========================
@tree.command(name="gemstone", description="Scan Gemstone & alert semua orang")
@app_commands.checks.cooldown(1, 60)
async def gemstone(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    keyword = "gemstone"
    channel = interaction.channel
    found_messages = []

    async for message in channel.history(limit=200):
        await asyncio.sleep(0.05)

        if keyword in message.content.lower():
            found_messages.append(message)
            continue

        for embed in message.embeds:
            if embed_contains(embed, keyword):
                found_messages.append(message)
                break

    # ❌ TIDAK DITEMUKAN
    if not found_messages:
        msg = await interaction.followup.send(
            "❌ Tidak ditemukan **Ruby Gemstone**"
        )
        await msg.delete(delay=10)
        return

    # =========================
    # EMBED RINGKAS (CHANNEL)
    # =========================
    embed = discord.Embed(
        title="💎 Gemstone Alert",
        description=(
            f"Ditemukan **{len(found_messages)}** **Ruby Gemstone**.\n\n"
            "📌 Detail lengkap ada di **thread**."
        ),
        color=discord.Color.gold()
    )
    embed.set_footer(text="Powered by KappaBot")

    alert_msg = await interaction.followup.send(
        embed=embed
    )

    asyncio.create_task(auto_delete_message(alert_msg, 60))

    # =========================
    # BUAT THREAD
    # =========================
    thread = await channel.create_thread(
        name=f"💎 Gemstone Details ({len(found_messages)})",
        message=alert_msg,
        type=discord.ChannelType.public_thread
    )

    # =========================
    # ISI THREAD (SEMUA LINK)
    # =========================
    for i, msg in enumerate(found_messages, start=1):
        await thread.send(
            f"🔗 **Pesan {i}** oleh **{msg.author.display_name}**\n{msg.jump_url}"
        )
    
    await thread.send("🗑️ Thread ini akan otomatis dihapus dalam **1 menit**")

    client.loop.create_task(delete_thread_later(thread, 60))

@gemstone.error
async def gemstone_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.errors.CommandOnCooldown):
        await interaction.response.send_message(
            f"⏳ Command ini sedang cooldown.\n"
            f"Coba lagi dalam **{error.retry_after:.0f} detik**.",
            ephemeral=True
        )
        return

    if isinstance(error, app_commands.CommandInvokeError):
        if isinstance(error.original, Forbidden):
            await interaction.response.send_message(
                "❌ Bot tidak memiliki izin untuk membaca pesan di channel ini.\n"
                "Pastikan bot memiliki **Read Message History**.",
                ephemeral=True
            )
            return

    raise error
    
# =========================
# RUN BOT
# =========================
client.run(BOT_TOKEN)
