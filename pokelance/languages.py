import enum
import typing as t

from pokelance.http import Endpoint
from pokelance.models import Language

__all__: t.Tuple[str, ...] = ("Languages",)
LANGUAGE = Endpoint.get_language_endpoints().url


class Languages(enum.Enum):
    """
    Languages that are available on Pokeapi.

    Attributes
    ----------
    JAPANESE: Language
        The Japanese language.
    ROOMAJI: Language
        The Japanese language written in roomaji.
    KOREAN: Language
        The Korean language.
    CHINESE: Language
        The Chinese language.
    FRENCH: Language
        The French language.
    GERMAN: Language
        The German language.
    SPANISH: Language
        The Spanish language.
    ITALIAN: Language
        The Italian language.
    CZECH: Language
        The Czech language.
    ENGLISH: Language
        The English language.
    JA: Language
        The Japanese language.
    CHINESE_SIMPLIFIED: Language
        The Chinese language written in simplified Chinese.
    PORTUGAL_BRAZILIAN: Language
        The Portuguese language written in Brazilian Portuguese.
    """

    JAPANESE = Language.from_payload(
        {
            "id": 1,
            "iso3166": "jp",
            "iso639": "ja",
            "name": "ja-Hrkt",
            "names": [
                {"language": {"name": "ja-Hrkt", "url": f"{LANGUAGE}/1/"}, "name": "日本語"},
                {"language": {"name": "ko", "url": f"{LANGUAGE}/3/"}, "name": "일본어"},
                {"language": {"name": "fr", "url": f"{LANGUAGE}/5/"}, "name": "Japonais"},
                {"language": {"name": "de", "url": f"{LANGUAGE}/6/"}, "name": "Japanisch"},
                {"language": {"name": "es", "url": f"{LANGUAGE}/7/"}, "name": "Japonés"},
                {"language": {"name": "en", "url": f"{LANGUAGE}/9/"}, "name": "Japanese"},
            ],
            "official": True,
        }
    )
    ROOMAJI = Language.from_payload(
        {
            "id": 2,
            "iso3166": "jp",
            "iso639": "ja",
            "name": "roomaji",
            "names": [
                {"language": {"name": "ja-Hrkt", "url": f"{LANGUAGE}/1/"}, "name": "正式ローマジ"},
                {"language": {"name": "ko", "url": f"{LANGUAGE}/3/"}, "name": "정식 로마자"},
                {"language": {"name": "fr", "url": f"{LANGUAGE}/5/"}, "name": "Romaji"},
                {"language": {"name": "de", "url": f"{LANGUAGE}/6/"}, "name": "Rōmaji"},
                {
                    "language": {"name": "en", "url": f"{LANGUAGE}/9/"},
                    "name": "Official roomaji",
                },
            ],
            "official": True,
        }
    )
    KOREAN = Language.from_payload(
        {
            "id": 3,
            "iso3166": "kr",
            "iso639": "ko",
            "name": "ko",
            "names": [
                {"language": {"name": "ja-Hrkt", "url": f"{LANGUAGE}/1/"}, "name": "韓国語"},
                {"language": {"name": "ko", "url": f"{LANGUAGE}/3/"}, "name": "한국어"},
                {"language": {"name": "fr", "url": f"{LANGUAGE}/5/"}, "name": "Coréen"},
                {"language": {"name": "de", "url": f"{LANGUAGE}/6/"}, "name": "Koreanisch"},
                {"language": {"name": "es", "url": f"{LANGUAGE}/7/"}, "name": "Coreano"},
                {"language": {"name": "en", "url": f"{LANGUAGE}/9/"}, "name": "Korean"},
            ],
            "official": True,
        }
    )
    CHINESE = Language.from_payload(
        {
            "id": 4,
            "iso3166": "cn",
            "iso639": "zh",
            "name": "zh-Hant",
            "names": [
                {"language": {"name": "ja-Hrkt", "url": f"{LANGUAGE}/1/"}, "name": "中国語"},
                {"language": {"name": "ko", "url": f"{LANGUAGE}/3/"}, "name": "중국어"},
                {"language": {"name": "fr", "url": f"{LANGUAGE}/5/"}, "name": "Chinois"},
                {"language": {"name": "de", "url": f"{LANGUAGE}/6/"}, "name": "Chinesisch"},
                {"language": {"name": "es", "url": f"{LANGUAGE}/7/"}, "name": "Chino"},
                {"language": {"name": "en", "url": f"{LANGUAGE}/9/"}, "name": "Chinese"},
            ],
            "official": True,
        }
    )
    FRENCH = Language.from_payload(
        {
            "id": 5,
            "iso3166": "fr",
            "iso639": "fr",
            "name": "fr",
            "names": [
                {"language": {"name": "ja-Hrkt", "url": f"{LANGUAGE}/1/"}, "name": "フランス語"},
                {"language": {"name": "ko", "url": f"{LANGUAGE}/3/"}, "name": "프랑스어"},
                {"language": {"name": "fr", "url": f"{LANGUAGE}/5/"}, "name": "Français"},
                {"language": {"name": "de", "url": f"{LANGUAGE}/6/"}, "name": "Französisch"},
                {"language": {"name": "es", "url": f"{LANGUAGE}/7/"}, "name": "Francés"},
                {"language": {"name": "en", "url": f"{LANGUAGE}/9/"}, "name": "French"},
            ],
            "official": True,
        }
    )
    GERMAN = Language.from_payload(
        {
            "id": 6,
            "iso3166": "de",
            "iso639": "de",
            "name": "de",
            "names": [
                {"language": {"name": "ja-Hrkt", "url": f"{LANGUAGE}/1/"}, "name": "ドイツ語"},
                {"language": {"name": "ko", "url": f"{LANGUAGE}/3/"}, "name": "도이치어"},
                {"language": {"name": "fr", "url": f"{LANGUAGE}/5/"}, "name": "Allemand"},
                {"language": {"name": "de", "url": f"{LANGUAGE}/6/"}, "name": "Deutsch"},
                {"language": {"name": "es", "url": f"{LANGUAGE}/7/"}, "name": "Alemán"},
                {"language": {"name": "en", "url": f"{LANGUAGE}/9/"}, "name": "German"},
            ],
            "official": True,
        }
    )
    SPANISH = Language.from_payload(
        {
            "id": 7,
            "iso3166": "es",
            "iso639": "es",
            "name": "es",
            "names": [
                {"language": {"name": "ja-Hrkt", "url": f"{LANGUAGE}/1/"}, "name": "西語"},
                {"language": {"name": "ko", "url": f"{LANGUAGE}/3/"}, "name": "스페인어"},
                {"language": {"name": "fr", "url": f"{LANGUAGE}/5/"}, "name": "Espagnol"},
                {"language": {"name": "de", "url": f"{LANGUAGE}/6/"}, "name": "Spanisch"},
                {"language": {"name": "es", "url": f"{LANGUAGE}/7/"}, "name": "Español"},
                {"language": {"name": "en", "url": f"{LANGUAGE}/9/"}, "name": "Spanish"},
            ],
            "official": True,
        }
    )
    ITALIAN = Language.from_payload(
        {
            "id": 8,
            "iso3166": "it",
            "iso639": "it",
            "name": "it",
            "names": [
                {"language": {"name": "ja-Hrkt", "url": f"{LANGUAGE}/1/"}, "name": "伊語"},
                {"language": {"name": "ko", "url": f"{LANGUAGE}/3/"}, "name": "이탈리아어"},
                {"language": {"name": "fr", "url": f"{LANGUAGE}/5/"}, "name": "Italien"},
                {"language": {"name": "de", "url": f"{LANGUAGE}/6/"}, "name": "Italienisch"},
                {"language": {"name": "es", "url": f"{LANGUAGE}/7/"}, "name": "Italiano"},
                {"language": {"name": "en", "url": f"{LANGUAGE}/9/"}, "name": "Italian"},
            ],
            "official": True,
        }
    )
    ENGLISH = Language.from_payload(
        {
            "id": 9,
            "iso3166": "us",
            "iso639": "en",
            "name": "en",
            "names": [
                {"language": {"name": "ja-Hrkt", "url": f"{LANGUAGE}/1/"}, "name": "英語"},
                {"language": {"name": "ko", "url": f"{LANGUAGE}/3/"}, "name": "영어"},
                {"language": {"name": "fr", "url": f"{LANGUAGE}/5/"}, "name": "Anglais"},
                {"language": {"name": "de", "url": f"{LANGUAGE}/6/"}, "name": "Englisch"},
                {"language": {"name": "es", "url": f"{LANGUAGE}/7/"}, "name": "Inglés"},
                {"language": {"name": "en", "url": f"{LANGUAGE}/9/"}, "name": "English"},
            ],
            "official": True,
        }
    )
    CZECH = Language.from_payload(
        {
            "id": 10,
            "iso3166": "cz",
            "iso639": "cs",
            "name": "cs",
            "names": [
                {"language": {"name": "ja-Hrkt", "url": f"{LANGUAGE}/1/"}, "name": "チェコ語"},
                {"language": {"name": "ko", "url": f"{LANGUAGE}/3/"}, "name": "체코어"},
                {"language": {"name": "fr", "url": f"{LANGUAGE}/5/"}, "name": "Tchèque"},
                {"language": {"name": "de", "url": f"{LANGUAGE}/6/"}, "name": "Tschechisch"},
                {"language": {"name": "es", "url": f"{LANGUAGE}/7/"}, "name": "Checo"},
                {"language": {"name": "en", "url": f"{LANGUAGE}/9/"}, "name": "Czech"},
            ],
            "official": False,
        }
    )
    JA = Language.from_payload({"id": 11, "iso3166": "jp", "iso639": "ja", "name": "ja", "names": [], "official": True})
    CHINESE_SIMPLIFIED = Language.from_payload(
        {"id": 12, "iso3166": "cn", "iso639": "zh", "name": "zh-Hans", "names": [], "official": True}
    )
    PORTUGAL_BRAZILIAN = Language.from_payload(
        {"id": 13, "iso3166": "br", "iso639": "pt-BR", "name": "pt-BR", "names": [], "official": False}
    )

    def __str__(self) -> str:
        """
        Returns the name of the language.
        """
        return str(self.value.name)

    def __int__(self) -> int:
        """
        Returns the id of the language.
        """
        return int(self.value.id)
