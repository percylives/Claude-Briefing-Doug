#!/usr/bin/env python3
"""
Daily briefing generator + sender.

Generates freshly web-search-informed briefings using the Anthropic API
and emails them via Gmail SMTP.

Topics run daily: Housing / Property / Homelessness, Tusla / Child Protection.
YMCA topic is stubbed here but not active — it lives in a separate Claude
project and can be turned on later by uncommenting it in TOPICS and adding
a Thursday-only schedule check.

Required environment variables (set as GitHub Actions secrets):
  ANTHROPIC_API_KEY
  GMAIL_ADDRESS
  GMAIL_APP_PASSWORD
  RECIPIENT_EMAIL
"""

import os
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic

MODEL = "claude-sonnet-5"

TOPICS = {
    "housing": {
        "label": "Housing, Property & Homelessness Briefing",
        "prompt": (
            "You are compiling a daily briefing on Irish housing, property, and "
            "homelessness news for {date}. Search the web for the most recent, "
            "credible news coverage (Irish Times, RTE, Irish Examiner, TheJournal.ie, "
            "government and NGO sources such as Focus Ireland, Simon Communities, "
            "the LDA, CSO, RTB) from the last 24-48 hours. Write a structured "
            "briefing in Markdown with a clear top story, any new threads, ongoing "
            "threads with no material change noted as such, and a short "
            "commentary-tone section. Include inline source links. Be concise and "
            "factual, and do not repeat old news as if it were new."
        ),
    },
    "tusla": {
        "label": "Tusla & Child Protection Briefing",
        "prompt": (
            "You are compiling a daily briefing on Tusla (Ireland's Child and "
            "Family Agency) and child protection news for {date}. Search the web "
            "for the most recent, credible news coverage (Irish Times, RTE, Irish "
            "Examiner, TheJournal.ie, HIQA, Ombudsman for Children, Oireachtas) "
            "from the last 24-48 hours. Write a structured briefing in Markdown "
            "with a clear top story, any new threads, ongoing threads with no "
            "material change noted as such, and a short commentary-tone section. "
            "Include inline source links. Be concise and factual, and do not "
            "repeat old news as if it were new."
        ),
    },
    # "ymca": {
    #     "label": "YMCA Dublin & Childcare/Youth Work Briefing",
    #     "prompt": (
    #         "You are compiling a weekly briefing on YMCA Dublin and the wider "
    #         "Irish childcare/youth work sector for {date}. Search the web for "
    #         "recent coverage of YMCA Dublin specifically plus childcare "
    #         "capacity, affordability, workforce, and youth work news. Write a "
    #         "structured Markdown briefing with sources."
    #     ),
    # },
}


def today_str() -> str:
    return datetime.now(timezone.utc).strftime("%d %B %Y")


def generate_briefing(client: anthropic.Anthropic, topic_key: str) -> str:
    topic = TOPICS[topic_key]
    prompt = topic["prompt"].format(date=today_str())

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )

    # Web search responses interleave text blocks with tool_use/tool_result
    # blocks. Only text blocks contain the briefing content we want.
    text_parts = [block.text for block in response.content if block.type == "text"]
    return "\n".join(text_parts).strip()


def send_email(subject: str, body: str) -> None:
    gmail_address = os.environ["GMAIL_ADDRESS"].strip()
    gmail_app_password = os.environ["GMAIL_APP_PASSWORD"].strip()
    recipient = os.environ["RECIPIENT_EMAIL"].strip()

    if not gmail_address or not gmail_app_password or not recipient:
        raise ValueError(
            "One or more required secrets (GMAIL_ADDRESS, GMAIL_APP_PASSWORD, "
            "RECIPIENT_EMAIL) is empty after stripping whitespace. Check the "
            "repository secrets for blank values or stray newlines."
        )

    msg = MIMEMultipart()
    msg["From"] = gmail_address
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_app_password)
        server.sendmail(gmail_address, [recipient], msg.as_string())


def main() -> int:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY is not set", file=sys.stderr)
        return 1

    client = anthropic.Anthropic(api_key=api_key)
    date_label = today_str()

    exit_code = 0
    for topic_key, topic in TOPICS.items():
        try:
            print(f"Generating briefing: {topic_key}")
            briefing = generate_briefing(client, topic_key)
            if not briefing:
                raise ValueError("Empty briefing content returned")

            subject = f"{topic['label']} — {date_label}"
            send_email(subject, briefing)
            print(f"Sent: {subject}")
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR generating/sending '{topic_key}': {exc}", file=sys.stderr)
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
