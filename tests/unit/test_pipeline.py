from __future__ import annotations

from utterwise.detectors import detect
from utterwise.normalizers.preprocess import preprocess
from utterwise.tokenizer import tokenize


def test_preprocess_strips_common_markdown() -> None:
    assert preprocess("> # Hello **world**") == "Hello world"


def test_tokenizer_preserves_spans() -> None:
    tokens = tokenize("A & B")

    assert [(token.value, token.start, token.end) for token in tokens] == [
        ("A", 0, 1),
        ("&", 2, 3),
        ("B", 4, 5),
    ]


def test_detection_flags() -> None:
    text = "Email hello@example.com in 2024."
    tokens = tokenize(preprocess(text))
    flags = detect(text, tokens)

    assert flags.email is True
    assert flags.year is True
    assert flags.number is True
    assert flags.punctuation is True
