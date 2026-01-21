---
name: summarization_skill
description: Text summarization using sumy library.
allowed-tools:
  - summarize_text
---

# Summarization Skill

This skill enables the agent to generate summaries of long texts using extractive summarization algorithms.

## Prerequisites

- `sumy` library (install via `pip install sumy`)
- `nltk` data (punkt tokenizer) – will be downloaded automatically if missing.

## Tools

### summarize_text
Summarize a text using the LSA (Latent Semantic Analysis) algorithm.

- `text`: The text to summarize.
- `sentence_count`: Number of sentences in the summary (default 3).
- `language`: Language code for tokenization (e.g., 'english', 'chinese'). Default 'english'.

Returns the summary as a single string.

## Notes

- Extractive summarization selects important sentences from the original text.
- Works best with longer, well‑structured texts (articles, reports).
- Supports multiple languages via NLTK tokenizers.
