# Goods Trading Crawler

Crawls Reddit & X search results via Playwright, validates selling posts using Gemini LLM, and saves them to JSONL.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
playwright install chromium
cp env.example .env  # Set GEMINI_API_KEY
```

## Usage

```bash
python main.py --keyword "아이유 포카 양도"
```
