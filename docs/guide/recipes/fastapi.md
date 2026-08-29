# Recipe: FastAPI Service

PokeLance's `get_*`/`fetch_*` pattern maps naturally onto a read-through REST API: check the cache, fall back to PokéAPI, and return the model directly.

## Full example with FastAPI Lifespan

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
import uvicorn
from pokelance import PokeLanceAsyncClient, models
from pokelance.exceptions import ResourceNotFound

pokemon_client = PokeLanceAsyncClient()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Start the client and pre-warm registries
    await pokemon_client.wait_until_ready()
    yield
    await pokemon_client.close()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(ResourceNotFound)
async def resource_not_found_handler(request: Request, exc: ResourceNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message, "suggestions": exc.suggestions or []},
    )


@app.get("/ping")
async def ping() -> dict[str, float]:
    return {"latency": await pokemon_client.ping()}


@app.get("/berry/{name}", response_model=models.Berry)
async def get_berry(name: str) -> models.Berry:
    return pokemon_client.berry.get_berry(name) or await pokemon_client.berry.fetch_berry(name)


@app.get("/pokemon/{name}/sprite")
async def get_sprite(name: str) -> Response:
    pokemon = pokemon_client.pokemon.get_pokemon(name) or await pokemon_client.pokemon.fetch_pokemon(name)
    if not pokemon.sprites.front_default:
        raise HTTPException(status_code=404, detail="No sprite available")
    image_bytes = await pokemon_client.get_image(pokemon.sprites.front_default)
    return Response(content=image_bytes, media_type="image/png")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
```

## How it works

### Read-through caching with `or await ...fetch_*`

`pokemon_client.berry.get_berry(name) or await pokemon_client.berry.fetch_berry(name)` implements a lightweight read-through cache:
- `get_*` checks in-memory LRU cache and returns `None` on a cache miss (falsy).
- Python's `or` operator immediately falls through to evaluate `await fetch_*`, fetching the resource from PokéAPI, caching it, and returning the parsed model.
- Subsequent requests for the same berry hit memory without an HTTP round-trip.

### Turning `ResourceNotFound` into a proper 404

Left unhandled, an invalid name or ID raises [`ResourceNotFound`][pokelance.exceptions.ResourceNotFound] and FastAPI would return an opaque `500 Internal Server Error`.

Registering `@app.exception_handler(ResourceNotFound)` intercepts this error and converts it into a structured `404 Not Found` response with fuzzy `did-you-mean` suggestions (e.g. suggesting `["cheri"]` when querying `/berry/chery`).

## Serving sprites through the API

Because [`get_image`][pokelance.client.async_client.PokeLanceAsyncClient.get_image] caches downloaded bytes in memory, proxying sprites through your own service (such as to prevent CORS issues on a frontend) is fast and skips repeated network requests.

See [Media](../media.md) for details on image and audio caching.

!!! tip "One client for the whole app's lifetime"
    Construct `PokeLanceAsyncClient` once during application startup (managed cleanly via FastAPI's `lifespan` context manager as shown above) and reuse it across all request handlers. Creating a new client per-request would discard all caching and connection pooling benefits.
