# Utterwise

Utterwise is a deterministic semantic text normalizer for speech pipelines.

It turns text such as:

```text
Visit https://openai.com in 2024.
```

into:

```text
Visit open ai dot com in twenty twenty four
```

## Quick Start

```python
from utterwise import normalize, normalize_ssml, explain

normalize("A & B in 2024")
normalize_ssml("hello@example.com")
explain("I have 42 apples")
```

### What These Methods Do

`normalize(...)` returns speech-friendly plain text. It cleans lightweight
Markdown, tokenizes the input, classifies semantic tokens, resolves simple
ambiguity, and verbalizes symbols, numbers, years, URLs, and emails.

```python
normalize("A & B in 2024")
# "A and B in twenty twenty four"
```

`normalize_ssml(...)` runs the same normalization pipeline, then wraps the
spoken result in a minimal SSML document.

```python
normalize_ssml("hello@example.com")
# "<speak>hello at example dot com</speak>"
```

`explain(...)` returns a trace dictionary instead of only the final text. Use it
when you want to see which rule fired for each token, the token type, confidence
score, source span, candidates, and metadata.

```python
explain("I have 42 apples")
# {
#   "output": "I have forty two apples",
#   "tokens": [
#     {"value": "I", "type": "WORD", "spoken": "I", ...},
#     {"value": "42", "type": "CARDINAL", "spoken": "forty two", ...}
#   ]
# }
```

## Development Tests

Run the interactive development menu:

```powershell
.venv\Scripts\python.exe tests\menu.py
```

Or run pytest directly:

```powershell
.venv\Scripts\python.exe -m pytest
```
