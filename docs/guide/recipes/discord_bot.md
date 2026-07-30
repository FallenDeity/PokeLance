# Recipe: Discord Bot

A common pattern: your bot already owns an `aiohttp.ClientSession` (or you want one shared
connector pool for everything), so PokeLance should reuse it rather than opening its own.

## Full example

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


async def main() -> None:
    load_dotenv()
    async with aiohttp.ClientSession() as session, PokeLance(session=session) as pokemon_db:
        async with Bot(web_client=session, pokemon_db=pokemon_db) as bot:
            await bot.start(os.getenv("TOKEN"))


asyncio.run(main())
```

Both `aiohttp.ClientSession` and `PokeLance` are entered as async context managers around
the bot's own lifetime, so everything tears down cleanly together on shutdown (`Ctrl+C`,
a crash, or a graceful `bot.close()`).

## A `/pokedex` slash command

Putting [Fetching Data](../fetching_data.md) and [Error Handling](../error_handling.md)
together into an actual command:

```python
from discord import app_commands, Interaction
from pokelance.exceptions import ResourceNotFound


@bot.tree.command(name="pokedex", description="Look up a Pokémon by name or id")
@app_commands.describe(name="Pokémon name or Pokédex number")
async def pokedex(interaction: Interaction, name: str) -> None:
    await interaction.response.defer()
    try:
        pokemon = await bot.pokemon_db.pokemon.fetch_pokemon(name.lower())
    except ResourceNotFound as exc:
        suggestions = ", ".join(exc.suggestions or []) or "no close matches"
        await interaction.followup.send(f"Couldn't find `{name}`. Did you mean: {suggestions}?")
        return

    sprite = pokemon.sprites.front_default
    embed = (
        discord.Embed(title=pokemon.name.title(), description=f"#{pokemon.id:04d}")
        .add_field(name="Types", value=", ".join(t.type.name for t in pokemon.types))
        .add_field(name="Height", value=f"{pokemon.height / 10} m")
        .add_field(name="Weight", value=f"{pokemon.weight / 10} kg")
        .set_thumbnail(url=sprite)
    )
    await interaction.followup.send(embed=embed)
```

Because `client.pokemon.fetch_pokemon` checks the cache first, running `/pokedex pikachu`
twice only hits the network once subsequent lookups (from this or any other command
sharing the same client) are served from memory.

## Autocomplete using `all_pokemons`

Once the endpoint registry is loaded (`await bot.pokemon_db.wait_until_ready()` during
startup), you get free autocomplete data:

```python
@pokedex.autocomplete("name")
async def pokedex_autocomplete(interaction: Interaction, current: str):
    names = bot.pokemon_db.pokemon.all_pokemons or []
    matches = [n for n in names if current.lower() in n][:25]
    return [app_commands.Choice(name=n, value=n) for n in matches]
```

!!! tip "Warm the cache before the bot starts accepting commands"
    Call `await pokemon_db.wait_until_ready()` right after entering the `PokeLance` context
    manager and before `bot.start(...)`, so `all_pokemons` and friends are populated by the
    time users can invoke commands.
