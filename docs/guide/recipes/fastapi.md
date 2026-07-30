# Recipe: FastAPI Service

PokeLance's `get_*`/`fetch_*` pattern maps naturally onto a read-through REST API: check the
cache, fall back to PokéAPI, return the model straight as a `response_model`.

## Full example

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

    def run(self) -> None:
        uvicorn.run(self, debug=True)


async def main() -> None:
    async with aiohttp.ClientSession() as session, PokeLance(session=session) as pokemon_db:
        async with App(web_client=session, pokemon_db=pokemon_db) as app:
            app.run()


asyncio.run(main())
```

`or await ...fetch_*` is the whole trick: `get_*` returns `None` on a cache miss (falsy),
so Python's `or` falls through to the network call automatically without an `if`.

## Turning `ResourceNotFound` into a proper 404

Left as-is, an invalid berry name raises
[`ResourceNotFound`][pokelance.exceptions.ResourceNotFound] and FastAPI will turn that into
an opaque `500`. Register an exception handler instead so clients get a real `404` with the
library's own suggestions attached:

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from pokelance.exceptions import ResourceNotFound


@app.exception_handler(ResourceNotFound)
async def resource_not_found_handler(request: Request, exc: ResourceNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message, "suggestions": exc.suggestions or []},
    )
```

## Serving sprites through the API

Because [`get_image_async`][pokelance.client.PokeLance.get_image_async] already caches downloaded
bytes, you can proxy sprites through your own service (e.g. to avoid CORS issues on a
frontend) essentially for free after the first request:

```python
from fastapi import Response


async def pokemon_sprite(self, name: str) -> Response:
    pokemon = self.pokemon_db.pokemon.get_pokemon(name) or await self.pokemon_db.pokemon.fetch_pokemon(name)
    image_bytes = await self.pokemon_db.get_image_async(pokemon.sprites.front_default)
    return Response(content=image_bytes, media_type="image/png")
```

See [Media](../media.md) for the full set of image/audio helpers and their caching
behaviour.

!!! tip "One client for the whole app's lifetime"
    Construct `PokeLance` once, in your app's startup (as shown via the `async with` in
    `main()` above, or via FastAPI's `lifespan` context manager), and reuse it across every
    request handler. Creating a new client per-request throws away all caching benefits.
