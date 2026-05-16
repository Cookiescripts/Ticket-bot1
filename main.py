import discord
from discord.ext import commands
import os
import asyncio
import logging
from aiohttp import web

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.setup_sessions = {}


async def health_server():
    async def handle(request):
        return web.Response(text="OK")

    app = web.Application()
    app.router.add_get("/api/healthz", handle)
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Health server running on port {port}")


@bot.event
async def on_ready():
    from database import init_db
    await init_db()

    from cogs.tickets import TicketActionView
    bot.add_view(TicketActionView())

    await bot.load_extension("cogs.setup")
    await bot.load_extension("cogs.tickets")
    await bot.load_extension("cogs.panel_edit")
    await bot.load_extension("cogs.invite")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


async def main():
    await health_server()
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("DISCORD_BOT_TOKEN environment variable not set")
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
