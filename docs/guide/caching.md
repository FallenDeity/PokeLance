# Caching In Depth

PokeLance caches data at two independent levels:

1. **Endpoint registries**: the list of valid names and IDs for each category (used for validation and fuzzy suggestions, see [Fetching Data](fetching_data.md#validation-and-did-you-mean)).
2. **Model caches**: the actual fetched resources, kept as bounded LRU maps keyed by [`Route`][pokelance.endpoints.Route].

Both live under `client.http.cache_manager`, mirrored per-extension as `client.<ext>.cache_group`.

## How endpoint registries are populated

Each category has a one-time "list everything" request behind it, querying PokéAPI with a `limit=10000` query parameter so the whole category index is fetched in a single request (e.g. `GET https://pokeapi.co/api/v2/pokemon?limit=10000`).

```json
{
    "count": 1351,
    "next": null,
    "previous": null,
    "results": [
        {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
        {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"},
        {"name": "venusaur", "url": "https://pokeapi.co/api/v2/pokemon/3/"}
    ]
}
```

[`BaseExtension.setup()`][pokelance.ext._base.BaseExtension.setup] kicks this off on initialization. For every category, it queries the endpoint and populates the category's cache state with [`CacheEndpoint`][pokelance.cache._base.CacheEndpoint] entries:

```python
{
    "bulbasaur": CacheEndpoint(id=1, url="https://pokeapi.co/api/v2/pokemon/1/"),
    "ivysaur": CacheEndpoint(id=2, url="https://pokeapi.co/api/v2/pokemon/2/"),
    "venusaur": CacheEndpoint(id=3, url="https://pokeapi.co/api/v2/pokemon/3/"),
}
```

This index powers two key features:

- **Fuzzy `did-you-mean` suggestions** on [`ResourceNotFound`][pokelance.exceptions.ResourceNotFound] errors.
- **Alias lookups** in cache lookups, ensuring `get_pokemon(1)` and `get_pokemon("bulbasaur")` resolve to the exact same cached model instance.

## The cache hierarchy

``` mermaid
flowchart TD
    A["client.http.cache_manager: BaseCacheManager"] --> B["cache_manager.berry: BerryCacheGroup"]
    A --> C["cache_manager.pokemon: PokemonCacheGroup"]
    A --> D["... 9 more extensions"]
    B --> E["BerryCache (BaseCacheState)"]
    B --> F["BerryFirmnessCache (BaseCacheState)"]
    B --> G["BerryFlavorCache (BaseCacheState)"]
    E -.->|LRU Cache: Route -> Model| E
```

- [`BaseCacheManager`][pokelance.cache._base.BaseCacheManager] is the top-level container, accessible via `client.http.cache_manager`.
- Each extension has a matching [`BaseCacheGroup`][pokelance.cache._base.BaseCacheGroup] (e.g. `client.berry.cache_group`).
- Each individual resource category is a [`BaseCacheState`][pokelance.cache._base.BaseCacheState] (such as `AsyncCache` / `SyncCache`): an LRU map with eviction once `max_size` is exceeded.

## LRU eviction

[`BaseCacheState`][pokelance.cache._base.BaseCacheState] behaves like a bounded dictionary with LRU semantics: accessing an item moves it to the most recently used position, and inserting beyond `max_size` evicts the oldest entry:

```python
client.berry.cache_group.berry.set_size(2)  # keep at most 2 berries in memory
await client.berry.fetch_berry("cheri")  # cache: [cheri]
await client.berry.fetch_berry("chesto")  # cache: [cheri, chesto]
await client.berry.fetch_berry("pecha")  # cache: [chesto, pecha] - cheri evicted
```

!!! note "LRU eviction is per-category"
    Each category has its own independent LRU cache (`cache_size=100` means up to 100 berries, 100 pokemon, 100 moves, etc., not 100 total across all categories combined).

To learn more about LRU caches and their design, see Python's [`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache) documentation and the RealPython guide [How to Implement an LRU Cache in Python](https://realpython.com/lru-cache-python/).

## Fuzzy cache lookups

`get()` checks whether the requested name or ID maps to an alias in the endpoint registry and returns the cached entry. This allows `client.pokemon.get_pokemon(1)` and `client.pokemon.get_pokemon("bulbasaur")` to resolve seamlessly to the same object even if only one representation was ever fetched from the network.

## Waiting for endpoint registries

With `cache_endpoints=True` (the default), registries load asynchronously in the background when the client connects. You can wait for endpoint registries to complete loading at three different levels of granularity:

- **Global**: `await client.wait_until_ready()` waits for all 11 extensions and all categories to finish their initial setup.
- **Extension-level**: `await client.berry.wait_until_ready()` (or `await client.berry.cache_group.wait_until_ready()`) waits specifically for the berry extension and its associated category registries.
- **Category-level**: `await client.berry.cache_group.berry.wait_until_ready()` waits specifically for a single category's endpoint registry.

## Loading endpoint registries

Similarly, you can trigger endpoint registry loading at three levels:

- **Global**: `client.http.connect()` triggers all extensions to populate their endpoint registries. This runs automatically once per client on first connect/request or when triggered manually via `await client.wait_until_ready()`.
- **Extension-level**: `await client.<ext>.setup()` triggers a specific extension to load its endpoint registries. You can call this manually to refresh a specific extension's registries without restarting the entire client.
- **Category-level**: `client.<ext>.cache_group.<category>.load_documents(data)` populates a category's endpoint registry from a list of raw document payloads.

## Resetting and re-loading an extension

If you need to refresh the endpoint registries for a specific extension without restarting the entire client, you can reset the extension's cache group and re-trigger setup:

```python exec="true" source="above" result="text"
import asyncio
from pokelance import PokeLanceAsyncClient


async def main() -> None:
    async with PokeLanceAsyncClient() as client:
        # 1. Wait for initial global load
        await client.wait_until_ready()

        # 2. Reset and re-load the 'berry' extension specifically
        client.berry.cache_group.reset()
        await client.berry.setup()

        # 3. Wait specifically for the 'berry' extension to be ready again
        await client.berry.cache_group.wait_until_ready()

        # 4. Fetch a berry to confirm the cache is working
        berry = await client.berry.fetch_berry("cheri")
        print(f"Fetched berry: {berry.name} (id={berry.id})")


asyncio.run(main())
```

This pattern allows you to maintain cache isolation and only incur the cost of re-loading data for the extensions you actually need to refresh.

## Bulk-loading an entire category

Once a category's endpoint registry is loaded, you can eagerly fetch **every** resource in that category, not just the ones you've explicitly requested, using `load_all()` (sequential) or `load_all_batch()` (concurrent in configurable batches):

```python
await client.berry.cache_group.berry_flavor.wait_until_ready()
await client.berry.cache_group.berry_flavor.load_all()  # one request at a time
# or, faster, with controlled concurrency:
await client.berry.cache_group.berry_flavor.load_all_batch(batch_size=20)
```

`load_all_batch` fetches `batch_size` resources concurrently via `asyncio.gather`, then moves to the next batch. This is an optimal default for high throughput without overwhelming PokéAPI with hundreds of simultaneous connections.

!!! danger "Requires endpoint registry to be loaded"
    `load_all()` and `load_all_batch()` require the category's endpoint registry to be populated first. Always `await ...wait_until_ready()` before calling either method.

## Persisting a cache to disk

Every cache state can serialize itself to a JSON file and reload from disk later, which is useful for warm-starting a process without hitting the network on every boot:

```python
import asyncio
from pokelance import PokeLanceAsyncClient


async def main() -> None:
    async with PokeLanceAsyncClient() as client:
        flavor_cache = client.berry.cache_group.berry_flavor
        try:
            print("Loading berry flavors from disk cache...")
            await flavor_cache.load()
        except FileNotFoundError:
            print("No cache file found; loading from API...")
            await flavor_cache.wait_until_ready()
            await flavor_cache.load_all()
            await flavor_cache.save()
        print(f"Loaded {len(flavor_cache)} berry flavors.")


asyncio.run(main())
```

- `save(path=".")` writes `<path>/<category_name>.json` (e.g. `./berry_flavor.json`), serializing all cached routes and payloads.
- `load(path=".")` reads the JSON file back, reconstructing model instances and populating the cache without any network requests.

!!! note "Where the file lives"
    The filename is derived from the category name (e.g. `berry_flavor.json`), and the directory is whatever `path` you provide (`"."` by default). In production code, specify a dedicated directory (such as `cache_dir="./data/cache"`).

## Clearing caches

Clear cached models dynamically at any level:

```python
client.http.cache_manager.clear()  # clear all categories across all extensions
client.berry.cache_group.clear()  # clear all berry categories
client.berry.cache_group.berry.clear()  # clear only the berry category
```

## Cache statistics & metrics

Each cache state and cache group tracks metrics for cache lookups:

```python
# Check stats on a specific category:
berry_stats = client.berry.cache_group.berry.stats
print(f"Hits: {berry_stats.hits}, Misses: {berry_stats.misses}, Hit Ratio: {berry_stats.hit_ratio:.1%}")

# Check aggregated stats across an entire extension group:
group_stats = client.berry.cache_group.stats
print(f"Berry group hit ratio: {group_stats.hit_ratio:.1%}")
```
