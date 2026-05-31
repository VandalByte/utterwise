# Utterwise Usage

This page keeps the practical bits close at hand: the public API, runtime
configuration, CLI examples, and a compact tour of what Utterwise can normalize.

## Quick Start

```python
from utterwise import normalize

normalize("Born in 1998 call 911 immediately and visit openai.com")
# "Born in nineteen ninety eight call nine one one immediately and visit open ai dot com"
```

## API Reference by Example

### `normalize(text, output="plain", policy="assistant", explain=False, config=None, **config_overrides)`

Use `normalize` when you want the normal spoken-text output.

```python
from utterwise import normalize

normalize("A & B in 2024")
# "A and B in twenty twenty four"

normalize("Python 3.12 costs $12.50")
# "Python three point twelve costs twelve dollars and fifty cents"

normalize("James bond 007")
# "James bond zero zero seven"
```

You can also request SSML through the same function:

```python
normalize("hello@example.com", output="ssml")
# "<speak>hello at example dot com</speak>"
```

Set `explain=True` when you want structured trace data instead of only the
rendered output:

```python
trace = normalize("Flight 911 departs at 6", explain=True)

trace["output"]
# "Flight nine eleven departs at six"

trace["tokens"][1]["type"]
# "FLIGHT_NO"
```

## Policies

The public API accepts a `policy` argument on `normalize`, `normalize_ssml`,
`explain`, and `explain_pretty`.

```python
normalize("x^2 + y^2 = z^2", policy="assistant")
normalize("x^2 + y^2 = z^2", policy="edu")
normalize("x^2 + y^2 = z^2", policy="accessibility")
```

Available policies today:

| Policy | Current behavior |
| --- | --- |
| `assistant` | Default policy name for voice-assistant style output. |
| `edu` | Accepted and recorded in explain output, but not style-specific yet. |
| `accessibility` | Accepted and recorded in explain output, but not style-specific yet. |

At the moment, policies are validation and pipeline placeholders. They do not
yet change wording, SSML rate, emphasis, spell-out behavior, or pauses.

### `normalize_ssml(text, policy="assistant", config=None, **config_overrides)`

Use `normalize_ssml` when your TTS engine expects a minimal SSML document.

```python
from utterwise import normalize_ssml

normalize_ssml("hello@example.com")
# "<speak>hello at example dot com</speak>"

normalize_ssml("5 < 6 & hello@example.com")
# "<speak>five &lt; six and hello at example dot com</speak>"
```

### `explain(text, policy="assistant", config=None, **config_overrides)`

Use `explain` when you want to inspect how Utterwise classified each token.

```python
from utterwise import explain

trace = explain("I have 42 apples")

trace["output"]
# "I have forty two apples"

trace["tokens"][2]
# {
#   "value": "42",
#   "type": "CARDINAL",
#   "spoken": "forty two",
#   "rule": "number_default",
#   "confidence": 0.76,
#   ...
# }
```

Explain output includes detection flags, token spans, confidence, candidates,
winner, rule chain, signals, and metadata where relevant.

### `explain_pretty(text, policy="assistant", config=None, **config_overrides)`

Use `explain_pretty` when you want a readable table for debugging or demos.

```python
from utterwise import explain_pretty

print(explain_pretty("Call 911 immediately"))
```

```text
raw          type   spoken         rule                     conf
-----------  -----  -------------  -----------------------  ----
Call         WORD   Call           identity                 1.00
911          PHONE  nine one one   verb_call_before_number  0.94
immediately  WORD   immediately    identity                 1.00
```

### `NormalizeConfig`

Use `NormalizeConfig` when you want to disable a normalizer or control slash-date
interpretation at runtime.

```python
from utterwise import NormalizeConfig, normalize

config = NormalizeConfig(
    enable_math=False,
    enable_currency=True,
    enable_dates=True,
    enable_temperature=True,
    date_format="DMY",
)

normalize("x^2 costs $5 on 03/04/2026", config=config)
# "x ^ two costs five dollars on third of April twenty twenty six"
```

