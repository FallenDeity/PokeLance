import asyncio
import collections
import itertools
import json
import typing as t

from pokelance import PokeLance
from pokelance.models import EvolutionChain, PokemonSpecies
from pokelance.models.abstract.evolution import ChainLink

DATA = t.Dict[str, t.Any]

FORM_FLAGS: t.Final[t.Tuple[str, ...]] = (
    "alola",
    "hisui",
    "galar",
    "paldea",
    "low-key",
    "dusk",
    "dawn",
    "ultra",
    "midnight",
    "strike",
    "wormadam",
    "segment",
    "family",
    "breed",
    "striped",
    "male",
    "female",
    "small",
    "average",
    "large",
    "super",
    "normal",
    "attack",
    "defense",
    "speed",
    "rotom",
    "original",
    "phony",
    "antique",
    "dada",
    "bloodmoon",
    "plumage",
    "tatsugiri",
    "gimmighoul",
    "origin",
    "altered",
    "arceus",
    "sky",
    "therian",
    "kyurem",
    "resolute",
    "oricorio",
    "miraidon",
    "koraidon",
    "eternal",
)
BATTLE_FORMS: t.Final[t.Tuple[str, ...]] = (
    "mega",
    "sunny",
    "rainy",
    "snowy",
    "primal",
    "overcast",
    "sunshine",
    "zen",
    "blade",
    "pirouette",
    "ash",
    "battle",
    "10",
    "50",
    "complete",
    "unbound",
    "school",
    "red",
    "blue",
    "orange",
    "yellow",
    "green",
    "blue",
    "indigo",
    "violet",
    "busted",
    "utlra",
    "gulping",
    "gorging",
    "gmax",
    "noice",
    "hangry",
    "crowned",
    "eternamax",
    "ice",
    "shadow",
    "hero",
    "stellar",
    "terastal",
    "wellspring",
    "hearthflame",
    "cornerstone",
)
BATTLE_FORM_FILTERS: t.Final[t.Tuple[str, ...]] = (
    "meteor",
    "totem",
    "wormadam",
    "plumage",
    "striped",
)
INVALID_FORMS: t.Final[t.Tuple[str, ...]] = (
    "gmax",  # gmax pokemon like toxtricity
    "totem",  # totem pokemon like marowak
    "zen",  # galarian darmanitan zen mode
    "meteor",  # minior meteor form
    "cap",  # cap pikachu
)
# evolutions that have multiple forms but all of them evolve only to a specific form
CONVERGING_EVOLUTIONS: t.Final[t.Tuple[str, ...]] = (
    "gimmighoul",
    "slowbro",
)
NO_EVOLUTIONS: t.Final[t.Tuple[str, ...]] = ("floette-eternal",)

ENABLE_BATTLE_FORMS = False


client = PokeLance(cache_endpoints=False)


def match_battle_form(name: str) -> bool:
    return any(f"-{i}" in name for i in BATTLE_FORMS) and not any(f"-{i}" in name for i in BATTLE_FORM_FILTERS)


def match_no_evolution(name: str) -> bool:
    return name in NO_EVOLUTIONS


def match_variety(name: str) -> bool:
    if name in NO_EVOLUTIONS:
        return False
    if len(name.split("-")) > 1:
        _d_form_flags = [i for i in FORM_FLAGS if "-" in i]
        _d_invalid_forms = [i for i in INVALID_FORMS if "-" in i]
        _form_flags = [i for i in FORM_FLAGS if "-" not in i]
        _invalid_forms = [i for i in INVALID_FORMS if "-" not in i]
        _form_flag = any(i == segment for segment in name.split("-") for i in _form_flags)
        _invalid_form = any(i == segment for segment in name.split("-") for i in _invalid_forms)
        _d_form_flag = any(i in name for i in _d_form_flags)
        _d_invalid_form = any(i in name for i in _d_invalid_forms)
        return any((_d_form_flag, _form_flag)) and not any((_d_invalid_form, _invalid_form))
    return False


