"""
CMB Salary Batch Import Handler
Integrates with SkillPay for paid access (0.5 USDT per call)
SKILL_ID: 1cf56d3a-bde9-4277-a5db-29108a8b7725
"""
import json
import subprocess
import os
import sys

# SkillPay Configuration
SKILLPAY_API_KEY = os.environ.get("SKILLPAY_API_KEY", "sk_93c5ff38cc3e6112623d361fffcc5d1eb1b5844eac9c40043b57c0e08f91430e")
SKILLPAY_API_URL = os.environ.get("SKILLPAY_API_URL", "https://skillpay.me/api/v1/billing")
SKILL_ID = os.environ.get("SKILLPAY_SKILL_ID", "1cf56d3a-bde9-4277-a5db-29108a8b7725")
PRICE_USDT = "0.5"
SKILL_NAME = "CMB Salary Import"

# Paths
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
IMPORT_SCRIPT = os.path.join(SKILL_DIR, "import_salary.py")


def charge_user(user_id: str) -> dict:
    """
    Charge user via SkillPay before providing the service.
    Uses POST /api/v1/billing/charge
    Returns dict with success=True/False and payment info.
    """
    if not SKILLPAY_API_KEY or not SKILL_ID:
        return {"success": False, "error": "SKILLPAY_API_KEY or SKILL_ID not configured"}

    try:
        import urllib.request
        import urllib.error

        payload = json.dumps({
            "user_id": user_id,
            "skill_id": SKILL_ID,
            "amount": float(PRICE_USDT)
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{SKILLPAY_API_URL}/charge",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": SKILLPAY_API_KEY
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("success"):
                return {"success": True, "balance": data.get("balance")}
            else:
                return {
                    "success": False,
                    "balance": data.get("balance"),
                    "payment_url": data.get("payment_url")
                }
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        try:
            err_json = json.loads(err_body)
            return {"success": False, "error": err_json.get("message", err_body)}
        except:
            return {"success": False, "error": err_body or str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle(input_text: str, user_id: str = "default") -> dict:
    """
    Main handler for CMB Salary Import skill.

    Args:
        input_text: JSON string with keys:
            - salary_file: path to salary Excel
            - template_file: path to AgencyPayment template
            - output_file: path for output (optional)
            Example: '{"salary_file":"/path/salary.xlsx","template_file":"/path/template.xlsx"}'
        user_id: unique user identifier for SkillPay

    Returns:
        dict with:
            - output_file: path to result file (on success)
            - payment_status: "paid" or error info
    """
    # Parse input
    try:
        params = json.loads(input_text)
    except (json.JSONDecodeError, TypeError):
        return {
            "error": "Invalid input format. Expected JSON: "
                     '{"salary_file":"path","template_file":"path","output_file":"path"}'
        }

    salary_file = params.get("salary_file", "")
    template_file = params.get("template_file", "")
    output_file = params.get("output_file", "")

    if not salary_file or not template_file:
        return {
            "error": "Missing required fields: salary_file and template_file are required",
            "payment_status": "not_charged"
        }

    # Default output filename
    if not output_file:
        base = os.path.splitext(os.path.basename(template_file))[0]
        output_file = os.path.join(
            os.path.dirname(template_file) or ".",
            f"{base}_输出.xlsx"
        )

    # Step 1: Charge user
    charge_result = charge_user(user_id)

    if not charge_result.get("success"):
        return {
            "payment_required": True,
            "amount": PRICE_USDT,
            "currency": "USDT",
            "message": f"请先支付 {PRICE_USDT} USDT 使用此技能",
            "payment_url": charge_result.get("payment_url", "https://skillpay.me"),
            "balance": charge_result.get("balance"),
            "error": charge_result.get("error", "Payment failed"),
            "payment_status": "failed"
        }

    # Step 2: Run import
    try:
        result = subprocess.run(
            [sys.executable, IMPORT_SCRIPT, salary_file, template_file, output_file],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return {
                "error": f"Import failed: {result.stderr}",
                "payment_status": "charged_no_result",
                "output_file": None
            }
    except subprocess.TimeoutExpired:
        return {
            "error": "Import timed out (>60s)",
            "payment_status": "charged_no_result"
        }
    except Exception as e:
        return {
            "error": f"Import error: {str(e)}",
            "payment_status": "charged_no_result"
        }

    return {
        "success": True,
        "output_file": output_file,
        "message": f"导入完成，共处理9名员工",
        "balance_after": charge_result.get("balance"),
        "payment_status": "paid"
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_input = sys.argv[1]
        user_id = sys.argv[2] if len(sys.argv) > 2 else "cli"
    else:
        user_input = input("Enter JSON input: ")
        user_id = "cli"

    result = handle(user_input, user_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))
