"""
AI News WhatsApp Bot
--------------------
Fetches top AI news from RSS feeds, summarizes with Claude,
and sends a daily digest to your WhatsApp via Twilio.

Setup: See README.md
"""

import os
import feedparser
import anthropic
from twilio.rest import Client
from datetime import datetime, timedelta


# ─── CONFIG ───────────────────────────────────────────────────────────────────

# Top AI news RSS feeds (no API key needed)
RSS_FEEDS = [
    ("TechCrunch AI",    "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("VentureBeat AI",   "https://venturebeat.com/category/ai/feed/"),
    ("The Verge AI",     "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("MIT Tech Review",  "https://www.technologyreview.com/feed/"),
    ("Hugging Face",     "https://huggingface.co/blog/feed.xml"),
    ("AI News",          "https://www.artificialintelligence-news.com/feed/"),
    ("Wired AI",         "https://www.wired.com/feed/tag/artificial-intelligence/latest/rss"),
    ("DeepMind Blog",    "https://deepmind.google/blog/rss.xml"),
]

HOURS_LOOKBACK = 24   # fetch news from last N hours
MAX_PER_FEED   = 5    # max articles to pull per feed
TOP_N_STORIES  = 3    # how many stories to include in digest


# ─── FETCH ────────────────────────────────────────────────────────────────────

def fetch_recent_articles(hours: int = HOURS_LOOKBACK) -> list[dict]:
    """Pull recent articles from all RSS feeds."""
    articles = []
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    for source_name, feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:MAX_PER_FEED]:
                # Filter by date if available
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_dt = datetime(*entry.published_parsed[:6])
                    if pub_dt < cutoff:
                        continue

                articles.append({
                    "title":   entry.get("title", "Untitled").strip(),
                    "summary": entry.get("summary", "")[:600].strip(),
                    "link":    entry.get("link", ""),
                    "source":  source_name,
                })
        except Exception as e:
            print(f"  ⚠️  Could not fetch {source_name}: {e}")

    print(f"  ✅ Fetched {len(articles)} articles from {len(RSS_FEEDS)} feeds")
    return articles


# ─── SUMMARISE ────────────────────────────────────────────────────────────────

def summarise_with_claude(articles: list[dict]) -> str:
    """Use Claude to pick and summarise the top stories."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    articles_text = "\n\n".join([
        f"[{i+1}] {a['source']} — {a['title']}\n{a['summary']}\n🔗 {a['link']}"
        for i, a in enumerate(articles)
    ])

    prompt = f"""You are an AI news curator for a senior software engineer.

From the articles below, pick the {TOP_N_STORIES} most impactful AI stories from the past 24 hours.

Format EXACTLY like this (keep it very short — headlines only):

🤖 *Daily AI Digest — {datetime.now().strftime("%d %b %Y")}*

1️⃣ *[Headline]* — [One line, max 15 words] 🔗 [link]
2️⃣ *[Headline]* — [One line, max 15 words] 🔗 [link]
3️⃣ *[Headline]* — [One line, max 15 words] 🔗 [link]
4️⃣ *[Headline]* — [One line, max 15 words] 🔗 [link]
5️⃣ *[Headline]* — [One line, max 15 words] 🔗 [link]
6️⃣ *[Headline]* — [One line, max 15 words] 🔗 [link]

💡 *Trend:* [One sentence on today's theme]

Total response MUST be under 1000 characters.

ARTICLES:
{articles_text}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


# ─── SEND ─────────────────────────────────────────────────────────────────────

def send_whatsapp(message: str, to_number: str) -> str:
    """Send message via Twilio WhatsApp sandbox."""
    twilio_client = Client(
        os.environ["TWILIO_ACCOUNT_SID"],
        os.environ["TWILIO_AUTH_TOKEN"]
    )

    msg = twilio_client.messages.create(
        from_=f"whatsapp:{os.environ['TWILIO_WHATSAPP_FROM']}",  # e.g. +14155238886
        to=f"whatsapp:{to_number}",                               # e.g. +919876543210
        body=message
    )

    return msg.sid


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("\n🚀 AI News WhatsApp Bot starting...\n")

    # 1. Fetch
    print("📡 Fetching news from RSS feeds...")
    articles = fetch_recent_articles()

    if not articles:
        print("❌ No recent articles found. Exiting.")
        return

    # 2. Summarise
    print(f"\n🧠 Asking Claude to pick top {TOP_N_STORIES} stories...")
    digest = summarise_with_claude(articles)
    print("\n--- DIGEST PREVIEW ---")
    print(digest)
    print("----------------------\n")

    # 3. Send
    to_number = os.environ.get("MY_WHATSAPP_NUMBER")
    if not to_number:
        print("⚠️  MY_WHATSAPP_NUMBER not set. Skipping WhatsApp send.")
        return

    print(f"📲 Sending to WhatsApp {to_number}...")
    sid = send_whatsapp(digest, to_number)
    print(f"✅ Message sent! Twilio SID: {sid}\n")


if __name__ == "__main__":
    main()
