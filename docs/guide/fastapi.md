# Implementing PokeLance with FastAPI

```python
import asyncio

import uvicorn
import aiohttp
from fastapi import FastAPI
from pokelance import PokeLance
from pokelance import models


class App(FastAPI):

    def __init__(self, *, web_client: aiohttp.ClientSession, pokemon_db: PokeLance) -> None:
        super().__init__()
        self.web_client = web_client
        self.pokemon_db = pokemon_db
        self.setup()

    async def ping(self) -> dict[str, float]:
        return {"ping": await self.pokemon_db.ping()}

    async def berry(self, name: str) -> models.Berry:
        return self.pokemon_db.berry.get_berry(name) or await self.pokemon_db.berry.fetch_berry(name)

    async def berry_flavor(self, name: str) -> models.BerryFlavor:
        return self.pokemon_db.berry.get_berry_flavor(name) or await self.pokemon_db.berry.fetch_berry_flavor(name)

    async def berry_firmness(self, name: str) -> models.BerryFirmness:
        return self.pokemon_db.berry.get_berry_firmness(name) or await self.pokemon_db.berry.fetch_berry_firmness(name)

    def setup(self) -> None:
        self.add_route(self.ping, "/ping", methods=["GET"], response_model=dict[str, float])
        self.add_route(self.berry, "/berry/{name}", methods=["GET"], response_model=models.Berry)
        self.add_route(self.berry_flavor, "/berry-flavor/{name}", methods=["GET"], response_model=models.BerryFlavor)
        self.add_route(self.berry_firmness, "/berry-firmness/{name}", methods=["GET"], response_model=models.BerryFirmness)
        return None

    def run(self) -> None:
        uvicorn.run(self, debug=True)


async def main() -> None:
    async with aiohttp.ClientSession() as session, PokeLance(session=session) as pokemon_db:
        async with App(web_client=session, pokemon_db=pokemon_db) as app:
            app.run()

asyncio.run(main())
```
