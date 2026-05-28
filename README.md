# Utterwise

Utterwise is a lightweight semantic text normalizer for Python voice assistants,
TTS apps, tutoring tools, and small developer projects.

It exists because compact TTS models often read useful assistant text badly:
versions, dates, money, temperatures, URLs, formulas, and ambiguous numbers can
sound strange unless they are normalized first.

```python
from utterwise import normalize

normalize("Call 911 if it reaches 25°C on 03/04/2026.")

# Output:
# "Call nine one one if it reaches twenty five degrees Celsius on third of April twenty twenty six"
```

## Install

```powershell
pip install utterwise
```

Math and LaTeX parser support is optional:

```powershell
pip install "utterwise[math]"
```

For local development with uv:

```powershell
.venv\Scripts\uv.exe sync --extra dev --extra math
```

## Quick Start

```python
from utterwise import explain, explain_pretty, normalize, normalize_ssml

normalize("Python 3.12 costs $12.50 on Jan 3, 2026")
normalize_ssml("hello@example.com")
explain("Flight 911 departs at 6")
print(explain_pretty("Call 911 immediately"))
```

## Examples

| Input | Output |
| --- | --- |
| `Born in 1998` | `Born in nineteen ninety eight` |
| `The value is 1998` | `The value is one thousand nine hundred ninety eight` |
| `Call 911 immediately` | `Call nine one one immediately` |
| `Flight 911 departs at 6` | `Flight nine eleven departs at six` |
| `Python 3.12` | `Python three point twelve` |
| `25°C` | `twenty five degrees Celsius` |
| `$12.50` | `twelve dollars and fifty cents` |
| `03/04/2026` | `third of April twenty twenty six` |
| `https://openai.com` | `open ai dot com` |
| `x^2` | `x squared` |
| `\frac{a+b}{c}` | `a plus b over c` |

## Why Not Just Regex?

Regex can replace symbols, but it cannot reliably decide what something means.
Utterwise keeps candidates and uses context before verbalizing.

```text
Call 911 immediately      -> nine one one
Flight 911 departs at 6   -> nine eleven
911 divided by 3 is 303   -> nine hundred eleven
```

That distinction is the point of the project: small, deterministic, explainable
normalization before text reaches a speech model.

## Supported Features

| Feature | Status | Example |
| --- | --- | --- |
| Numbers and years | Supported | `2024`, `42` |
| Contextual ambiguity | Supported | `911`, `1998` |
| URLs and emails | Supported | `https://openai.com`, `hello@example.com` |
| Versions | Supported | `Python 3.12`, `v3.12` |
| Phones | Supported | `9876543210`, `+1-800-555-0100` |
| Acronyms | Supported | `NASA`, `HTTP` |
| Percentages | Supported | `12.5%` |
| Temperatures | Supported | `25°C`, `98.6°F` |
| Currency | Supported | `$12.50`, `€45`, `£9.99` |
| Dates | Supported | `Jan 3, 2026`, `2026-04-03`, `03/04/2026` |
| Math and LaTeX | Optional extra | `x^2`, `\sqrt{x+1}` |
| SSML | Minimal | `<speak>...</speak>` |

Slash dates use day/month/year by default.

## Explain Mode

```python
from utterwise import explain

explain("Call 911 immediately")
```

Returns a dictionary with the normalized output, detection flags, token spans,
candidates, winner, rule chain, signals, confidence, and metadata.

For humans, use:

```python
from utterwise import explain_pretty

print(explain_pretty("Call 911 immediately"))
```

Example shape:

```text
raw          type   spoken         rule                     conf
-----------  -----  -------------  -----------------------  ----
Call         WORD   Call           identity                 1.00
911          PHONE  nine one one   verb_call_before_number  0.94
immediately  WORD   immediately    identity                 1.00
```

## Runtime Configuration

Use `NormalizeConfig` or convenience keyword flags to disable optional semantic
normalizers at runtime.

```python
from utterwise import NormalizeConfig, normalize

normalize("x^2", enable_math=False)

config = NormalizeConfig(enable_currency=False, enable_dates=False)
normalize("$12.50 on 03/04/2026", config=config)
```

## CLI

```powershell
utterwise "Call 911 immediately"
utterwise --ssml "hello@example.com"
utterwise --explain "Flight 911 departs at 6"
utterwise --pretty 'Python 3.12 costs $12.50'
```

## Limitations

- Utterwise is deterministic and rule-based; confidence scores are rule
  confidence, not statistical probabilities.
- Date parsing uses day/month/year for slash dates.
- SSML output is currently minimal.
- Chemistry normalization, rich policy-specific SSML, and locale-aware date
  formatting are planned for later.

## Development

Run tests with:

```powershell
.venv\Scripts\uv.exe run --extra dev pytest
.venv\Scripts\python.exe -m pytest
```

Run the interactive development menu:

```powershell
.venv\Scripts\python.exe tests\menu.py
```
