import argparse
import requests
import json
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Trigger the Eonik Budget Leak Agent audit")
    parser.add_argument("--account_id", required=True, help="Meta Ad Account ID (e.g., act_12345)")
    parser.add_argument("--days", type=int, default=7, help="Days to evaluate (default: 7)")
    parser.add_argument("--send_slack", action="store_true", help="Send formatted output to Slack webhook")
    args = parser.parse_args()

    token = os.environ.get("EONIK_AUTH_TOKEN")
    if not token:
        print(json.dumps({
            "status": "error",
            "message": "EONIK_AUTH_TOKEN environment variable is not set."
        }, indent=2), file=sys.stderr)
        sys.exit(1)
        
    # Security: Drop the ephemeral token from the execution environment securely.
    del os.environ["EONIK_AUTH_TOKEN"]

    # The Endpoint Requirements
    endpoint = "https://api.eonik.ai/api/budget-agent/run-audit"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    params = {
        "account_id": args.account_id,
        "days": args.days,
        "send_slack": args.send_slack
    }

    try:
        response = requests.post(endpoint, headers=headers, params=params)
        response.raise_for_status()
        
        report = response.json()
        
        # Simplified stdout for the LLM to easily parse
        print(json.dumps({
            "status": "success",
            "flagged_ads_count": report.get("flagged_ads_count", 0),
            "total_leaked_spend": report.get("total_leaked_spend", 0.0),
            "pause_recommendations": report.get("pause_recommendations", []),
            "scale_recommendations": report.get("scale_recommendations", []),
            "monitor_recommendations": report.get("monitor_recommendations", []),
            "slack_dispatched": args.send_slack
        }, indent=2))
        
    except requests.exceptions.HTTPError as http_err:
        print(json.dumps({
            "status": "error",
            "message": f"HTTP error occurred: {http_err}",
            "response_text": response.text if response else "No response body"
        }, indent=2), file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(json.dumps({
            "status": "error",
            "message": f"An unexpected error occurred: {err}"
        }, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
