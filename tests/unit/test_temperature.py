from __future__ import annotations

from utterwise import explain, normalize
from utterwise.classifiers import classify
from utterwise.detectors import detect
from utterwise.normalizers.preprocess import preprocess
from utterwise.tokenizer import tokenize


def test_tokenizer_emits_temperature_tokens() -> None:
    tokens = tokenize("It is -3°C and 98.6°F")

    assert [(token.type, token.value) for token in tokens if token.type == "TEMPERATURE"] == [
        ("TEMPERATURE", "-3°C"),
        ("TEMPERATURE", "98.6°F"),
    ]


def test_tokenizer_supports_spaced_degree_temperature() -> None:
    tokens = tokenize("The temperature is 25 °C")
    temperature = next(token for token in tokens if token.type == "TEMPERATURE")

    assert temperature.value == "25 °C"


def test_bare_c_or_f_requires_temperature_context() -> None:
    assert normalize("Model 25C ships") == "Model twenty five C ships"
    assert normalize("The temperature is 25C") == "The temperature is twenty five degrees Celsius"


def test_detector_sets_temperature_flag() -> None:
    text = "The temperature is 98.6°F"
    tokens = tokenize(preprocess(text))
    flags = detect(text, tokens)

    assert flags.temperature is True


def test_classifier_records_temperature_rule() -> None:
    text = "25°C"
    tokens = tokenize(preprocess(text))
    classified = classify(tokens, detect(text, tokens))
    token = classified[0]

    assert token.type == "TEMPERATURE"
    assert token.metadata["matched_rule"] == "temperature_exact"
    assert token.confidence == 0.96


def test_explain_contains_temperature_trace() -> None:
    trace = explain("It is -3°C today")
    token = next(token for token in trace["tokens"] if token["type"] == "TEMPERATURE")

    assert token["spoken"] == "minus three degrees Celsius"
    assert token["rule"] == "temperature_exact"
    assert token["confidence"] == 0.96
