# Recipe: Discord Bot

A common pattern is integrating PokeLance with a Discord bot framework (like `discord.py`) using `PokeLanceAsyncClient`.

## Full example

```python
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pokelance import PokeLanceAsyncClient


class Bot(commands.Bot):
    def __init__(self, *, pokemon_db: PokeLanceAsyncClient) -> None:
        super().__init__(command_prefix="!", intents=discord.Intents.all(), case_insensitive=True)
        self.pokemon_db = pokemon_db

    async def setup_hook(self) -> None:
        # Pre-warm registries before accepting interactions
        await self.pokemon_db.wait_until_ready()
        await self.tree.sync()

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user} ({self.user.id})")


async def main() -> None:
    load_dotenv()
    async with PokeLanceAsyncClient() as pokemon_db:
        async with Bot(pokemon_db=pokemon_db) as bot:
            await bot.start(os.getenv("TOKEN", ""))


asyncio.run(main())
```

`PokeLanceAsyncClient` is entered as an async context manager around the bot's own lifetime, so all network connections, registries, and background tasks tear down cleanly together on shutdown (`Ctrl+C`, a crash, or a graceful `bot.close()`).

## A `/pokedex` slash command

Putting [Fetching Data](../fetching_data.md) and [Error Handling](../error_handling.md) together into a slash command:

```python
import discord
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

Because `bot.pokemon_db.pokemon.fetch_pokemon` checks the LRU cache first, running `/pokedex pikachu` twice only hits the network once; subsequent lookups (from this or any other command sharing the client) are served instantly from memory.

## Autocomplete using endpoint registries

Once endpoint registries are pre-warmed (`await bot.pokemon_db.wait_until_ready()` in `setup_hook()`), you get instant, network-free autocomplete data:

```python
@pokedex.autocomplete("name")
async def pokedex_autocomplete(interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
    names = bot.pokemon_db.pokemon.cache_group.pokemon.identifiers
    matches = [n for n in names if current.lower() in n][:25]
    return [app_commands.Choice(name=n, value=n) for n in matches]
```

!!! tip "Warm the cache before the bot starts accepting commands"
    Call `await pokemon_db.wait_until_ready()` inside `setup_hook()` before `tree.sync()`, so `cache_group.pokemon.identifiers` and all other registries are fully populated by the time users can invoke slash commands.
