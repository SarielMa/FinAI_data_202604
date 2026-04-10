# 📦 FreeBSD CVS Archive (C/C++)

## Dataset Summary

**FreeBSD CVS Archive (C/C++)** is a large-scale dataset of source code extracted from the historical FreeBSD CVS repository. The dataset focuses on **C and C++ source files**, providing structured samples suitable for code modeling, analysis, and benchmarking.

Each sample includes:
- the dataset source
- commit year
- extracted code content
- token count (computed using GPT tokenizer)

This dataset is designed for:
- code language modeling
- software evolution analysis
- code understanding and generation
- benchmarking LLMs on real-world system code

---

## Dataset Structure

Each record follows a simple JSONL format:

```jsonl
{
  "Source": "freebsd-cvs-archive",
  "Date": 2003,
  "Text": "... C/C++ source code ...",
  "Token_count": 512
}
```

## Fields


Source: Name of the dataset
Date: Year extracted from CVS revision metadata
Text: Raw C/C++ code snippet
Token_count: Number of tokens computed using tiktoken (cl100k_base)

## Source Data

The dataset is derived from:

FreeBSD CVS archive ([historical version control system](https://download.freebsd.org/development/CVS-archive/))

## Processing

Processing Pipeline

The dataset was constructed using the following steps:

Parse CVS revision files
Extract revision metadata (commit date → year)
Extract text blocks (code sections between CVS delimiters)
Filter samples (remove empty or short entries)
Keep only C/C++ code
Compute token counts using tiktoken
Split into fixed-size JSONL shards (~8MB each)

