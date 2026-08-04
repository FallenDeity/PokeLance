# Extensions Reference

PokeLance groups PokéAPI's ~60 resource categories into 11 **extensions**, each attached to
the client as an attribute (`client.berry`, `client.pokemon`, ...). This page is the
complete map: which extension owns which category, what identifier it takes, and any
quirks worth knowing about.

Extensions are loaded automatically in [`setup_hook`][pokelance.client.PokeLance.setup_hook],
you never construct them yourself.

## How to read the tables

- **Category** is the API resource name (hyphenated, matching PokéAPI's own naming).
- **Methods** are always `get_<category>` / `fetch_<category>` with hyphens turned into
  underscores, per [Fetching Data](fetching_data.md).
- **Key** is what you pass in: a `name` (`str`), an `id` (`int`), or both interchangeably.
- **Cache model** notes anything non-obvious about how the result is stored.

=== "Berry"

    `client.berry`, [`Berry`][pokelance.ext.berry.Berry]

    | Category         | Key        | Returns                                                                 |
    | ---------------- | ---------- | ----------------------------------------------------------------------- |
    | `berry`          | name or id | [`models.Berry`][pokelance.models.abstract.berry.Berry]                 |
    | `berry-firmness` | name or id | [`models.BerryFirmness`][pokelance.models.abstract.berry.BerryFirmness] |
    | `berry-flavor`   | name or id | [`models.BerryFlavor`][pokelance.models.abstract.berry.BerryFlavor]     |

=== "Contest"

    `client.contest`, [`Contest`][pokelance.ext.contest.Contest]

    | Category               | Key        | Returns                                                                                               |
    | ---------------------- | ---------- | ----------------------------------------------------------------------------------------------------- |
    | `contest-type`         | name or id | [`models.ContestType`][pokelance.models.abstract.contest.ContestType]                                 |
    | `contest-effect`       | id only    | [`models.ContestEffect`][pokelance.models.abstract.contest.ContestEffect] (secondary cache)           |
    | `super-contest-effect` | id only    | [`models.SuperContestEffect`][pokelance.models.abstract.contest.SuperContestEffect] (secondary cache) |

=== "Encounter"

    `client.encounter`, [`Encounter`][pokelance.ext.encounter.Encounter]

    | Category                    | Key        | Returns                                                                                         |
    | --------------------------- | ---------- | ----------------------------------------------------------------------------------------------- |
    | `encounter-method`          | name or id | [`models.EncounterMethod`][pokelance.models.abstract.encounter.EncounterMethod]                 |
    | `encounter-condition`       | name or id | [`models.EncounterCondition`][pokelance.models.abstract.encounter.EncounterCondition]           |
    | `encounter-condition-value` | name or id | [`models.EncounterConditionValue`][pokelance.models.abstract.encounter.EncounterConditionValue] |

=== "Evolution"

    `client.evolution`, [`Evolution`][pokelance.ext.evolution.Evolution]

    | Category            | Key        | Returns                                                                                         |
    | ------------------- | ---------- | ----------------------------------------------------------------------------------------------- |
    | `evolution-chain`   | id only    | [`models.EvolutionChain`][pokelance.models.abstract.evolution.EvolutionChain] (secondary cache) |
    | `evolution-trigger` | name or id | [`models.EvolutionTrigger`][pokelance.models.abstract.evolution.EvolutionTrigger]               |

=== "Game"

    `client.game`, [`Game`][pokelance.ext.game.Game]

    | Category        | Key        | Returns                                                              |
    | --------------- | ---------- | -------------------------------------------------------------------- |
    | `generation`    | name or id | [`models.Generation`][pokelance.models.abstract.game.Generation]     |
    | `pokedex`       | name or id | [`models.Pokedex`][pokelance.models.abstract.game.Pokedex]           |
    | `version`       | name or id | [`models.Version`][pokelance.models.abstract.game.Version]           |
    | `version-group` | name or id | [`models.VersionGroup`][pokelance.models.abstract.game.VersionGroup] |

=== "Item"

    `client.item`, [`Item`][pokelance.ext.item.Item]

    | Category            | Key        | Returns                                                                    |
    | ------------------- | ---------- | -------------------------------------------------------------------------- |
    | `currency`          | name or id | [`models.Currency`][pokelance.models.abstract.item.Currency]               |
    | `item`              | name or id | [`models.Item`][pokelance.models.abstract.item.Item]                       |
    | `item-attribute`    | name or id | [`models.ItemAttribute`][pokelance.models.abstract.item.ItemAttribute]     |
    | `item-category`     | name or id | [`models.ItemCategory`][pokelance.models.abstract.item.ItemCategory]       |
    | `item-fling-effect` | name or id | [`models.ItemFlingEffect`][pokelance.models.abstract.item.ItemFlingEffect] |
    | `item-pocket`       | name or id | [`models.ItemPocket`][pokelance.models.abstract.item.ItemPocket]           |

=== "Location"

    `client.location`, [`Location`][pokelance.ext.location.Location]

    | Category        | Key        | Returns                                                                  |
    | --------------- | ---------- | ------------------------------------------------------------------------ |
    | `location`      | name or id | [`models.Location`][pokelance.models.abstract.location.Location]         |
    | `location-area` | name or id | [`models.LocationArea`][pokelance.models.abstract.location.LocationArea] |
    | `pal-park-area` | name or id | [`models.PalParkArea`][pokelance.models.abstract.location.PalParkArea]   |
    | `region`        | name or id | [`models.Region`][pokelance.models.abstract.location.Region]             |

=== "Machine"

    `client.machine`, [`Machine`][pokelance.ext.machine.Machine]

    | Category  | Key     | Returns                                                                         |
    | --------- | ------- | ------------------------------------------------------------------------------- |
    | `machine` | id only | [`models.Machine`][pokelance.models.abstract.machine.Machine] (secondary cache) |

=== "Move"

    `client.move`, [`Move`][pokelance.ext.move.Move]

    | Category            | Key        | Returns                                                                    |
    | ------------------- | ---------- | -------------------------------------------------------------------------- |
    | `move`              | name or id | [`models.Move`][pokelance.models.abstract.move.Move]                       |
    | `move-ailment`      | name or id | [`models.MoveAilment`][pokelance.models.abstract.move.MoveAilment]         |
    | `move-battle-style` | name or id | [`models.MoveBattleStyle`][pokelance.models.abstract.move.MoveBattleStyle] |
    | `move-category`     | name or id | [`models.MoveCategory`][pokelance.models.abstract.move.MoveCategory]       |
    | `move-damage-class` | name or id | [`models.MoveDamageClass`][pokelance.models.abstract.move.MoveDamageClass] |
    | `move-learn-method` | name or id | [`models.MoveLearnMethod`][pokelance.models.abstract.move.MoveLearnMethod] |
    | `move-target`       | name or id | [`models.MoveTarget`](../api_reference/models/abstract/move.md)            |

=== "Pokemon"

    `client.pokemon`, [`Pokemon`][pokelance.ext.pokemon.Pokemon]

    | Category                  | Key        | Returns                                                                                                                             |
    | ------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------- |
    | `ability`                 | name or id | [`models.Ability`][pokelance.models.abstract.pokemon.Ability]                                                                       |
    | `characteristic`          | id only    | [`models.Characteristic`][pokelance.models.abstract.pokemon.Characteristic] (secondary cache)                                       |
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

    `client.pokemon.all_pokemons` also gives you every known Pokémon name as a
    `list[str]`, once endpoints are cached, handy for autocompletion.

=== "Utility"

    `client.utility`, [`Utility`][pokelance.ext.utility.Utility]

    | Category       | Key        | Returns                                                                                         |
    | -------------- | ---------- | ----------------------------------------------------------------------------------------------- |
    | `language`     | name or id | [`models.Language`][pokelance.models.common.models.Language]                                    |
    | `api-metadata` | *none*     | [`models.APIMetadata`][pokelance.models.common.models.APIMetadata], singleton, no list endpoint |

    !!! warning "Not part of `getch_data` / `from_url`"
        `utility` is **not** registered in
        [`ExtensionEnum`][pokelance.constants.ExtensionEnum], so
        [`getch_data`][pokelance.client.PokeLance.getch_data] and
        [`from_url`][pokelance.client.PokeLance.from_url] can't dispatch to it. Call
        `client.utility.fetch_language(...)` / `client.utility.fetch_api_metadata()`
        directly instead.

## Secondary caches (id-only, no list endpoint)

A handful of categories, `machine`, `evolution-chain`, `characteristic`, `contest-effect`,
`super-contest-effect`, `language`, `api-metadata`, use a secondary keyed cache instead of
the regular [`BaseCache`][pokelance.cache.cache.BaseCache]. PokéAPI doesn't give these a
stable `name`, only a numeric id embedded in the resource URL, so they're addressed by
**id only**, not name, and their endpoint registry (when one exists) keys by the id parsed
out of the URL rather than a `name` field in the payload.

Here's the contrast in practice:

=== "Regular category (has a name)"

    ```json
    {
      "id": 1,
      "name": "cheri",
      "growth_time": 3,
      ...
    }
    ```

    ```python
    await client.berry.fetch_berry("cheri")  # or fetch_berry(1), both work
    ```

=== "Secondary category (id only)"

    ```json
    {
      "id": 1,
      "descriptions": [
        {
          "description": "Loves to eat",
          "language": {...},
        }
      ],
      ...
    }
    ```

    ```python
    await client.pokemon.fetch_characteristic(1)  # no name to fetch by
    ```

`api-metadata` has no list endpoint at all (it's a true singleton, `GET /meta`) and is
gracefully skipped during [`setup_hook`][pokelance.client.PokeLance.setup_hook] when populating
the endpoint registries.

## Programmatic access via `ExtensionEnum`

If you're building something generic (a REPL, a lookup endpoint or a cli tool, ...), the categories
above are also available as data through
[`pokelance.constants.ExtensionEnum`][pokelance.constants.ExtensionEnum]. Note that, because
of the `__get__` descriptor on [`BaseEnum`][pokelance.constants.BaseEnum] this only applies
when *iterating* the enum, direct attribute access like `ExtensionEnum.Pokemon` returns the
underlying [`PokemonExtension`][pokelance.constants.PokemonExtension] object directly rather
than the enum member:

```python exec="true" source="above" result="text"
from pokelance.constants import ExtensionEnum

for ext in ExtensionEnum:
    print(f"{ext.name:<10} -> {', '.join(ext.value.categories)}")
```

This is exactly what powers [`getch_data`](fetching_data.md#one-call-for-any-extension-getch_data)'s
extension/category validation.
