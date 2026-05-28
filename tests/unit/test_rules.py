from __future__ import annotations

from utterwise import explain, normalize
from utterwise.classifiers import classify
from utterwise.detectors import detect
from utterwise.disambiguator import disambiguate
from utterwise.normalizers.preprocess import preprocess
from utterwise.tokenizer import tokenize


def test_exact_rule_priority_for_phone() -> None:
    trace = explain("Call 9876543210")
    phone_token = next(token for token in trace["tokens"] if token["value"] == "9876543210")

    assert phone_token["type"] == "PHONE"
    assert phone_token["rule"] == "phone_exact"
    assert normalize("Call 9876543210") == "Call nine eight seven six five four three two one zero"


def test_ambiguous_year_uses_context_candidates() -> None:
    trace = explain("Born in 1998")
    year_token = next(token for token in trace["tokens"] if token["value"] == "1998")

    assert year_token["type"] == "YEAR"
    assert year_token["rule"] == "year_context"
    assert [candidate["type"] for candidate in year_token["candidates"]] == ["YEAR", "CARDINAL"]


def test_ambiguous_cardinal_uses_context_candidates() -> None:
    trace = explain("The value is 1998")
    number_token = next(token for token in trace["tokens"] if token["value"] == "1998")

    assert number_token["type"] == "CARDINAL"
    assert number_token["rule"] == "cardinal_context"
    assert normalize("The value is 1998") == "The value is one thousand nine hundred ninety eight"


def test_contextual_version_rule() -> None:
    trace = explain("Python 3.12")
    version_token = next(token for token in trace["tokens"] if token["value"] == "3.12")

    assert version_token["type"] == "VERSION"
    assert version_token["rule"] == "version_context"
    assert normalize("Python 3.12") == "Python three point twelve"


def test_classifier_collects_multiple_candidates_for_ambiguous_911() -> None:
    text = "Call 911 immediately"
    tokens = tokenize(preprocess(text))
    classified = classify(tokens, detect(text, tokens))
    token = next(token for token in classified if token.value == "911")

    assert token.type == "CARDINAL"
    assert [candidate.type for candidate in token.candidates] == [
        "PHONE",
        "FLIGHT_NO",
        "CARDINAL",
    ]


def test_disambiguator_chooses_phone_from_call_context() -> None:
    trace = explain("Call 911 immediately")
    token = next(token for token in trace["tokens"] if token["value"] == "911")

    assert normalize("Call 911 immediately") == "Call nine one one immediately"
    assert token["type"] == "PHONE"
    assert token["winner"] == "PHONE"
    assert token["rule"] == "verb_call_before_number"
    assert "verb_call_before_number" in token["signals"]


def test_disambiguator_chooses_flight_number_from_domain_context() -> None:
    trace = explain("Flight 911 departs at 6")
    token = next(token for token in trace["tokens"] if token["value"] == "911")

    assert normalize("Flight 911 departs at 6") == "Flight nine eleven departs at six"
    assert token["type"] == "FLIGHT_NO"
    assert token["winner"] == "FLIGHT_NO"
    assert token["rule"] == "domain_flight_before_number"
    assert "domain_flight_before_number" in token["signals"]


def test_disambiguator_chooses_cardinal_from_math_context() -> None:
    trace = explain("911 divided by 3 is 303")
    token = next(token for token in trace["tokens"] if token["value"] == "911")

    assert normalize("911 divided by 3 is 303") == "nine hundred eleven divided by three is three hundred three"
    assert token["type"] == "CARDINAL"
    assert token["winner"] == "CARDINAL"
    assert token["rule"] == "math_context_near_number"
    assert "math_context_near_number" in token["signals"]


def test_sentence_start_bias_prefers_cardinal_without_stronger_context() -> None:
    trace = explain("911 was recorded")
    token = next(token for token in trace["tokens"] if token["value"] == "911")

    assert token["type"] == "CARDINAL"
    assert token["winner"] == "CARDINAL"
    assert "sentence_start_cardinal_bias" in token["signals"]
    assert token["fallback_used"] is False


def test_disambiguator_low_confidence_falls_back_to_cardinal() -> None:
    text = "About 911 cases"
    tokens = tokenize(preprocess(text))
    classified = classify(tokens, detect(text, tokens))
    token = next(token for token in classified if token.value == "911")
    token.candidates = [candidate for candidate in token.candidates if candidate.type != "CARDINAL"]

    resolved = disambiguate(classified)
    resolved_token = next(token for token in resolved if token.value == "911")

    assert resolved_token.type == "CARDINAL"
    assert resolved_token.metadata["fallback_used"] is True
    assert "low_confidence_cardinal_fallback" in resolved_token.metadata["signals"]


def test_explain_includes_phase3_trace_fields() -> None:
    trace = explain("Call 911 immediately")
    token = next(token for token in trace["tokens"] if token["value"] == "911")

    assert token["candidates"]
    assert token["winner"] == "PHONE"
    assert token["rule_chain"] == ["candidate_collection", "verb_call_before_number"]
    assert token["signals"] == ["verb_call_before_number"]
    assert token["fallback_used"] is False
