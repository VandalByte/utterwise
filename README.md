# Utterwise 🗣️

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/utterwise)](https://pypi.org/project/utterwise/)
[![License](https://img.shields.io/github/license/VandalByte/utterwise)](https://github.com/VandalByte/utterwise/blob/main/LICENSE)
[![Package Status](https://img.shields.io/badge/status-alpha-orange)](https://github.com/VandalByte/utterwise)
[![Dependencies](https://img.shields.io/badge/dependencies-lightweight-brightgreen)](https://github.com/VandalByte/utterwise)

Utterwise is a lightweight, deterministic semantic text normalizer for Python
voice assistants, TTS apps, tutoring tools, and small voice-agent pipelines.

It exists because compact TTS models often read useful assistant text badly:
dates, money, temperatures, URLs, versions, equations, and ambiguous numbers can
sound awkward unless the text is normalized before it reaches the speech model.

```python
from utterwise import normalize

normalize("Call 911 if it reaches 25°C on 03/04/2026.")
# "Call nine one one if it reaches twenty five degrees Celsius on third of April twenty twenty six"
```

<a id="contents"></a>

## 📚 Contents

- [📦 Install](#install)
- [✨ Why Use Utterwise?](#why-use-utterwise)
- [🤔 Why Not Regex?](#why-not-regex)
- [✅ Supported Features](#supported-features)
- [📖 Usage and Examples](https://github.com/VandalByte/utterwise/blob/main/USAGE.md)
- [🖥️ CLI](#cli)
- [⚠️ Limitations](#limitations)
- [🛠️ Development](#development)

<a id="install"></a>

## 📦 Install

```powershell
pip install utterwise
```

Math and LaTeX parser support is optional:

```powershell
pip install "utterwise[math]"
```

For local development (with [uv](https://docs.astral.sh/uv/)):

```powershell
uv sync --all-extras
```

<a id="why-use-utterwise"></a>

## ✨ Why Use Utterwise?

- **Deterministic by design** → _The same input produces the same output every time._
- **Lightweight by default** → _No heavy NLP dependency is required for the core path._
- **Fast detection gate** → _Processors only run when the text needs them._
- **Semantic before speech** → _Tokens are classified before they are verbalized._
- **Context-aware ambiguity handling** → _`911` can be emergency, flight number, or cardinal._
- **Explainable output** → _Every token can report its rule, confidence, candidates, and span._
- **Practical for voice assistants** → _Covers dates, currency, temperature, URLs, email, math, and more._

<a id="why-not-regex"></a>

## 🤔 Why Not Regex?

Regex is useful for finding patterns, but speech normalization also needs meaning.
The same characters can have different spoken forms depending on context:

```text
Call 911 immediately      -> nine one one
Flight 911 departs at 6   -> nine eleven
911 divided by 3 is 303   -> nine hundred eleven
```

Utterwise keeps scored candidates, checks nearby words, resolves ambiguity, and
then verbalizes the winning interpretation. That is the core difference between
a cleanup script and a speech-focused normalizer.

<a id="supported-features"></a>

## ✅ Supported Features

| Feature                     | Status               | Example                                   |
| --------------------------- | -------------------- | ----------------------------------------- |
| Numbers and large cardinals | Supported            | `42`, `9999999`                           |
| Decimals and leading zeroes | Supported            | `3.145`, `007`                            |
| Years and ambiguity         | Supported            | `1998`, `911`                             |
| URLs and emails             | Supported            | `openai.com`, `hello@example.com`         |
| Versions                    | Supported            | `Python 3.12`, `v0.1.0`                   |
| Phones and flight numbers   | Supported            | `+1-800-555-0100`, `Flight 911`           |
| Acronyms                    | Supported            | `NASA`, `HTTP`                            |
| Percentages                 | Supported            | `12.5%`                                   |
| Temperatures                | Supported            | `25°C`, `98.6°F`                          |
| Currency                    | Supported            | `$12.50`, `€45`, `£9.99`                  |
| Dates                       | Supported            | `Jan 3, 2026`, `2026-04-03`, `03/04/2026` |
| Math and LaTeX              | Supported (Optional) | `x^2`, `\sqrt{x+1}`                       |
| SSML                        | Minimal              | `<speak>...</speak>`                      |

See [USAGE.md](https://github.com/VandalByte/utterwise/blob/main/USAGE.md)
for API examples, runtime configuration, and CLI output.

<a id="cli"></a>

## 🖥️ CLI

```powershell
utterwise "Call 911 immediately"
utterwise --ssml "hello@example.com"
utterwise --pretty "Python 3.12 costs $12.50"
```

<a id="limitations"></a>

## ⚠️ Limitations

- Utterwise is rule-based; confidence scores are rule confidence, not statistical probabilities.
- Slash dates default to day/month/year unless configured as month/day/year.
- SSML output is currently intentionally minimal.
- Policy names are accepted, but style-specific policy output is not implemented yet.
- Locale-specific speech styles, rich SSML policies, and chemistry normalization are planned later.

<a id="development"></a>

## 🛠️ Development

Run tests:

```powershell
uv run --extra dev pytest
.venv\Scripts\python.exe -m pytest
```

Run the interactive development menu:

```powershell
.venv\Scripts\python.exe tests\menu.py
```
