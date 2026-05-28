from __future__ import annotations

from dataclasses import replace

from utterwise.tokens import Candidate, Token


CALL_WORDS = {"call", "called", "dial", "phone"}
FLIGHT_WORDS = {"flight", "route", "gate"}
MATH_WORDS = {"divided", "plus", "minus", "times", "multiply", "multiplied", "by"}
MATH_SYMBOLS = {"+", "-", "×", "*", "/", "÷", "="}
CONFIDENCE_THRESHOLD = 0.75


def disambiguate(tokens: list[Token]) -> list[Token]:
    """Resolve candidate-bearing tokens using context signals and safe fallback."""

    for token in tokens:
        if not token.candidates:
            _record_exact_trace(token)
            continue

        scored_candidates = list(token.candidates)
        signals: list[str] = []
        rule_chain = ["candidate_collection"]

        if _has_call_context(token):
            scored_candidates = _boost(scored_candidates, "PHONE", 0.52, "verb_call_before_number")
            signals.append("verb_call_before_number")
            rule_chain.append("verb_call_before_number")

        if _has_flight_context(token):
            scored_candidates = _boost(scored_candidates, "FLIGHT_NO", 0.67, "domain_flight_before_number")
            signals.append("domain_flight_before_number")
            rule_chain.append("domain_flight_before_number")

        if _has_math_context(token):
            scored_candidates = _boost(scored_candidates, "CARDINAL", 0.21, "math_context_near_number")
            signals.append("math_context_near_number")
            rule_chain.append("math_context_near_number")

        if not signals and token.context.get("token_index") == 0:
            scored_candidates = _boost(scored_candidates, "CARDINAL", 0.08, "sentence_start_cardinal_bias")
            signals.append("sentence_start_cardinal_bias")
            rule_chain.append("sentence_start_cardinal_bias")

        winner = max(scored_candidates, key=lambda candidate: candidate.confidence)
        fallback_used = False
        if winner.confidence < CONFIDENCE_THRESHOLD:
            winner = _best_cardinal(scored_candidates)
            fallback_used = True
            signals.append("low_confidence_cardinal_fallback")
            rule_chain.append("low_confidence_cardinal_fallback")

        token.candidates = scored_candidates
        token.type = winner.type
        token.confidence = winner.confidence
        token.metadata["matched_rule"] = winner.rule
        token.metadata["classification_reason"] = winner.reason
        token.metadata["winner"] = winner.type
        token.metadata["rule_chain"] = rule_chain
        token.metadata["signals"] = signals
        token.metadata["fallback_used"] = fallback_used
    return tokens


def _record_exact_trace(token: Token) -> None:
    if "matched_rule" not in token.metadata:
        return
    token.metadata.setdefault("winner", token.type)
    token.metadata.setdefault("rule_chain", [token.metadata["matched_rule"]])
    token.metadata.setdefault("signals", [])
    token.metadata.setdefault("fallback_used", False)


def _has_call_context(token: Token) -> bool:
    return bool(_context_words(token) & CALL_WORDS)


def _has_flight_context(token: Token) -> bool:
    return bool(_context_words(token) & FLIGHT_WORDS)


def _has_math_context(token: Token) -> bool:
    words = _context_words(token)
    values = set(token.context.get("previous_values", [])) | set(token.context.get("next_values", []))
    return bool((words & MATH_WORDS) or (values & MATH_SYMBOLS))


def _context_words(token: Token) -> set[str]:
    previous_words = set(token.context.get("previous_words", []))
    next_words = set(token.context.get("next_words", []))
    return previous_words | next_words


def _boost(
    candidates: list[Candidate],
    candidate_type: str,
    amount: float,
    rule: str,
) -> list[Candidate]:
    boosted = []
    for candidate in candidates:
        if candidate.type != candidate_type:
            boosted.append(candidate)
            continue
        boosted.append(
            replace(
                candidate,
                confidence=round(min(candidate.confidence + amount, 0.99), 2),
                rule=rule,
            )
        )
    return boosted


def _best_cardinal(candidates: list[Candidate]) -> Candidate:
    cardinal_candidates = [candidate for candidate in candidates if candidate.type == "CARDINAL"]
    if cardinal_candidates:
        return max(cardinal_candidates, key=lambda candidate: candidate.confidence)
    return Candidate("CARDINAL", 0.75, "low_confidence_cardinal_fallback", "safe default for unresolved ambiguity")
