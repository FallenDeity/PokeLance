import typing as t

__all__: t.Tuple[str, ...] = ("Language",)


class Language:
    JAPAENSE_TRADITIONAL: str = "ja-Hrkt"
    KOREAN: str = "ko"
    CHINESE_TRADITIONAL: str = "zh-Hant"
    FRENCH: str = "fr"
    GERMAN: str = "de"
    SPANISH: str = "es"
    ITALIAN: str = "it"
    ENGLISH: str = "en"
    JAPANESE_SIMPLIFIED: str = "ja"
    CHINESE_SIMPLIFIED: str = "zh-Hans"

    @classmethod
    def default(cls) -> str:
        return cls.ENGLISH

    @classmethod
    def from_name(cls, name: str) -> str:
        return getattr(cls, name.upper())