async def get_evolutions(data: EvolutionChain) -> t.Tuple[DATA, DATA]:
    evolution_dict = {}
    details_dict = {}

    def _clean_dict(d: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        return {k: _clean_dict(v) if isinstance(v, dict) else v for k, v in d.items() if k != "raw"}

    async def process_evolution_chain(chain: ChainLink, n: int = 0) -> None:
        mon_name = (await client.pokemon.fetch_pokemon_species(chain.species.name)).varieties[0].pokemon.name
        if chain.evolves_to:
            evolution_dict[mon_name] = [
                (await client.pokemon.fetch_pokemon_species(i.species.name)).varieties[0].pokemon.name
                for i in chain.evolves_to
            ]
            details_dict[mon_name] = [
                _clean_dict(details.simplified_details) | {"depth": n} for details in chain.evolution_details  # type: ignore
            ]
            for evo in chain.evolves_to:
                await process_evolution_chain(evo, n + 1)
        else:
            evolution_dict[mon_name] = []
            details_dict[mon_name] = [
                _clean_dict(details.simplified_details) | {"depth": n} for details in chain.evolution_details  # type: ignore
            ]

    await process_evolution_chain(data.chain)
    return evolution_dict, details_dict


def stringify_dict(data: t.List[t.Dict[str, t.Any]]) -> str:
    common = collections.defaultdict(set)
    for i in data:
        for k, v in i.items():
            common[k].add(v["name"] if isinstance(v, dict) else v)
    return "".join([f"{k}: {', '.join(v)}\n" if len(v) > 1 else f"{k}: {v.pop()}\n" for k, v in common.items()])


def converging_evolution(varieties: t.List[str], details: t.List[t.Dict[str, t.Any]]) -> None:
    evos = details[:]
    evo_map = {k: v for i in evos for k, v in i.items()}
    if any(i in varieties for i in CONVERGING_EVOLUTIONS):
        for _ in range(len(varieties)):
            details.append(evo_map)


def converge_data(evolution_dict: DATA, details_dict: DATA, variety_dict: t.Optional[DATA]) -> DATA:
    if not variety_dict:
        return {k: {i: details_dict[i] for i in v} for k, v in evolution_dict.items()}
    final: DATA = {}
    keys: t.List[str] = []
    for k, v in evolution_dict.items():
        varieties = variety_dict.get(k, [k])
        details = [
            {j: [details_dict.get(i, [])[0 if (lx := len(details_dict.get(i, []))) == 1 else (n - 1) % lx]]}
            for i in v
            for n, j in enumerate(variety_dict.get(i, [i]), start=1)
        ]
        # for basculin where it has 3 forms but evolves only from the white stripe form, so we just add another white stripe form
        # pokeapi holds no such context about forms, so we have to manually add them
        if len(details) == 2 and set(list(i.keys())[0].split("-")[-1] for i in details) == {"male", "female"}:
            varieties += [varieties[-1]]
        # cases where multiple forms evolve to a single form
        converging_evolution(varieties, details)
        varieties, details = (varieties[::-1], details[::-1]) if len(varieties) > len(details) else (varieties, details)
        for k, v in zip(itertools.cycle(varieties), details):
            final.setdefault(k, {}).update(v)
        keys.extend(varieties)
    for k in keys:
        final.setdefault(k, {})
    return final


async def main() -> None:
    branched = [
        "charmander",
        "squirtle",
        "bulbasaur",
        "wurmple",
        "wooper",
        "tyrogue",
        "toxel",
        "snorunt",
        "weavile",
        "ralts",
        "oddish",
        "exeggcute",
        "eevee",
        "cubone",
        "clamperl",
        "charcadet",
        "slowpoke",
        "scyther",
        "rockruff",
        "poliwag",
        "pichu",
        "nincada",
        "mime-jr",
        "kubfu",
        "koffing",
        "cosmog",
        "burmy",
        "applin",
        "dunsparce",
        "tandemaus",
        "cyndaquil",
        "oshawott",
        "petilil",
        "rufflet",
        "goomy",
        "bergmite",
        "rowlet",
        "vulpix",
        "sandshrew",
        "diglett",
        "darumaka",
        "meowth",
        "growlithe",
        "geodude",
        "ponyta",
        "farfetchd",
        "grimer",
        "voltorb",
        "tauros",
        "articuno",
        "zapdos",
        "moltres",
        "qwilfish",
        "corsola",
        "zigzagoon",
        "yamask",
        "zorua",
        "stunfisk",
        "stantler",
        "teddiursa",
        "espurr",
        "salandit",
        "nidoran-m",
        "nidoran-f",
        "combee",
        "hippopotas",
        "tranquill",
        "frillish",
        "litleo",
        "indeedee",
        "lechonk",
        "basculin",
        "pumpkaboo",
        "deoxys",
        "magearna",
        "sinistea",
        "zarude",
        "squawkabilly",
        "tatsugiri",
        "gimmighoul",
        "sneasel",
        "aegislash",
        "mewtwo",
        "castform",
        "groudon",
        "cherrim",
        "meloetta",
        "greninja",
        "floette",
        "zygarde",
        "hoopa",
        "wishiwashi",
        "minior",
        "mimikyu",
        "necrozma",
        "cramorant",
        "eiscue",
        "zacian",
        "zamazenta",
        "eternatus",
        "calyrex",
        "palafin",
        "terapagos",
    ]
    # await client.wait_until_ready()
    # await client.pokemon.cache.pokemon_species.load_all_batch(batch_size=20)
    # branched = [i.name for i in client.pokemon.cache.pokemon_species.values()]
    processed_chains = set()
    strings = []
    for n, i in enumerate(branched, start=1):
        species: PokemonSpecies = await client.pokemon.fetch_pokemon_species(i)
        evolution_chain: EvolutionChain = await client.from_url(species.evolution_chain.url)
        if evolution_chain.id in processed_chains:
            client.logger.info(f"Skipping {evolution_chain.id} | {n}/{len(branched)}")
            continue
        processed_chains.add(evolution_chain.id)
        evo_data, detail_data = await get_evolutions(evolution_chain)
        variety_data = {}
        form_entries: DATA = {}
        for k in evo_data.keys():
            pokemon = await client.pokemon.fetch_pokemon(k)
            varieties = (await client.pokemon.fetch_pokemon_species(pokemon.species.name)).varieties
            default = [i.pokemon.name for i in varieties if i.is_default][0]
            forms = [i.pokemon.name for i in varieties if not i.is_default and match_variety(i.pokemon.name)]
            if forms:
                variety_data[default] = [default] + forms
            battle_forms = [i.pokemon.name for i in varieties if not i.is_default and match_battle_form(i.pokemon.name)]
            if ENABLE_BATTLE_FORMS and battle_forms:
                evo_data[k] = evo_data.get(k, []) + battle_forms
                form_entries.update({form: [] for form in battle_forms})
                detail_data.update({form: [{"trigger": {"name": "battle"}}] for form in battle_forms})
            no_evos = [i.pokemon.name for i in varieties if not i.is_default and match_no_evolution(i.pokemon.name)]
            if no_evos:
                form_entries.update({form: [] for form in no_evos})
                detail_data.update({form: [{"trigger": {"name": "none"}}] for form in no_evos})
        evo_data.update(form_entries)
        strings.append(json.dumps(converge_data(evo_data, detail_data, variety_data), indent=4))
        client.logger.info(f"Processed {evolution_chain.id} | {n}/{len(branched)}")
    with open("evolutions.json", "w") as f:
        f.write("[" + ",\n".join(strings) + "]")
    await client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