You can also pass convenience overrides directly:

```python
normalize("$12.50 on 03/04/2026", enable_currency=False)
# "twelve dollars and fifty cents on third of April twenty twenty six"

normalize("04/03/2026", date_format="MDY")
# "third of April twenty twenty six"
```

Available config fields:

| Field | Default | Meaning |
| --- | --- | --- |
| `enable_math` | `True` | Normalize math and LaTeX fragments. |
| `enable_currency` | `True` | Normalize `$`, `€`, and `£` amounts. |
| `enable_dates` | `True` | Normalize ISO, slash, and month-name dates. |
| `enable_temperature` | `True` | Normalize Celsius and Fahrenheit values. |
| `date_format` | `"DMY"` | Interpret slash dates as `"DMY"` or `"MDY"`. |

## CLI

The CLI is intentionally small and good for quick checks.

```powershell
utterwise "Call 911 immediately"
# Call nine one one immediately

utterwise --ssml "hello@example.com"
# <speak>hello at example dot com</speak>

utterwise --pretty "Python 3.12 costs $12.50"
```

Useful flags:

```powershell
utterwise --explain "Flight 911 departs at 6"
utterwise --no-math "x^2"
utterwise --no-currency "$12.50"
utterwise --no-dates "03/04/2026"
utterwise --no-temperature "25°C"
```

## Before and After

| Input | Output |
| --- | --- |
| `Born in 1998` | `Born in nineteen ninety eight` |
| `The value is 1998` | `The value is one thousand nine hundred ninety eight` |
| `Call 911 immediately` | `Call nine one one immediately` |
| `Flight 911 departs at 6` | `Flight nine eleven departs at six` |
| `911 divided by 3 is 303` | `nine hundred eleven divided by three is three hundred three` |
| `Python 3.12` | `Python three point twelve` |
| `v0.1.0` | `v zero point one point zero` |
| `3.145` | `three point one four five` |
| `James bond 007` | `James bond zero zero seven` |
| `25°C` | `twenty five degrees Celsius` |
| `98.6°F` | `ninety eight point six degrees Fahrenheit` |
| `$12.50` | `twelve dollars and fifty cents` |
| `€45` | `forty five euros` |
| `Jan 3, 2026` | `January third twenty twenty six` |
| `03/04/2026` | `third of April twenty twenty six` |
| `hello@example.com` | `hello at example dot com` |
| `google.com` | `google dot com` |
| `https://openai.com` | `open ai dot com` |
| `NASA and HTTP` | `nasa and H T T P` |
| `12.5%` | `twelve point five percent` |

## Math and LaTeX

Math support is optional. Install it with:

```powershell
pip install "utterwise[math]"
```

Fast deterministic rules still handle common fragments:

| Input | Output |
| --- | --- |
| `x^2` | `x squared` |
| `a/b` | `a over b` |
| `(x+1)^2` | `open parenthesis x plus one close parenthesis squared` |
| `E = mc^2` | `E equals m c squared` |
| `x_1, x_2, \ldots` | `x sub one, x sub two, and so on` |
| `\frac{a+b}{c}` | `a plus b over c` |
| `\sqrt{x+1}` | `square root of x plus one` |
| `\sum_{i=1}^{n} i` | `sum from i equals one to n of i` |

## Test String

Here is one compact sample that touches most of the current normalizers:

```python
sample = (
    "Born in 1998, call 911 immediately, Flight 911 departs at 6, "
    "Python 3.12 supports x^2, a/b, (x+1)^2, \\frac{a+b}{c}, "
    "E = mc^4, \\sqrt{x+1}, \\sum_{i=1}^{n} i, and x_1, x_2, \\ldots; "
    "email hello@example.com, visit https://openai.com, pay $12.50, "
    "and expect 25°C on 03/04/2026."
)

print(normalize(sample))
```
