# Extensions Reference

PokeLance groups PokéAPI's ~60 resource categories into 11 **extensions**, attached to the client as attributes (`client.berry`, `client.pokemon`, ...).

Extensions are loaded dynamically during client initialization, you never construct them manually.

## How to read the tables

- **Category** is the API resource name (hyphenated, matching PokéAPI's own naming).
- **Methods** are always `get_<category>` / `fetch_<category>` with hyphens turned into underscores.
- **Key** is what you pass in: a `name` (`str`), an `id` (`int`), or both interchangeably.

=== "Berry"

    `client.berry`, [`Berry`][pokelance.ext._async.berry.Berry]

    | Category         | Key        | Returns                                                                 |
    | ---------------- | ---------- | ----------------------------------------------------------------------- |
    | `berry`          | name or id | [`models.Berry`][pokelance.models.abstract.berry.Berry]                 |
    | `berry-firmness` | name or id | [`models.BerryFirmness`][pokelance.models.abstract.berry.BerryFirmness] |
    | `berry-flavor`   | name or id | [`models.BerryFlavor`][pokelance.models.abstract.berry.BerryFlavor]     |

=== "Contest"

    `client.contest`, [`Contest`][pokelance.ext._async.contest.Contest]

    | Category               | Key        | Returns                                                                                               |
    | ---------------------- | ---------- | ----------------------------------------------------------------------------------------------------- |
    | `contest-type`         | name or id | [`models.ContestType`][pokelance.models.abstract.contest.ContestType]                                 |
    | `contest-effect`       | id only    | [`models.ContestEffect`][pokelance.models.abstract.contest.ContestEffect]                             |
    | `super-contest-effect` | id only    | [`models.SuperContestEffect`][pokelance.models.abstract.contest.SuperContestEffect]                   |

=== "Encounter"

    `client.encounter`, [`Encounter`][pokelance.ext._async.encounter.Encounter]

    | Category                    | Key        | Returns                                                                                         |
    | --------------------------- | ---------- | ----------------------------------------------------------------------------------------------- |
    | `encounter-method`          | name or id | [`models.EncounterMethod`][pokelance.models.abstract.encounter.EncounterMethod]                 |
    | `encounter-condition`       | name or id | [`models.EncounterCondition`][pokelance.models.abstract.encounter.EncounterCondition]           |
    | `encounter-condition-value` | name or id | [`models.EncounterConditionValue`][pokelance.models.abstract.encounter.EncounterConditionValue] |

=== "Evolution"

    `client.evolution`, [`Evolution`][pokelance.ext._async.evolution.Evolution]

    | Category            | Key        | Returns                                                                           |
    | ------------------- | ---------- | --------------------------------------------------------------------------------- |
    | `evolution-chain`   | id only    | [`models.EvolutionChain`][pokelance.models.abstract.evolution.EvolutionChain]     |
    | `evolution-trigger` | name or id | [`models.EvolutionTrigger`][pokelance.models.abstract.evolution.EvolutionTrigger] |

=== "Game"

    `client.game`, [`Game`][pokelance.ext._async.game.Game]

    | Category        | Key        | Returns                                                              |
    | --------------- | ---------- | -------------------------------------------------------------------- |
    | `generation`    | name or id | [`models.Generation`][pokelance.models.abstract.game.Generation]     |
    | `pokedex`       | name or id | [`models.Pokedex`][pokelance.models.abstract.game.Pokedex]           |
    | `version`       | name or id | [`models.Version`][pokelance.models.abstract.game.Version]           |
    | `version-group` | name or id | [`models.VersionGroup`][pokelance.models.abstract.game.VersionGroup] |

=== "Item"

    `client.item`, [`Item`][pokelance.ext._async.item.Item]

    | Category            | Key        | Returns                                                                    |
    | ------------------- | ---------- | -------------------------------------------------------------------------- |
    | `currency`          | name or id | [`models.Currency`][pokelance.models.abstract.item.Currency]               |
    | `item`              | name or id | [`models.Item`][pokelance.models.abstract.item.Item]                       |
    | `item-attribute`    | name or id | [`models.ItemAttribute`][pokelance.models.abstract.item.ItemAttribute]     |
    | `item-category`     | name or id | [`models.ItemCategory`][pokelance.models.abstract.item.ItemCategory]       |
    | `item-fling-effect` | name or id | [`models.ItemFlingEffect`][pokelance.models.abstract.item.ItemFlingEffect] |
    | `item-pocket`       | name or id | [`models.ItemPocket`][pokelance.models.abstract.item.ItemPocket]           |

=== "Location"

    `client.location`, [`Location`][pokelance.ext._async.location.Location]

    | Category        | Key        | Returns                                                                  |
    | --------------- | ---------- | ------------------------------------------------------------------------ |
    | `location`      | name or id | [`models.Location`][pokelance.models.abstract.location.Location]         |
    | `location-area` | name or id | [`models.LocationArea`][pokelance.models.abstract.location.LocationArea] |
    | `pal-park-area` | name or id | [`models.PalParkArea`][pokelance.models.abstract.location.PalParkArea]   |
    | `region`        | name or id | [`models.Region`][pokelance.models.abstract.location.Region]             |

=== "Machine"

    `client.machine`, [`Machine`][pokelance.ext._async.machine.Machine]

    | Category  | Key     | Returns                                                       |
    | --------- | ------- | ------------------------------------------------------------- |
    | `machine` | id only | [`models.Machine`][pokelance.models.abstract.machine.Machine] |

=== "Move"

    `client.move`, [`Move`][pokelance.ext._async.move.Move]

    | Category            | Key        | Returns                                                                    |
    | ------------------- | ---------- | -------------------------------------------------------------------------- |
    | `move`              | name or id | [`models.Move`][pokelance.models.abstract.move.Move]                       |
    | `move-ailment`      | name or id | [`models.MoveAilment`][pokelance.models.abstract.move.MoveAilment]         |
    | `move-battle-style` | name or id | [`models.MoveBattleStyle`][pokelance.models.abstract.move.MoveBattleStyle] |
    | `move-category`     | name or id | [`models.MoveCategory`][pokelance.models.abstract.move.MoveCategory]       |
    | `move-damage-class` | name or id | [`models.MoveDamageClass`][pokelance.models.abstract.move.MoveDamageClass] |
    | `move-learn-method` | name or id | [`models.MoveLearnMethod`][pokelance.models.abstract.move.MoveLearnMethod] |
    | `move-target`       | name or id | [`models.MoveTarget`][pokelance.models.abstract.move.MoveTarget]           |

=== "Pokemon"

    `client.pokemon`, [`Pokemon`][pokelance.ext._async.pokemon.Pokemon]

    | Category                  | Key        | Returns                                                                                                                             |
    | ------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------- |
    | `ability`                 | name or id | [`models.Ability`][pokelance.models.abstract.pokemon.Ability]                                                                       |
    | `characteristic`          | id only    | [`models.Characteristic`][pokelance.models.abstract.pokemon.Characteristic]                                                         |
    | `egg-group`               | name or id | [`models.EggGroup`][pokelance.models.abstract.pokemon.EggGroup]                                                                     |
    | `gender`                  | name or id | [`models.Gender`][pokelance.models.abstract.pokemon.Gender]                                                                         |
    | `growth-rate`             | name or id | [`models.GrowthRate`][pokelance.models.abstract.pokemon.GrowthRate]                                                                 |
    | `location-area-encounter` | name or id | `list[`[`models.LocationAreaEncounter`][pokelance.models.abstract.pokemon.LocationAreaEncounter]`]`, a **list**, not a single model |
    | `nature`                  | name or id | [`models.Nature`][pokelance.models.abstract.pokemon.Nature]                                                                         |
    | `pokeathlon-stat`         | name or id | [`models.PokeathlonStat`][pokelance.models.abstract.pokemon.PokeathlonStat]                                                         |
    | `pokemon`                 | name or id | [`models.Pokemon`][pokelance.models.abstract.pokemon.Pokemon]                                                                       |
    | `pokemon-color`           | name or id | [`models.PokemonColor`][pokelance.models.abstract.pokemon.PokemonColor]                                                             |
    | `pokemon-form`            | name or id | [`models.PokemonForm`][pokelance.models.abstract.pokemon.PokemonForm]                                                               |
    | `pokemon-habitat`         | name or id | [`models.PokemonHabitats`][pokelance.models.abstract.pokemon.PokemonHabitats]                                                       |
    | `pokemon-shape`           | name or id | [`models.PokemonShape`][pokelance.models.abstract.pokemon.PokemonShape]                                                             |
    | `pokemon-species`         | name or id | [`models.PokemonSpecies`][pokelance.models.abstract.pokemon.PokemonSpecies]                                                         |
    | `stat`                    | name or id | [`models.Stat`][pokelance.models.abstract.pokemon.Stat]                                                                             |
    | `type`                    | name or id | [`models.Type`][pokelance.models.abstract.pokemon.Type]                                                                             |

=== "Utility"

    `client.utility`, [`Utility`][pokelance.ext._async.utility.Utility]

    | Category       | Key        | Returns                                                                                         |
    | -------------- | ---------- | ----------------------------------------------------------------------------------------------- |
    | `language`     | name or id | [`models.Language`][pokelance.models.common.models.Language]                                    |
    | `api-metadata` | *none*     | [`models.APIMetadata`][pokelance.models.common.models.APIMetadata], singleton, no list endpoint |

## Inspecting valid names and IDs

Once endpoint registries are cached (either on initial client connection or after `await client.wait_until_ready()`), all valid names and IDs for any category across all 11 extensions can be inspected directly:

- **`client.<ext>.cache_group.<category>.identifiers`**: A `set[str]` containing every valid name and ID for the category (e.g. `client.pokemon.cache_group.pokemon.identifiers`).
- **`client.<ext>.cache_group.<category>.endpoints`**: A `dict[str, CacheEndpoint]` mapping each resource identifier to its [`CacheEndpoint`][pokelance.cache._base.CacheEndpoint] metadata (`id`, `url`).

```python exec="true" source="above" result="text"
import asyncio
from pokelance import PokeLanceAsyncClient


async def main() -> None:
    async with PokeLanceAsyncClient() as client:
        await client.wait_until_ready()
        berries = client.berry.cache_group.berry.endpoints
        print(f"Registered {len(berries)} berries (e.g. 'cheri' -> id {berries['cheri'].id})")


asyncio.run(main())
```

## Programmatic access via `ExtensionEnum`

Categories are also available programmatically through [`pokelance.constants.ExtensionEnum`][pokelance.constants.ExtensionEnum]:

```python exec="true" source="above" result="text"
from pokelance.constants import ExtensionEnum

for ext in ExtensionEnum:
    print(f"{ext.name:<10} -> {', '.join(ext.value.categories)}")
```
