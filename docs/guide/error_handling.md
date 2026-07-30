# Error Handling

PokeLance raises a small, predictable exception hierarchy so you can catch broadly (any
library error) or narrowly (a specific HTTP status) depending on what your application
needs.

## The hierarchy

``` mermaid
flowchart TD
    A[PokeLanceException] --> B[HTTPException]
    B --> C[BadRequest - 400]
    B --> D[Unauthorized - 401]
    B --> E[Forbidden - 403]
    B --> F[NotFound - 404]
    F --> G[ResourceNotFound]
    B --> H[MethodNotAllowed - 405]
    B --> I[UnknownError - any other status]
    F --> J[ImageNotFound]
    F --> K[AudioNotFound]
```

Every exception carries the [`Route`][pokelance.http.endpoints.Route] that caused it, so
`str(exc)` always tells you exactly which endpoint failed:

```python exec="true" source="above" result="text"
import asyncio
from pokelance import PokeLance
from pokelance.exceptions import ResourceNotFound

client = PokeLance()


async def main() -> str:
    await client.wait_until_ready()
    try:
        await client.pokemon.fetch_pokemon("not-a-real-pokemon")
    except ResourceNotFound as exc:
        return str(exc)
    finally:
        await client.close()
    return "unreachable"


print(asyncio.run(main()))
```

## `ResourceNotFound`: typo suggestions

[`ResourceNotFound`][pokelance.exceptions.ResourceNotFound] is raised by
`_validate_resource` (used internally by every `get_*`/`fetch_*` method) *before* any
network request is made, as soon as a name/id isn't found in the pre-loaded endpoint
registry. It carries a `suggestions: Optional[List[str]]` attribute, computed with
`difflib.get_close_matches` against every known name and id in that category:

```python exec="true" source="above" result="text"
import asyncio
from pokelance import PokeLance
from pokelance.exceptions import ResourceNotFound

client = PokeLance()


async def main() -> str:
    await client.wait_until_ready()
    try:
        await client.berry.fetch_berry("chery")  # typo for "cheri"
    except ResourceNotFound as exc:
        print(f"Failed to fetch {exc.route}: {', '.join(exc.suggestions or [])}")
    finally:
        await client.close()


asyncio.run(main())
```

!!! note "Requires the endpoint registry to be populated"
    Suggestions (and the pre-flight validation itself) only work when the relevant
    category's endpoint registry has been loaded, i.e. `cache_endpoints=True`
    (the default) and, ideally, after `await client.wait_until_ready()`. See
    [Configuration](configuration.md#disabling-endpoint-pre-loading).

## HTTP status mapping

Anything that *does* reach the network and comes back with a non-2xx status is converted
by [`HTTPException.create()`][pokelance.exceptions.HTTPException] into the matching
subclass, via [`get_exception`][pokelance.exceptions.get_exception]:

```python exec="true" source="above" result="text"
from pokelance.exceptions import CODES, UnknownError

for status, cls in sorted(CODES.items()):
    print(f"{status} -> {cls.__name__}")
print(f"(anything else) -> {UnknownError.__name__}")
```

| Status | Exception                                              |
| ------- | --------------------------------------------------------- |
| 400     | [`BadRequest`][pokelance.exceptions.BadRequest]             |
| 401     | [`Unauthorized`][pokelance.exceptions.Unauthorized]         |
| 403     | [`Forbidden`][pokelance.exceptions.Forbidden]               |
| 404     | [`ResourceNotFound`][pokelance.exceptions.ResourceNotFound] |
| 405     | [`MethodNotAllowed`][pokelance.exceptions.MethodNotAllowed] |
| other   | [`UnknownError`][pokelance.exceptions.UnknownError]         |

## Media-specific exceptions

[`get_image_async`][pokelance.client.PokeLance.get_image_async] and
[`get_audio_async`][pokelance.client.PokeLance.get_audio_async] validate the response's
`Content-Type` in addition to its status code, and raise
[`ImageNotFound`][pokelance.exceptions.ImageNotFound] /
[`AudioNotFound`][pokelance.exceptions.AudioNotFound] respectively if either the request
failed *or* the URL didn't actually point at image/audio content. See
[Media](media.md#error-handling) for the accepted content types.

## Recommended patterns

=== "Catch broadly"

    ```python
    from pokelance.exceptions import PokeLanceException

    try:
        pokemon = await client.pokemon.fetch_pokemon(user_input)
    except PokeLanceException as exc:
        await ctx.send(f"Something went wrong: {exc}")
    ```

=== "Catch a specific status"

    ```python
    from pokelance.exceptions import ResourceNotFound

    try:
        pokemon = await client.pokemon.fetch_pokemon(user_input)
    except ResourceNotFound as exc:
        suggestions = ", ".join(exc.suggestions or [])
        await ctx.send(f"Couldn't find '{user_input}'. Did you mean: {suggestions}?")
    ```

=== "Let it propagate"

    In a FastAPI handler, for instance, you may want an unhandled `ResourceNotFound` to
    naturally become a 404, see the [FastAPI recipe](recipes/fastapi.md) for a
    complete example with an exception handler registered at the app level.
