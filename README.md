# CodeGuardian AI

Paste any code, pick your level, get a real explanation — not just "here's what to submit."

## What it does

- 📖 Line-by-line explanation, tuned to your level (total beginner → interview prep)
- ⏱️ Time/space complexity with plain-English reasoning
- 🐛 Bug/issue detection with suggested fixes
- 💡 Improvement suggestions
- 🎯 Interview questions this code could plausibly trigger
- 🔀 An auto-generated flowchart of the code's control flow

## How it works

This one genuinely needs an AI model to understand arbitrary code (unlike a
rules-based checker), so it calls **Google's Gemini API** on the backend.
Gemini has a free tier, so this costs nothing to run for personal/demo use.

## 1. Get a free API key

1. Go to **https://aistudio.google.com/app/apikey**
2. Sign in with any Google account
3. Click **Create API Key**
4. Copy it

## 2. Run it locally

```bash
git clone https://github.com/<your-username>/codeguardian-ai.git
cd codeguardian-ai
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and paste your key:
```
GEMINI_API_KEY=your_actual_key_here
```

Then:
```bash
python app.py
```

Open **http://127.0.0.1:5000**.

## 3. Deploy (Render, free)

1. Push this repo to GitHub (keep `.env` out of it — `.gitignore` already excludes it)
2. On [render.com](https://render.com) → **New Web Service** → connect this repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app`
5. Under **Environment**, add a variable: `GEMINI_API_KEY` = your key
6. Deploy

Your API key never goes in the code or the repo — only in Render's environment
variables panel. That's what keeps it private even though the repo is public.

## Project structure

```
codeguardian-ai/
├── app.py           # Flask routes, calls Gemini, parses response
├── prompts.py        # The "explain at my level" prompt logic
├── templates/index.html
├── static/style.css
├── static/app.js
├── requirements.txt
├── .env.example
└── .gitignore
```

## Notes

- The AI is instructed to return strict JSON; `app.py` defensively strips
  markdown fences in case the model wraps its answer anyway.
- Free-tier Gemini has rate limits — fine for demos/interviews, not for
  heavy production traffic.
