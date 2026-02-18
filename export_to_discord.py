import requests
import os
import logging

logger = logging.getLogger(__name__)

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def export_to_discord(summary_json):
    if not WEBHOOK_URL:
        logger.warning("DISCORD_WEBHOOK_URL not set. Skipping Discord export.")
        return False

    decisions = "\n".join(
        f"- {d}" for d in summary_json.get("decisions", [])
    )

    action_items = "\n".join(
        f"- {item.get('task')} (Owner/assigned to: {item.get('owner', 'N/A')})"
        for item in summary_json.get("action_items", [])
    )

    formatted = f"""
📝 {summary_json.get('title', 'Meeting')}

**Summary**
{summary_json.get('summary', '')}

**Decisions**
{decisions if decisions else "None"}

**Action Items**
{action_items if action_items else "None"}
"""

    try:
        response = requests.post(WEBHOOK_URL, json={"content": formatted})

        if response.status_code == 204:
            logger.info("Discord export successful.")
            return True
        else:
            logger.error(f"Discord export failed: {response.text}")
            return False

    except Exception as e:
        logger.exception(f"Error exporting to Discord: {e}")
        return False
if __name__ == "__main__":
    test_summary = {
        "title": "Weekly Sync",
        "summary": "Team discussed pipeline progress.",
        "decisions": ["Use webhook MVP"],
        "action_items": [{"task": "Test integration"}]
    }

    export_to_discord(test_summary)

