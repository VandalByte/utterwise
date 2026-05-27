from __future__ import annotations

from utterwise.classifiers.rules import exact_rules, numeric_candidates
from utterwise.detectors.basic import DetectionFlags
from utterwise.tokens import Token


def classify(tokens: list[Token], flags: DetectionFlags) -> list[Token]:
    for index, token in enumerate(tokens):
        token.context = _context_for(tokens, index)

        if _apply_exact_rule(token):
            continue

        candidates = numeric_candidates(token)
        if not candidates:
            continue

        token.candidates = candidates
        best = max(candidates, key=lambda candidate: candidate.confidence)
        token.type = best.type
        token.confidence = best.confidence
        token.metadata["matched_rule"] = best.rule
        token.metadata["classification_reason"] = best.reason
    return tokens


def _apply_exact_rule(token: Token) -> bool:
    for rule in exact_rules():
        if not rule.matches(token):
            continue

        token.type = rule.token_type
        token.confidence = rule.confidence
        token.metadata["matched_rule"] = rule.name
        token.metadata["classification_reason"] = rule.reason
        return True
    return False


def _context_for(tokens: list[Token], index: int) -> dict[str, list[str]]:
    previous_tokens = tokens[max(0, index - 3) : index]
    next_tokens = tokens[index + 1 : index + 4]
    return {
        "previous_words": [
            token.value.lower() for token in previous_tokens if token.type == "WORD"
        ],
        "next_words": [
            token.value.lower() for token in next_tokens if token.type == "WORD"
        ],
    }
