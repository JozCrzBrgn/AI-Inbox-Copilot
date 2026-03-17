import requests

from ..core.config import get_settings

cnf = get_settings()

def send_slack_alert(result: str) -> bool:
    """
    Send an alert to Slack using a webhook
    """
    webhook_url = cnf.slack.slack_webhook_url

    if not webhook_url:
        print("Slack webhook URL not configured")
        return False
    
    slack_message = f"""
    🚨 *High Priority Customer Email*
    *Customer:* {result['customer_name']}
    *Intent:* {result['intent']}
    *Sentiment:* {result['sentiment']}

    *Summary:*
    {result['summary']}

    *Suggested reply:*
    {result['suggested_reply']}
    """
    
    try:
        payload = {
            "text": slack_message,
            "username": "AI Inbox Copilot",
            "icon_emoji": ":robot_face:"
        }
        
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        return True
    
    except Exception as e:
        print(f"Error sending Slack alert: {e}")
        return False