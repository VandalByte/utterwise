from __future__ import annotations

from utterwise import NormalizeConfig, explain, explain_pretty, normalize
from utterwise.cli import main
from utterwise.detectors import detect
from utterwise.normalizers.preprocess import preprocess
from utterwise.tokenizer import tokenize


def test_currency_tokenization_detection_and_explain() -> None:
    text = "$12.50"
    tokens = tokenize(preprocess(text))
    flags = detect(text, tokens)
    trace = explain(text)
    token = trace["tokens"][0]

    assert [(token.type, token.value) for token in tokens] == [("CURRENCY", "$12.50")]
    assert flags.currency is True
    assert token["type"] == "CURRENCY"
    assert token["rule"] == "currency_exact"
    assert token["spoken"] == "twelve dollars and fifty cents"


def test_date_tokenization_detection_and_explain() -> None:
    text = "03/04/2026"
    tokens = tokenize(preprocess(text))
    flags = detect(text, tokens)
    trace = explain(text)
    token = trace["tokens"][0]

    assert [(token.type, token.value) for token in tokens] == [("DATE", "03/04/2026")]
    assert flags.date is True
    assert token["type"] == "DATE"
    assert token["rule"] == "date_exact"
    assert token["spoken"] == "third of April twenty twenty six"


def test_runtime_config_can_disable_semantic_normalizers() -> None:
    config = NormalizeConfig(
        enable_math=False,
        enable_currency=False,
        enable_dates=False,
        enable_temperature=False,
    )

    assert normalize("x^2", config=config) != "x squared"
    assert normalize("$12.50", config=config) != "twelve dollars and fifty cents"
    assert normalize("03/04/2026", config=config) != "third of April twenty twenty six"
    assert normalize("25°C", config=config) != "twenty five degrees Celsius"


def test_runtime_config_convenience_kwargs() -> None:
    assert normalize("$12.50", enable_currency=False) != "twelve dollars and fifty cents"
    assert normalize("x^2", enable_math=False) != "x squared"


def test_explain_pretty_outputs_table() -> None:
    pretty = explain_pretty("Call 911 immediately")

    assert "raw" in pretty
    assert "type" in pretty
    assert "911" in pretty
    assert "PHONE" in pretty
    assert "verb_call_before_number" in pretty


def test_cli_plain_output(capsys) -> None:
    assert main(["Call 911 immediately"]) == 0

    captured = capsys.readouterr()

    assert captured.out.strip() == "Call nine one one immediately"


def test_cli_ssml_output(capsys) -> None:
    assert main(["hello@example.com", "--ssml"]) == 0

    captured = capsys.readouterr()

    assert captured.out.strip() == "<speak>hello at example dot com</speak>"


def test_cli_pretty_output(capsys) -> None:
    assert main(["Call 911 immediately", "--pretty"]) == 0

    captured = capsys.readouterr()

    assert "PHONE" in captured.out
    assert "verb_call_before_number" in captured.out
