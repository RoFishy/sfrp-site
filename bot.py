import discord
from discord.ext import commands
from aiohttp import web
import os
from dotenv import dotenv_values
import asyncio

config = dotenv_values(".env")

TOKEN = str(config["TOKEN"])

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_app = web.Application()
        self.api_runner = None

        # Add API routes
        self.api_app.router.add_get("/staff_check", self.staff_check)

    async def setup_hook(self):
        """Setup the aiohttp server."""
        self.api_runner = web.AppRunner(self.api_app)
        await self.api_runner.setup()
        site = web.TCPSite(self.api_runner, host="127.0.0.1", port=8080)
        await site.start()
        print("API server running on http://127.0.0.1:8080")

    async def close(self):
        """Cleanup the aiohttp server."""
        if self.api_runner:
            await self.api_runner.cleanup()
        await super().close()

    async def staff_check(self, request):
        """Check if a user has the 'Staff Board' role."""
        user_id = request.query.get("id")
        if not user_id:
            return web.json_response({"error": "Missing 'id' parameter"}, status=400)

        try:
            guild = discord.utils.get(self.guilds, id=1117521010175004694)
            if not guild:
                return web.json_response({"error": "Guild not found"}, status=404)

            user = guild.get_member(int(user_id))
            if not user:
                return web.json_response({"error": "User not found in the guild"}, status=404)

            role = discord.utils.get(guild.roles, name="Staff Board")
            if not role:
                return web.json_response({"error": "Role not found"}, status=404)

            # Check if the user has the role
            has_role = role in user.roles
            return web.json_response({"value": "True" if has_role else "False"})

        except Exception as e:
            print(f"Error in staff_check: {e}")
            return web.json_response({"error": str(e)}, status=500)

    #async def get_guild(self, request):
     #   params = request.query.get("id")
      #  guild = discord.utils.get(self.guilds, id=int(params))

       # return web.json_response({"name" : guild.name})

    async def on_ready(self):
        print(f"Bot is ready. Logged in as {self.user}")

# Instantiate and run the bot
bot = MyBot(command_prefix="!", intents=discord.Intents.all())

#async def load():
 #   for filename in os.listdir("cogs"):
  #      if filename.endswith(".py"):
   #         await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())