# Error Handling

PokeLance raises a clear, predictable exception hierarchy so you can catch broadly (any library error) or narrowly (a specific HTTP status) depending on what your application needs.

## The hierarchy

``` mermaid
flowchart TD
    A[PokeLanceException] --> B[HTTPException]
    B --> C["BadRequest (400)"]
    B --> D["Unauthorized (401)"]
    B --> E["Forbidden (403)"]
    B --> F["NotFound (404)"]
    F --> G[ResourceNotFound]
    B --> H["MethodNotAllowed (405)"]
    B --> I["UnknownError (other statuses)"]
    F --> J[ImageNotFound]
    F --> K[AudioNotFound]
```

Every exception carries the [`Route`][pokelance.endpoints.Route] that caused it:

```python exec="true" source="above" result="text"
import asyncio
from pokelance import PokeLanceAsyncClient
from pokelance.exceptions import ResourceNotFound


async def main() -> None:
    async with PokeLanceAsyncClient() as client:
        await client.wait_until_ready()
        try:
            await client.pokemon.fetch_pokemon("not-a-real-pokemon")
        except ResourceNotFound as exc:
            print(f"Failed route: {exc.route}")
            print(f"Suggestions: {exc.suggestions}")


asyncio.run(main())
```

## `ResourceNotFound`: typo suggestions

[`ResourceNotFound`][pokelance.exceptions.ResourceNotFound] is raised when a requested resource name or ID is not recognized. It carries a `suggestions: list[str] | None` attribute computed with `difflib.get_close_matches`:

```python exec="true" source="above" result="text"
import asyncio
from pokelance import PokeLanceAsyncClient
from pokelance.exceptions import ResourceNotFound


async def main() -> None:
    async with PokeLanceAsyncClient() as client:
        await client.wait_until_ready()
        try:
            await client.berry.fetch_berry("chery")  # typo for "cheri"
        except ResourceNotFound as exc:
            print(f"Failed to fetch {exc.route}: {', '.join(exc.suggestions or [])}")


asyncio.run(main())
```

!!! note "Requires endpoint registry to be populated"
    Suggestions work when the category's endpoint registry has been loaded (`cache_endpoints=True`, the default).

## HTTP status mapping

Non-2xx HTTP responses are mapped to their corresponding exception subclasses:

| Status | Exception                                              |
| ------ | ------------------------------------------------------ |
| 400    | [`BadRequest`][pokelance.exceptions.BadRequest]         |
| 401    | [`Unauthorized`][pokelance.exceptions.Unauthorized]     |
| 403    | [`Forbidden`][pokelance.exceptions.Forbidden]           |
| 404    | [`ResourceNotFound`][pokelance.exceptions.ResourceNotFound] |
| 405    | [`MethodNotAllowed`][pokelance.exceptions.MethodNotAllowed] |
| other  | [`UnknownError`][pokelance.exceptions.UnknownError]     |

## Media-specific exceptions

[`get_image`][pokelance.client.async_client.PokeLanceAsyncClient.get_image] and
[`get_audio`][pokelance.client.async_client.PokeLanceAsyncClient.get_audio] validate the response's `Content-Type` in addition to its status code, raising [`ImageNotFound`][pokelance.exceptions.ImageNotFound] and [`AudioNotFound`][pokelance.exceptions.AudioNotFound] respectively.

## Recommended patterns

=== "Catch broadly"

    ```python
    from pokelance.exceptions import PokeLanceException

    try:
        pokemon = await client.pokemon.fetch_pokemon(user_input)
    except PokeLanceException as exc:
        print(f"PokeLance error: {exc}")
    ```

=== "Catch a specific status"

    ```python
    from pokelance.exceptions import ResourceNotFound

    try:
        pokemon = await client.pokemon.fetch_pokemon(user_input)
    except ResourceNotFound as exc:
        suggestions = ", ".join(exc.suggestions or [])
        print(f"Couldn't find '{user_input}'. Did you mean: {suggestions}?")
    ```
