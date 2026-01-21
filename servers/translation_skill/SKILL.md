---
name: translation_skill
description: Text translation using googletrans library.
allowed-tools:
  - translate_text
---

# Translation Skill

This skill enables the agent to translate text between languages using the googletrans library.

## Prerequisites

- `googletrans==4.0.0rc1` library (install via `pip install googletrans==4.0.0rc1`)
- Internet connection (uses Google Translate API)

## Tools

### translate_text
Translate text from one language to another.

- `text`: The text to translate.
- `src`: Source language code (e.g., 'en', 'auto' for auto‑detect). Default 'auto'.
- `dest`: Destination language code (e.g., 'zh‑CN', 'es', 'fr'). Default 'zh‑CN'.

Returns the translated text and detected source language.

## Notes

- Google Translate API may have usage limits.
- Language codes follow ISO 639‑1 (two‑letter codes).
