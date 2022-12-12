# Implementation of a Discord bot and PokeLance

```python
import os
import asyncio

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pokelance import PokeLance


class Bot(commands.Bot):

    def __init__(self, *, web_client: aiohttp.ClientSession, pokemon_db: PokeLance) -> None:
        super().__init__(command_prefix="!", intents=discord.Intents.all(), case_insensitive=True)
        self.web_client = web_client
        self.pokemon_db = pokemon_db

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user} ({self.user.id})")
        return None


async def main() -> None:
    load_dotenv()
    async with aiohttp.ClientSession() as session, PokeLance(session=session) as pokemon_db:
        async with Bot(web_client=session, pokemon_db=pokemon_db) as bot:
            bot.run(os.getenv("TOKEN"))

asyncio.run(main())
```