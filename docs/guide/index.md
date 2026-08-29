# Guide

Everything you need to build with PokeLance, from your first request to caching the entire gamut of PokéAPI resources on disk.

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Installation__

    ---

    Install PokeLance with `uv` or `pip` with support for both asynchronous and synchronous execution.

    [:octicons-arrow-right-24: Installation](installation.md)

-   :material-lightning-bolt:{ .lg .middle } __Quickstart__

    ---

    Create a client, ping the API, and fetch your first resources in a few lines of code.

    [:octicons-arrow-right-24: Quickstart](quickstart.md)

-   :material-tune:{ .lg .middle } __Configuration__

    ---

    Tune cache sizes, bring your own `niquests` sessions, configure logging, and control endpoint pre-loading.

    [:octicons-arrow-right-24: Configuration](configuration.md)

-   :material-database-search:{ .lg .middle } __Fetching Data__

    ---

    Understand the `get_*` / `fetch_*` pattern, `getch_data`, and constructing requests straight `from_url`.

    [:octicons-arrow-right-24: Fetching Data](fetching_data.md)

-   :material-view-grid-plus:{ .lg .middle } __Extensions Reference__

    ---

    A complete map of all 11 extensions and every category/endpoint they expose.

    [:octicons-arrow-right-24: Extensions Reference](extensions.md)

-   :material-cached:{ .lg .middle } __Caching In Depth__

    ---

    LRU in-memory caches, endpoint auto-completion, and persisting entire resource sets to disk as JSON.

    [:octicons-arrow-right-24: Caching In Depth](caching.md)

-   :material-alert-decagram:{ .lg .middle } __Error Handling__

    ---

    The exception hierarchy, HTTP status mapping, and "did you mean...?" suggestions for typoed resources.

    [:octicons-arrow-right-24: Error Handling](error_handling.md)

-   :material-image-multiple:{ .lg .middle } __Media: Sprites & Cries__

    ---

    Download sprites and cries with a built-in LRU cache (`get_image`, `get_audio`).

    [:octicons-arrow-right-24: Media](media.md)

</div>

## Recipes

Full, runnable integrations built on top of the client.

<div class="grid cards" markdown>

-   :fontawesome-brands-discord:{ .lg .middle } __Discord Bot__

    ---

    Share a `PokeLanceAsyncClient` across your whole bot's lifetime.

    [:octicons-arrow-right-24: Discord Bot](recipes/discord_bot.md)

-   :material-api:{ .lg .middle } __FastAPI Service__

    ---

    Expose PokeLance's cache-then-fetch pattern as a read-through REST API.

    [:octicons-arrow-right-24: FastAPI Service](recipes/fastapi.md)

-   :material-notebook:{ .lg .middle } __Notebook Playground__

    ---

    An interactive Jupyter notebook for exploring the client cell-by-cell.

    [:octicons-arrow-right-24: Notebook Playground](recipes/playground.ipynb)

</div>

!!! tip "Reading alongside the API Reference"
    Every page here links out to the relevant [API Reference](../api_reference/pokelance.md) section.
