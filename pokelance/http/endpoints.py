import typing as t

import attrs

__all__: t.Tuple[str, ...] = ("Endpoint", "Route")


@attrs.define(repr=True, slots=True, kw_only=True, hash=True)
class Route:
    """Represents a route for an endpoint.

    Attributes
    ----------
    endpoint: str
        The endpoint name.
    _url: str
        The URL for the route.
    _api_version: int
        The API version for the route.
    method: str
        The HTTP method for the route.
    payload: t.Optional[t.Dict[str, t.Any]]
        The payload for the route.

    Examples
    --------
    >>> pokemon = "pikachu"
    >>> route = Route(endpoint=f"/pokemon/{pokemon}", method="GET")
    """

    endpoint: str = attrs.field(factory=str)
    _url: str = "https://pokeapi.co/api/v2{endpoint}"
    _api_version: int = 2
    method: str = "GET"
    payload: t.Optional[t.Dict[str, t.Any]] = None

    def __str__(self) -> str:
        return f"<Route endpoint={self.endpoint} method={self.method}>"

    @property
    def url(self) -> str:
        return self._url.format(endpoint=self.endpoint)


class Endpoint:
    """Represents an endpoint for the API."""

    @classmethod
    def get_language_endpoints(cls) -> Route:
        """Gets the language endpoints."""
        return Route(endpoint="/language", payload={"limit": 10000})

    @classmethod
    def get_language(cls, language: t.Union[str, int]) -> Route:
        """Gets a language."""
        return Route(endpoint=f"/language/{language}")

    @classmethod
    def get_berry_endpoints(cls) -> Route:
        """Get a list of berry endpoints."""
        return Route(endpoint="/berry", payload={"limit": 10000})

    @classmethod
    def get_berry(cls, berry: t.Union[int, str]) -> Route:
        """Get a berry by its ID or name."""
        return Route(endpoint=f"/berry/{berry}")

    @classmethod
    def get_berry_firmness_endpoints(cls) -> Route:
        """Get a list of berry firmness endpoints."""
        return Route(endpoint="/berry-firmness", payload={"limit": 10000})

    @classmethod
    def get_berry_firmness(cls, berry_firmness: t.Union[int, str]) -> Route:
        """Get a berry firmness by its ID or name."""
        return Route(endpoint=f"/berry-firmness/{berry_firmness}")

    @classmethod
    def get_berry_flavor_endpoints(cls) -> Route:
        """Get a list of berry flavor endpoints."""
        return Route(endpoint="/berry-flavor", payload={"limit": 10000})

    @classmethod
    def get_berry_flavor(cls, berry_flavor: t.Union[int, str]) -> Route:
        """Get a berry flavor by its ID or name."""
        return Route(endpoint=f"/berry-flavor/{berry_flavor}")

    @classmethod
    def get_contest_type_endpoints(cls) -> Route:
        """Get a list of contest type endpoints."""
        return Route(endpoint="/contest-type", payload={"limit": 10000})

    @classmethod
    def get_contest_type(cls, contest_type: t.Union[int, str]) -> Route:
        """Get a contest type by its ID or name."""
        return Route(endpoint=f"/contest-type/{contest_type}")

    @classmethod
    def get_contest_effect_endpoints(cls) -> Route:
        """Get a list of contest effect endpoints."""
        return Route(endpoint="/contest-effect", payload={"limit": 10000})

    @classmethod
    def get_contest_effect(cls, contest_effect: int) -> Route:
        """Get a contest effect by its ID."""
        return Route(endpoint=f"/contest-effect/{contest_effect}")

    @classmethod
    def get_super_contest_effect_endpoints(cls) -> Route:
        """Get a list of super contest effect endpoints."""
        return Route(endpoint="/super-contest-effect", payload={"limit": 10000})

    @classmethod
    def get_super_contest_effect(cls, super_contest_effect: int) -> Route:
        """Get a super contest effect by its ID."""
        return Route(endpoint=f"/super-contest-effect/{super_contest_effect}")

    @classmethod
    def get_encounter_method_endpoints(cls) -> Route:
        """Get a list of encounter method endpoints."""
        return Route(endpoint="/encounter-method", payload={"limit": 10000})

    @classmethod
    def get_encounter_method(cls, encounter_method: t.Union[int, str]) -> Route:
        """Get an encounter method by its ID or name."""
        return Route(endpoint=f"/encounter-method/{encounter_method}")

    @classmethod
    def get_encounter_condition_endpoints(cls) -> Route:
        """Get a list of encounter condition endpoints."""
        return Route(endpoint="/encounter-condition", payload={"limit": 10000})

    @classmethod
    def get_encounter_condition(cls, encounter_condition: t.Union[int, str]) -> Route:
        """Get an encounter condition by its ID or name."""
        return Route(endpoint=f"/encounter-condition/{encounter_condition}")

    @classmethod
    def get_encounter_condition_value_endpoints(cls) -> Route:
        """Get a list of encounter condition value endpoints."""
        return Route(endpoint="/encounter-condition-value", payload={"limit": 10000})

    @classmethod
    def get_encounter_condition_value(cls, encounter_condition_value: t.Union[int, str]) -> Route:
        """Get an encounter condition value by its ID or name."""
        return Route(endpoint=f"/encounter-condition-value/{encounter_condition_value}")

    @classmethod
    def get_evolution_chain_endpoints(cls) -> Route:
        """Get a list of evolution chain endpoints."""
        return Route(endpoint="/evolution-chain", payload={"limit": 10000})

    @classmethod
    def get_evolution_chain(cls, evolution_chain: int) -> Route:
        """Get an evolution chain by its ID."""
        return Route(endpoint=f"/evolution-chain/{evolution_chain}")

    @classmethod
    def get_evolution_trigger_endpoints(cls) -> Route:
        """Get a list of evolution trigger endpoints."""
        return Route(endpoint="/evolution-trigger", payload={"limit": 10000})

    @classmethod
    def get_evolution_trigger(cls, evolution_trigger: t.Union[int, str]) -> Route:
        """Get an evolution trigger by its ID or name."""
        return Route(endpoint=f"/evolution-trigger/{evolution_trigger}")

    @classmethod
    def get_generation_endpoints(cls) -> Route:
        """Get a list of generation endpoints."""
        return Route(endpoint="/generation", payload={"limit": 10000})

    @classmethod
    def get_generation(cls, generation: t.Union[int, str]) -> Route:
        """Get a generation by its ID or name."""
        return Route(endpoint=f"/generation/{generation}")

    @classmethod
    def get_pokedex_endpoints(cls) -> Route:
        """Get a list of pokedex endpoints."""
        return Route(endpoint="/pokedex", payload={"limit": 10000})

    @classmethod
    def get_pokedex(cls, pokedex: t.Union[int, str]) -> Route:
        """Get a pokedex by its ID or name."""
        return Route(endpoint=f"/pokedex/{pokedex}")

    @classmethod
    def get_version_endpoints(cls) -> Route:
        """Get a list of version endpoints."""
        return Route(endpoint="/version", payload={"limit": 10000})

    @classmethod
    def get_version(cls, version: t.Union[int, str]) -> Route:
        """Get a version by its ID or name."""
        return Route(endpoint=f"/version/{version}")

    @classmethod
    def get_version_group_endpoints(cls) -> Route:
        """Get a list of version group endpoints."""
        return Route(endpoint="/version-group", payload={"limit": 10000})

    @classmethod
    def get_version_group(cls, version_group: t.Union[int, str]) -> Route:
        """Get a version group by its ID or name."""
        return Route(endpoint=f"/version-group/{version_group}")

    @classmethod
    def get_item_endpoints(cls) -> Route:
        """Get a list of item endpoints."""
        return Route(endpoint="/item", payload={"limit": 10000})

    @classmethod
    def get_item(cls, item: t.Union[int, str]) -> Route:
        """Get an item by its ID or name."""
        return Route(endpoint=f"/item/{item}")

    @classmethod
    def get_item_attribute_endpoints(cls) -> Route:
        """Get a list of item attribute endpoints."""
        return Route(endpoint="/item-attribute", payload={"limit": 10000})

    @classmethod
    def get_item_attribute(cls, item_attribute: t.Union[int, str]) -> Route:
        """Get an item attribute by its ID or name."""
        return Route(endpoint=f"/item-attribute/{item_attribute}")

    @classmethod
    def get_item_category_endpoints(cls) -> Route:
        """Get a list of item category endpoints."""
        return Route(endpoint="/item-category", payload={"limit": 10000})

    @classmethod
    def get_item_category(cls, item_category: t.Union[int, str]) -> Route:
        """Get an item category by its ID or name."""
        return Route(endpoint=f"/item-category/{item_category}")

    @classmethod
    def get_item_fling_effect_endpoints(cls) -> Route:
        """Get a list of item fling effect endpoints."""
        return Route(endpoint="/item-fling-effect", payload={"limit": 10000})

    @classmethod
    def get_item_fling_effect(cls, item_fling_effect: t.Union[int, str]) -> Route:
        """Get an item fling effect by its ID or name."""
        return Route(endpoint=f"/item-fling-effect/{item_fling_effect}")

    @classmethod
    def get_item_pocket_endpoints(cls) -> Route:
        """Get a list of item pocket endpoints."""
        return Route(endpoint="/item-pocket", payload={"limit": 10000})

    @classmethod
    def get_item_pocket(cls, item_pocket: t.Union[int, str]) -> Route:
        """Get an item pocket by its ID or name."""
        return Route(endpoint=f"/item-pocket/{item_pocket}")

    @classmethod
    def get_location_endpoints(cls) -> Route:
        """Get a list of location endpoints."""
        return Route(endpoint="/location", payload={"limit": 10000})

    @classmethod
    def get_location(cls, location: t.Union[int, str]) -> Route:
        """Get a location by its ID or name."""
        return Route(endpoint=f"/location/{location}")

    @classmethod
    def get_location_area_endpoints(cls) -> Route:
        """Get a list of location area endpoints."""
        return Route(endpoint="/location-area", payload={"limit": 10000})

    @classmethod
    def get_location_area(cls, location_area: t.Union[int, str]) -> Route:
        """Get a location area by its ID or name."""
        return Route(endpoint=f"/location-area/{location_area}")

    @classmethod
    def get_pal_park_area_endpoints(cls) -> Route:
        """Get a list of pal park area endpoints."""
        return Route(endpoint="/pal-park-area", payload={"limit": 10000})

    @classmethod
    def get_pal_park_area(cls, pal_park_area: t.Union[int, str]) -> Route:
        """Get a pal park area by its ID or name."""
        return Route(endpoint=f"/pal-park-area/{pal_park_area}")

    @classmethod
    def get_region_endpoints(cls) -> Route:
        """Get a list of region endpoints."""
        return Route(endpoint="/region", payload={"limit": 10000})

    @classmethod
    def get_region(cls, region: t.Union[int, str]) -> Route:
        """Get a region by its ID or name."""
        return Route(endpoint=f"/region/{region}")

    @classmethod
    def get_machine_endpoints(cls) -> Route:
        """Get a list of machine endpoints."""
        return Route(endpoint="/machine", payload={"limit": 10000})

    @classmethod
    def get_machine(cls, machine: int) -> Route:
        """Get a machine by its ID."""
        return Route(endpoint=f"/machine/{machine}")

    @classmethod
    def get_move_endpoints(cls) -> Route:
        """Get a list of move endpoints."""
        return Route(endpoint="/move", payload={"limit": 10000})

    @classmethod
    def get_move(cls, move: t.Union[int, str]) -> Route:
        """Get a move by its ID or name."""
        return Route(endpoint=f"/move/{move}")

    @classmethod
    def get_move_ailment_endpoints(cls) -> Route:
        """Get a list of move ailment endpoints."""
        return Route(endpoint="/move-ailment", payload={"limit": 10000})

    @classmethod
    def get_move_ailment(cls, move_ailment: t.Union[int, str]) -> Route:
        """Get a move ailment by its ID or name."""
        return Route(endpoint=f"/move-ailment/{move_ailment}")

    @classmethod
    def get_move_battle_style_endpoints(cls) -> Route:
        """Get a list of move battle style endpoints."""
        return Route(endpoint="/move-battle-style", payload={"limit": 10000})

    @classmethod
    def get_move_battle_style(cls, move_battle_style: t.Union[int, str]) -> Route:
        """Get a move battle style by its ID or name."""
        return Route(endpoint=f"/move-battle-style/{move_battle_style}")

    @classmethod
    def get_move_category_endpoints(cls) -> Route:
        """Get a list of move category endpoints."""
        return Route(endpoint="/move-category", payload={"limit": 10000})

    @classmethod
    def get_move_category(cls, move_category: t.Union[int, str]) -> Route:
        """Get a move category by its ID or name."""
        return Route(endpoint=f"/move-category/{move_category}")

    @classmethod
    def get_move_damage_class_endpoints(cls) -> Route:
        """Get a list of move damage class endpoints."""
        return Route(endpoint="/move-damage-class", payload={"limit": 10000})

    @classmethod
    def get_move_damage_class(cls, move_damage_class: t.Union[int, str]) -> Route:
        """Get a move damage class by its ID or name."""
        return Route(endpoint=f"/move-damage-class/{move_damage_class}")

    @classmethod
    def get_move_learn_method_endpoints(cls) -> Route:
        """Get a list of move learn method endpoints."""
        return Route(endpoint="/move-learn-method", payload={"limit": 10000})

    @classmethod
    def get_move_learn_method(cls, move_learn_method: t.Union[int, str]) -> Route:
        """Get a move learn method by its ID or name."""
        return Route(endpoint=f"/move-learn-method/{move_learn_method}")

    @classmethod
    def get_move_target_endpoints(cls) -> Route:
        """Get a list of move target endpoints."""
        return Route(endpoint="/move-target", payload={"limit": 10000})

    @classmethod
    def get_move_target(cls, move_target: t.Union[int, str]) -> Route:
        """Get a move target by its ID or name."""
        return Route(endpoint=f"/move-target/{move_target}")

    @classmethod
    def get_ability_endpoints(cls) -> Route:
        """Get a list of ability endpoints."""
        return Route(endpoint="/ability", payload={"limit": 10000})

    @classmethod
    def get_ability(cls, ability: t.Union[int, str]) -> Route:
        """Get an ability by its ID or name."""
        return Route(endpoint=f"/ability/{ability}")

    @classmethod
    def get_characteristic_endpoints(cls) -> Route:
        """Get a list of characteristic endpoints."""
        return Route(endpoint="/characteristic", payload={"limit": 10000})

    @classmethod
    def get_characteristic(cls, characteristic: int) -> Route:
        """Get a characteristic by its ID."""
        return Route(endpoint=f"/characteristic/{characteristic}")

    @classmethod
    def get_egg_group_endpoints(cls) -> Route:
        """Get a list of egg group endpoints."""
        return Route(endpoint="/egg-group", payload={"limit": 10000})

    @classmethod
    def get_egg_group(cls, egg_group: t.Union[int, str]) -> Route:
        """Get an egg group by its ID or name."""
        return Route(endpoint=f"/egg-group/{egg_group}")

    @classmethod
    def get_gender_endpoints(cls) -> Route:
        """Get a list of gender endpoints."""
        return Route(endpoint="/gender", payload={"limit": 10000})

    @classmethod
    def get_gender(cls, gender: t.Union[int, str]) -> Route:
        """Get a gender by its ID or name."""
        return Route(endpoint=f"/gender/{gender}")

    @classmethod
    def get_growth_rate_endpoints(cls) -> Route:
        """Get a list of growth rate endpoints."""
        return Route(endpoint="/growth-rate", payload={"limit": 10000})

    @classmethod
    def get_growth_rate(cls, growth_rate: t.Union[int, str]) -> Route:
        """Get a growth rate by its ID or name."""
        return Route(endpoint=f"/growth-rate/{growth_rate}")

    @classmethod
    def get_nature_endpoints(cls) -> Route:
        """Get a list of nature endpoints."""
        return Route(endpoint="/nature", payload={"limit": 10000})

    @classmethod
    def get_nature(cls, nature: t.Union[int, str]) -> Route:
        """Get a nature by its ID or name."""
        return Route(endpoint=f"/nature/{nature}")

    @classmethod
    def get_location_area_encounter_endpoints(cls) -> Route:
        """Get a list of location area encounter endpoints."""
        return Route(endpoint="/pokemon", payload={"limit": 10000})

    @classmethod
    def get_location_area_encounter(cls, name: t.Union[int, str]) -> Route:
        """Get a location area encounter by its ID or name."""
        return Route(endpoint=f"/pokemon/{name}/encounters")

    @classmethod
    def get_pokeathlon_stat_endpoints(cls) -> Route:
        """Get a list of pokeathlon stat endpoints."""
        return Route(endpoint="/pokeathlon-stat", payload={"limit": 10000})

    @classmethod
    def get_pokeathlon_stat(cls, pokeathlon_stat: t.Union[int, str]) -> Route:
        """Get a pokeathlon stat by its ID or name."""
        return Route(endpoint=f"/pokeathlon-stat/{pokeathlon_stat}")

    @classmethod
    def get_pokemon_endpoints(cls) -> Route:
        """Get a list of pokemon endpoints."""
        return Route(endpoint="/pokemon", payload={"limit": 10000})

    @classmethod
    def get_pokemon(cls, pokemon: t.Union[int, str]) -> Route:
        """Get a pokemon by its ID or name."""
        return Route(endpoint=f"/pokemon/{pokemon}")

    @classmethod
    def get_pokemon_color_endpoints(cls) -> Route:
        """Get a list of pokemon color endpoints."""
        return Route(endpoint="/pokemon-color", payload={"limit": 10000})

    @classmethod
    def get_pokemon_color(cls, pokemon_color: t.Union[int, str]) -> Route:
        """Get a pokemon color by its ID or name."""
        return Route(endpoint=f"/pokemon-color/{pokemon_color}")

    @classmethod
    def get_pokemon_form_endpoints(cls) -> Route:
        """Get a list of pokemon form endpoints."""
        return Route(endpoint="/pokemon-form", payload={"limit": 10000})

    @classmethod
    def get_pokemon_form(cls, pokemon_form: t.Union[int, str]) -> Route:
        """Get a pokemon form by its ID or name."""
        return Route(endpoint=f"/pokemon-form/{pokemon_form}")

    @classmethod
    def get_pokemon_habitat_endpoints(cls) -> Route:
        """Get a list of pokemon habitat endpoints."""
        return Route(endpoint="/pokemon-habitat", payload={"limit": 10000})

    @classmethod
    def get_pokemon_habitat(cls, pokemon_habitat: t.Union[int, str]) -> Route:
        """Get a pokemon habitat by its ID or name."""
        return Route(endpoint=f"/pokemon-habitat/{pokemon_habitat}")

    @classmethod
    def get_pokemon_shape_endpoints(cls) -> Route:
        """Get a list of pokemon shape endpoints."""
        return Route(endpoint="/pokemon-shape", payload={"limit": 10000})

    @classmethod
    def get_pokemon_shape(cls, pokemon_shape: t.Union[int, str]) -> Route:
        """Get a pokemon shape by its ID or name."""
        return Route(endpoint=f"/pokemon-shape/{pokemon_shape}")

    @classmethod
    def get_pokemon_species_endpoints(cls) -> Route:
        """Get a list of pokemon species endpoints."""
        return Route(endpoint="/pokemon-species", payload={"limit": 10000})

    @classmethod
    def get_pokemon_species(cls, pokemon_species: t.Union[int, str]) -> Route:
        """Get a pokemon species by its ID or name."""
        return Route(endpoint=f"/pokemon-species/{pokemon_species}")

    @classmethod
    def get_stat_endpoints(cls) -> Route:
        """Get a list of stat endpoints."""
        return Route(endpoint="/stat", payload={"limit": 10000})

    @classmethod
    def get_stat(cls, stat: t.Union[int, str]) -> Route:
        """Get a stat by its ID or name."""
        return Route(endpoint=f"/stat/{stat}")

    @classmethod
    def get_type_endpoints(cls) -> Route:
        """Get a list of type endpoints."""
        return Route(endpoint="/type", payload={"limit": 10000})

    @classmethod
    def get_type(cls, type_: t.Union[int, str]) -> Route:
        """Get a type by its ID or name."""
        return Route(endpoint=f"/type/{type_}")
