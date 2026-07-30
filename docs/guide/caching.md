# Caching In Depth

PokeLance caches at two independent levels:

1. **Endpoint registries**: the list of every valid name/id for a category (used for
   validation and suggestions, see [Fetching Data](fetching_data.md#validation-and-did-you-mean)).
2. **Model caches**: the actual fetched resources, kept as bounded LRU maps keyed by
   [`Route`][pokelance.http.endpoints.Route].

Both live under `client.http.cache`, mirrored per-extension as `client.<ext>.cache`.

## How endpoint registries are populated

Each category has its own one-time "list everything" request behind it, using PokéAPI's
pagination `limit` param cranked up to `10000` so the whole category comes back in a single
page instead of paginating. For `pokemon`, that's a GET to
[`https://pokeapi.co/api/v2/pokemon?limit=10000`](https://pokeapi.co/api/v2/pokemon?limit=10000),
which shapes up like:

```json
{
    "count": 1351,
    "next": null,
    "previous": null,
    "results": [
        {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
        {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"},
        {"name": "venusaur", "url": "https://pokeapi.co/api/v2/pokemon/3/"},
        {"name": "charmander", "url": "https://pokeapi.co/api/v2/pokemon/4/"},
        {"name": "charmeleon", "url": "https://pokeapi.co/api/v2/pokemon/5/"}
    ]
}
```

[`BaseExtension.setup()`][pokelance.ext._base.BaseExtension.setup] is what kicks this off. For
every `fetch_*` method it finds on the extension, it looks for a matching
`Endpoint.get_*_endpoints()` route builder (here, `Endpoint.get_pokemon_endpoints()`), sends
that request, and passes the `results` list straight to
[`Cache.load_documents()`][pokelance.cache.cache_manager.Cache.load_documents]. That routes
to the right sub-cache (`client.pokemon.cache.pokemon`) and calls its own
[`load_documents()`][pokelance.cache.cache.BaseCache.load_documents], which is what actually
builds the `_endpoints` dict, one entry per result:

```python
def load_documents(self, data: t.List[t.Dict[str, str]]) -> None:
    for document in data:
        self._endpoints[document["name"]] = Endpoint(
            url=document["url"],
            id=int(document["url"].split("/")[-2]),
        )
    self._endpoints_cached = True
```

For the sample response above, `client.pokemon.cache.pokemon.endpoints` ends up as:

```python
{
    "bulbasaur": Endpoint(id=1, url="https://pokeapi.co/api/v2/pokemon/1/"),
    "ivysaur": Endpoint(id=2, url="https://pokeapi.co/api/v2/pokemon/2/"),
    "venusaur": Endpoint(id=3, url="https://pokeapi.co/api/v2/pokemon/3/"),
    "charmander": Endpoint(id=4, url="https://pokeapi.co/api/v2/pokemon/4/"),
    "charmeleon": Endpoint(id=5, url="https://pokeapi.co/api/v2/pokemon/5/"),
}
```

i.e. each result becomes a name -> [`CacheEndpoint(id, url)`][pokelance.cache.cache.CacheEndpoint]
entry. No model is fetched or built at this stage; this is purely the name/id index, not
the actual `Pokemon` resources themselves.

That dict is what powers two other things covered below:

- Fuzzy `did-you-mean` suggestions on `ResourceNotFound` (matched against both name and id).
- The alias lookup in `BaseCache.get`, so `get_pokemon(1)` and `get_pokemon("bulbasaur")`
  resolve to the same cached entry even though only one of those two forms was ever fetched.

## The cache hierarchy

``` mermaid
flowchart TD
    A[client.http.cache: Cache] --> B[Cache.berry: Berry]
    A --> C[Cache.pokemon: Pokemon]
    A --> D["... 9 more extensions"]
    B --> E[BerryCache]
    B --> F[BerryFirmnessCache]
    B --> G[BerryFlavorCache]
    E -.->|MutableMapping Route to Berry, max_size LRU| E
```

- [`Cache`][pokelance.cache.cache_manager.Cache] is the top-level container, one per client.
- Each extension gets a matching container (e.g. [`cache.Berry`][pokelance.cache.cache_manager.Berry]) that
  groups its categories' individual caches.
- Each individual cache (e.g. [`BerryCache`][pokelance.cache.cache.BerryCache]) is a
  [`BaseCache`][pokelance.cache.cache.BaseCache]: a `MutableMapping[Route, Model]` with LRU
  eviction once `max_size` is exceeded.

## LRU eviction

[`BaseCache`][pokelance.cache.cache.BaseCache] implements `MutableMapping` directly, so it behaves
like a `dict` with two extra properties: accessing a key moves it to the "most recently
used" end, and inserting past `max_size` evicts the oldest entry:

```python
client.berry.cache.berry.set_size(2)          # keep at most 2 berries in memory
await client.berry.fetch_berry("cheri")        # cache: [cheri]
await client.berry.fetch_berry("chesto")       # cache: [cheri, chesto]
await client.berry.fetch_berry("pecha")        # cache: [chesto, pecha] - cheri evicted
```

!!! note "LRU eviction is per-category"
    Each category has its own independent LRU cache, so `cache_size=100` means "keep up to
    100 berries, 100 pokemon, 100 moves, etc." not "keep 100 total resources across all
    categories".

If you want to read a bit more about LRU caches and how they work, check out the Python docs for [`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache) and this article: [How to Implement an LRU Cache in Python](https://realpython.com/lru-cache-python/).

## Fuzzy cache lookups

[`BaseCache.get`][pokelance.cache.cache.BaseCache.get] doesn't only do exact key lookups: if the exact
`Route` isn't cached, it also checks whether the requested name/id maps to an *alias* in the
endpoint registry (e.g. numeric id vs. name) and returns the cached entry under that alias
if found. This is how `get_pokemon(1)` and `get_pokemon("bulbasaur")` can return the same
cached instance even though only one of those two forms was ever actually fetched.

## Waiting for endpoint registries

With `cache_endpoints=True` (the default), registries load in the background right after the
client connects. Await [`wait_until_ready()`][pokelance.client.PokeLance.wait_until_ready] on the
client (or [`BaseCache.wait_until_ready()`][pokelance.cache.cache.BaseCache.wait_until_ready] on an individual
cache) to block until they've finished:

```python exec="true" source="above" result="text"
import asyncio
from pokelance import PokeLance

client = PokeLance()


async def main() -> str:
    await client.wait_until_ready()
    n = len(client.berry.cache.berry.endpoints)
    await client.close()
    return f"{n} berries registered"


print(asyncio.run(main()))
```

## Bulk-loading an entire category

Once a category's endpoint registry is loaded, you can eagerly fetch **every** resource in
it, not just the ones you've explicitly requested, with
[`load_all()`][pokelance.cache.cache.BaseCache.load_all] (sequential) or
[`load_all_batch()`][pokelance.cache.cache.BaseCache.load_all_batch] (concurrent, in configurable batches):

```python
await client.berry.cache.berry_flavor.wait_until_ready()
await client.berry.cache.berry_flavor.load_all()          # one request at a time
# or, faster, with controlled concurrency:
await client.berry.cache.berry_flavor.load_all_batch(batch_size=20)
```

`load_all_batch` fetches `batch_size` resources concurrently via `asyncio.gather`, then
moves to the next batch, a good default for not overwhelming PokéAPI with hundreds of
simultaneous connections while still being much faster than fetching one at a time.

!!! danger "Both raise `RuntimeError` if the registry isn't loaded"
    `load_all()` / `load_all_batch()` require `_endpoints_cached` to already be `True`.
    Always `await ...wait_until_ready()` on the same cache first (or construct the client
    with `cache_endpoints=True` and await `client.wait_until_ready()`).

## Persisting a cache to disk

Every [`BaseCache`][pokelance.cache.cache.BaseCache] can serialize itself to a JSON file and load
back from it later, useful for warm-starting a process without hitting the network on
every boot:

```python
import asyncio
import pokelance


async def main() -> None:
    client = pokelance.PokeLance()
    client.logger.info(await client.ping())
    client.logger.info(f"Size: {len(client.berry.cache.berry_flavor)}")
    try:
        client.logger.info("Loading berry flavors from cache file...")
        await client.berry.cache.berry_flavor.load()
    except FileNotFoundError:
        client.logger.info("No cache file yet - loading berry flavors from the API...")
        await client.berry.cache.berry_flavor.wait_until_ready()
        await client.berry.cache.berry_flavor.load_all()
        await client.berry.cache.berry_flavor.save()
    client.logger.info(f"Loaded {len(client.berry.cache.berry_flavor)} berry flavors.")
    await client.close()


asyncio.run(main())
```

- [`save(path=".")`][pokelance.cache.cache.BaseCache.save] writes `<path>/<CacheClassName>.json`,
  mapping each cached route's endpoint to its raw (or serialized) payload.
- [`load(path=".")`][pokelance.cache.cache.BaseCache.load] reads that same file back, reconstructing
  models via `Model.from_payload(...)` and re-populating the cache, no network calls.

!!! note "Where the file lives"
    The filename is derived from the cache's class name (e.g. `BerryFlavorCache.json`), and
    the directory is whatever `path` you pass, the current working directory by
    default. Pick a stable path (e.g. an app-specific data directory) in production code.

## Clearing caches

Clear everything at once:

```python
client.http.cache.clear()          # every extension, every category
client.berry.cache.clear()         # just the berry extension
client.berry.cache.berry.clear()   # just one category
```

!!! info "Caches are shared across client instances"
    Because the underlying `attrs`-defined cache containers use mutable defaults shared at
    the class level, creating multiple `PokeLance()` instances in the same process shares
    their model caches. This is usually what you want (one warm cache, however many clients
    you construct) but is worth knowing if you're concerned about multi-threading behavior or
    expect strict isolation between instances.
