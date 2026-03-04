# 🤖 AI News WhatsApp Bot

Gets the top AI news from 8 sources every day, summarises them with Claude, and sends them straight to your WhatsApp.

**Totally free to run** (GitHub Actions free tier is more than enough for one daily job).

---

## What you'll get on WhatsApp

```
🤖 Daily AI Digest — 04 Mar 2026

1. Google Releases Gemini 2.0 Ultra
   Source: VentureBeat AI
   Google just dropped their most capable model yet, claiming 
   state-of-the-art on coding and multimodal tasks. Relevant 
   for engineers evaluating model APIs for production use.
   🔗 https://...

2. ...

━━━━━━━━━━━━━━━━━━━
💡 Today's Trend: The agent + tool-use wave is accelerating — 
   every major lab shipped something in that space this week.
```

---

## Setup (15–20 minutes)

### Step 1 — Get a Twilio account (free)

1. Sign up at [twilio.com](https://www.twilio.com) — free trial gives you $15 credit, more than enough
2. Go to **Messaging → Try it out → Send a WhatsApp message**
3. Follow the sandbox setup: you'll send a join code to `+1 415 523 8886` on WhatsApp
4. Note down:
   - **Account SID** (from Console dashboard)
   - **Auth Token** (from Console dashboard)
   - **From number**: `+14155238886` (Twilio sandbox number)

> 💡 For a permanent number (not sandbox), upgrade to a paid Twilio account and provision a WhatsApp-enabled number (~$1/month). But the sandbox is fine for personal use.

---

### Step 2 — Get your Anthropic API key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an API key under **API Keys**
3. The bot uses `claude-sonnet-4` — costs roughly **$0.002–0.005 per run** (essentially free)

---

### Step 3 — Set up the GitHub repo

1. Create a **private** GitHub repo (keep your keys safe)
2. Add these files to the root:
   - `ai_news_whatsapp.py`
   - `requirements.txt`
   - `.github/workflows/daily_digest.yml`

3. Add your secrets in GitHub → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret Name            | Value                          |
|------------------------|--------------------------------|
| `ANTHROPIC_API_KEY`    | Your Anthropic API key         |
| `TWILIO_ACCOUNT_SID`   | From Twilio console            |
| `TWILIO_AUTH_TOKEN`    | From Twilio console            |
| `TWILIO_WHATSAPP_FROM` | `+14155238886` (sandbox)       |
| `MY_WHATSAPP_NUMBER`   | Your number e.g. `+919876543210` |

---

### Step 4 — Test it manually

In GitHub → **Actions → Daily AI News WhatsApp Digest → Run workflow**

You should get a WhatsApp message within ~30 seconds.

---

## Customisation

### Change delivery time
Edit the cron in `.github/workflows/daily_digest.yml`:
```yaml
- cron: "30 2 * * *"   # 8:00 AM IST
- cron: "0 1 * * *"    # 6:30 AM IST  
- cron: "30 3 * * *"   # 9:00 AM IST
```
Use [crontab.guru](https://crontab.guru) to build your preferred schedule.

### Add or remove news sources
Edit the `RSS_FEEDS` list in `ai_news_whatsapp.py`:
```python
RSS_FEEDS = [
    ("OpenAI Blog", "https://openai.com/blog/rss.xml"),
    # add more here...
]
```

**More good RSS feeds:**
- OpenAI blog: `https://openai.com/blog/rss.xml`
- Anthropic news: `https://www.anthropic.com/news/rss`
- Arxiv CS.AI: `https://rss.arxiv.org/rss/cs.AI`
- Import AI newsletter: check Jack Clark's substack for RSS link
- Hacker News AI: `https://hnrss.org/newest?q=AI+LLM&points=50`

### Change the number of stories
```python
TOP_N_STORIES = 6   # change to 3 for a shorter digest, 10 for more
```

### Run locally
```bash
pip install -r requirements.txt

export ANTHROPIC_API_KEY="sk-..."
export TWILIO_ACCOUNT_SID="AC..."
export TWILIO_AUTH_TOKEN="..."
export TWILIO_WHATSAPP_FROM="+14155238886"
export MY_WHATSAPP_NUMBER="+919876543210"

python ai_news_whatsapp.py
```

---

## Architecture

```
GitHub Actions (cron: 8am daily)
        │
        ▼
  fetch_recent_articles()
  ┌─ TechCrunch AI ─────────┐
  ├─ VentureBeat AI ────────┤  feedparser (RSS)
  ├─ The Verge AI ──────────┤  → last 24h articles
  ├─ Hugging Face Blog ─────┤
  └─ + 4 more sources ──────┘
        │
        ▼
  summarise_with_claude()
  └─ Claude Sonnet 4 → picks top 6, formats digest
        │
        ▼
  send_whatsapp()
  └─ Twilio API → your WhatsApp 📱
```

---

## Cost estimate

| Service       | Usage             | Cost/month   |
|---------------|-------------------|--------------|
| GitHub Actions| ~30 runs/month    | **Free**     |
| Anthropic API | ~30 calls/month   | ~**$0.15**   |
| Twilio        | ~30 messages/month| ~**$0.00*** |

*Twilio sandbox is free. Paid number is ~$1/mo + $0.005/msg.

**Total: essentially free.**
