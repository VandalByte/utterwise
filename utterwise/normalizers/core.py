from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from utterwise.classifiers import classify
from utterwise.detectors import DetectionFlags, detect
from utterwise.disambiguator import disambiguate
from utterwise.formatters import format_plain, format_ssml
from utterwise.normalizers.preprocess import preprocess
from utterwise.policies import get_policy
from utterwise.tokenizer import tokenize
from utterwise.tokens import SpokenSegment, Token
from utterwise.verbalizers import verbalize


@dataclass(slots=True)
class NormalizationResult:
    """Full pipeline result used internally and by advanced integrations."""

    original_text: str
    cleaned_text: str
    output: str
    output_format: str
    policy: str
    detection: DetectionFlags
    tokens: list[Token]
    segments: list[SpokenSegment]

    def explain(self) -> dict[str, Any]:
        """Convert the result into a serializable trace dictionary."""

        return {
            "input": self.original_text,
            "cleaned": self.cleaned_text,
            "output": self.output,
            "format": self.output_format,
            "policy": self.policy,
            "detection": asdict(self.detection),
            "tokens": [
                {
                    "type": token.type,
                    "value": token.value,
                    "spoken": segment.text,
                    "rule": segment.rule,
                    "confidence": segment.confidence,
                    "start": token.start,
                    "end": token.end,
                    "candidates": [asdict(candidate) for candidate in token.candidates],
                    "winner": token.metadata.get("winner"),
                    "rule_chain": token.metadata.get("rule_chain", []),
                    "signals": token.metadata.get("signals", []),
                    "fallback_used": token.metadata.get("fallback_used", False),
                    "parser": token.metadata.get("parser"),
                    "metadata": token.metadata,
                }
                for token, segment in zip(self.tokens, self.segments)
            ],
        }


class Normalizer:
    def normalize(self, text: str, output: str = "plain", policy: str = "assistant") -> NormalizationResult:
        """Run text through preprocessing, tokenization, classification, and formatting."""

        if not isinstance(text, str):
            raise TypeError("text must be a string")
        if output not in {"plain", "ssml"}:
            raise ValueError("output must be 'plain' or 'ssml'")

        active_policy = get_policy(policy)
        cleaned = preprocess(text)
        tokens = tokenize(cleaned)
        flags = detect(text, tokens)
        classified = classify(tokens, flags)
        resolved = disambiguate(classified)
        segments = verbalize(resolved, active_policy)
        rendered = format_ssml(segments) if output == "ssml" else format_plain(segments)

        return NormalizationResult(
            original_text=text,
            cleaned_text=cleaned,
            output=rendered,
            output_format=output,
            policy=active_policy.name,
            detection=flags,
            tokens=resolved,
            segments=segments,
        )
