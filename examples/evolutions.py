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
    "midnight",
    "strike",
    "wormadam",
    "segment",
    "family",
    "breed",
    "striped",
    "male",
    "female",
)
INVALID_FORMS: t.Final[t.Tuple[str, ...]] = (
    "gmax",  # gmax pokemon like toxtricity
    "cap",  # cap pikachu
    "totem",  # totem pokemon like marowak
    "galar-zen",  # galarian darmanitan zen mode
)


def match_variety(name: str) -> bool:
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


def get_evolutions(data: EvolutionChain) -> t.Tuple[DATA, DATA]:
    evolution_dict = {}
    details_dict = {}

    def _clean_dict(d: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        return {k: _clean_dict(v) if isinstance(v, dict) else v for k, v in d.items() if k != "raw"}

    def process_evolution_chain(chain: ChainLink, n: int = 0) -> None:
        if chain.evolves_to:
            evolution_dict[chain.species.name] = [evo.species.name for evo in chain.evolves_to]
            details_dict[chain.species.name] = [
                _clean_dict(details.simplified_details) | {"depth": n} for details in chain.evolution_details  # type: ignore
            ]
            for evo in chain.evolves_to:
                process_evolution_chain(evo, n + 1)
        else:
            evolution_dict[chain.species.name] = []
            details_dict[chain.species.name] = [
                _clean_dict(details.simplified_details) | {"depth": n} for details in chain.evolution_details  # type: ignore
            ]

    process_evolution_chain(data.chain)
    return evolution_dict, details_dict


def stringify_dict(data: t.List[t.Dict[str, t.Any]]) -> str:
    common = collections.defaultdict(set)
    for i in data:
        for k, v in i.items():
            common[k].add(v["name"] if isinstance(v, dict) else v)
    return "".join([f"{k}: {', '.join(v)}\n" if len(v) > 1 else f"{k}: {v.pop()}\n" for k, v in common.items()])


def converge_data(evolution_dict: DATA, details_dict: DATA, variety_dict: t.Optional[DATA]) -> DATA:
    if not variety_dict:
        return {k: {i: details_dict[i] for i in v} for k, v in evolution_dict.items()}
    final: DATA = {}
    keys: t.List[str] = []
    for k, v in evolution_dict.items():
        varieties = variety_dict.get(k, [k])
        details = [
            {j: [details_dict.get(i, [])[(lx % n) - 1 if (lx := len(details_dict.get(i, []))) == 1 else n - 1]]}
            for i in v
            for n, j in enumerate(variety_dict.get(i, [i]), start=1)
        ]
        # for basculin where it has 3 forms but evolves only from the white stripe form, so we just add another white stripe form
        # pokeapi holds no such context about forms, so we have to manually add them
        if len(details) == 2 and set(list(i.keys())[0].split("-")[-1] for i in details) == {"male", "female"}:
            varieties += [varieties[-1]]
        for k, v in zip(itertools.cycle(varieties[::-1]), details[::-1]):
            final.setdefault(k, {}).update(v)
        keys.extend(varieties)
    for k in keys:
        final.setdefault(k, {})
    return final


async def main() -> None:
    # branched = [
    #     "charmander",
    #     "squirtle",
    #     "bulbasaur",
    #     "wurmple",
    #     "wooper",
    #     "tyrogue",
    #     "toxel",
    #     "snorunt",
    #     "weavile",
    #     "ralts",
    #     "oddish",
    #     "exeggcute",
    #     "eevee",
    #     "cubone",
    #     "clamperl",
    #     "charcadet",
    #     "slowpoke",
    #     "scyther",
    #     "rockruff",
    #     "poliwag",
    #     "pichu",
    #     "nincada",
    #     "mime-jr",
    #     "kubfu",
    #     "koffing",
    #     "cosmog",
    #     "burmy",
    #     "applin",
    #     "dunsparce",
    #     "tandemaus",
    #     "cyndaquil",
    #     "oshawott",
    #     "petilil",
    #     "rufflet",
    #     "goomy",
    #     "bergmite",
    #     "rowlet",
    #     "vulpix",
    #     "sandshrew",
    #     "diglett",
    #     "darumaka",
    #     "meowth",
    #     "growlithe",
    #     "geodude",
    #     "ponyta",
    #     "farfetchd",
    #     "grimer",
    #     "voltorb",
    #     "tauros",
    #     "articuno",
    #     "zapdos",
    #     "moltres",
    #     "qwilfish",
    #     "corsola",
    #     "zigzagoon",
    #     "darumaka",
    #     "yamask",
    #     "zorua",
    #     "stunfisk",
    #     "stantler",
    #     "teddiursa",
    #     "espurr",
    #     "salandit",
    #     "nidoran-m",
    #     "nidoran-f",
    #     "combee",
    #     "hippopotas",
    #     "tranquill",
    #     "frillish",
    #     "litleo",
    #     "indeedee",
    #     "lechonk",
    #     "basculin",
    # ]
    branched = ["froakie"]
    client = PokeLance(cache_endpoints=False)
    strings = []
    for i in branched:
        species: PokemonSpecies = await client.pokemon.fetch_pokemon_species(i)
        evolution_chain: EvolutionChain = await client.from_url(species.evolution_chain.url)
        evo_data, detail_data = get_evolutions(evolution_chain)
        variety_data = {}
        for k in evo_data.keys():
            varieties = (await client.pokemon.fetch_pokemon_species(k)).varieties
            default = [i.pokemon.name for i in varieties if i.is_default][0]
            forms = [i.pokemon.name for i in varieties if not i.is_default and match_variety(i.pokemon.name)]
            if forms:
                variety_data[k] = [default] + forms
        strings.append(json.dumps(converge_data(evo_data, detail_data, variety_data), indent=4))
    with open("evolutions.json", "w") as f:
        f.write("[" + ",\n".join(strings) + "]")
    await client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
