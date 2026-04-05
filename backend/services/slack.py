import logging

import requests

from ..core.config import get_settings

cnf = get_settings()
logger = logging.getLogger(__name__)


def send_slack_alert(result: str) -> bool:
    """
    Send an alert to Slack using a webhook
    """
    webhook_url = cnf.slack.slack_webhook_url

    if not webhook_url:
        return False

    slack_message = f"""
    🚨 *High Priority Customer Email*
    *Customer:* {result["customer_name"]}
    *Intent:* {result["intent"]}
    *Sentiment:* {result["sentiment"]}

    *Summary:*
    {result["summary"]}

    *Suggested reply:*
    {result["suggested_reply"]}
    """

    try:
        payload = {
            "text": slack_message,
            "username": "AI Inbox Copilot",
            "icon_emoji": ":robot_face:",
        }

        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        return True

    except Exception as e:
        logger.error(f"Error sending Slack alert: {e}")
        return False
