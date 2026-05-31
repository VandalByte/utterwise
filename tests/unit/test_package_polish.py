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
    assert token["metadata"]["currency_code"] == "USD"


def test_expanded_currency_symbols_and_codes() -> None:
    cases = {
        "₹500": "five hundred rupees",
        "¥12.50": "twelve point five zero yen",
        "₩12.50": "twelve point five zero won",
        "₫12.50": "twelve point five zero dong",
        "INR 12.25": "twelve rupees and twenty five paise",
        "12.50 USD": "twelve dollars and fifty cents",
        "RMB 45": "forty five yuan",
    }

    for raw, spoken in cases.items():
        assert normalize(raw) == spoken


def test_brazilian_real_symbol_is_one_currency_token() -> None:
    text = "R$25.50"
    tokens = tokenize(preprocess(text))
    trace = explain(text)
    token = trace["tokens"][0]

    assert [(token.type, token.value) for token in tokens] == [("CURRENCY", "R$25.50")]
    assert normalize(text) == "twenty five Brazilian reais and fifty centavos"
    assert token["type"] == "CURRENCY"
    assert token["rule"] == "currency_exact"
    assert token["metadata"]["currency_code"] == "BRL"
    assert token["metadata"]["currency_display"] == "R$"


def test_currency_detector_for_iso_code_forms() -> None:
    text = "USD 12.50"
    tokens = tokenize(preprocess(text))
    flags = detect(text, tokens)

    assert [(token.type, token.value) for token in tokens] == [("CURRENCY", "USD 12.50")]
    assert flags.currency is True


def test_expanded_currency_can_be_disabled() -> None:
    config = NormalizeConfig(enable_currency=False)

    assert normalize("₹500", config=config) != "five hundred rupees"
    assert normalize("USD 12.50", config=config) != "twelve dollars and fifty cents"
    assert normalize("R$25.50", config=config) != "twenty five Brazilian reais and fifty centavos"


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
