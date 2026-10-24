import unicodedata
import numpy as np


def narrow_language_hint(text):
    words = set(text.lower().split())
    english = len(words & {"the", "is"})
    spanish = len(words & {"el", "es"})
    if english == spanish:
        return None
    return "en" if english > spanish else "es"


def strip_marks(text):
    return "".join(
        ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn"
    )


def main():
    text = "服务正常"
    assert len(text) == 4 and len(text.encode("utf-8")) == 12 and len(text.split()) == 1
    assert narrow_language_hint("the service is ready") == "en"
    assert narrow_language_hint("el servicio es correcto") == "es"
    assert (
        narrow_language_hint("bank") is None
        and narrow_language_hint("the servicio es ready") is None
    )
    assert strip_marks("résumé") == "resume" and "résumé" != "resume"
    assert "İ".lower() == "i\u0307" and len("İ".lower()) == 2
    assert "Straße".casefold() == "strasse"
    english = np.array([1] * 9 + [0])
    spanish = np.array([1, 0])
    pooled = (english.sum() + spanish.sum()) / (len(english) + len(spanish))
    macro = (english.mean() + spanish.mean()) / 2
    assert np.isclose(pooled, 5 / 6) and macro == 0.7
    print(
        "nlp-018: codepoint/byte/whitespace differences; ambiguous-language abstention; slice metrics passed"
    )


if __name__ == "__main__":
    main()
