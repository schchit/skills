#!/usr/bin/env python3
"""
Create QA_Unified workflow in n8n
Based on illicocash QA workflow, makes it project-aware for illicocash, vaulsys, and ussd
"""

import os
import json
import requests
import sys

# Configuration
N8N_URL = os.getenv('N8N_URL', 'https://n8n.nelflow.cloud')
N8N_API_KEY = os.getenv('N8N_API_TOKEN')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'nel@illicocash.com')

# illicocash configs
ILINCOCASH_CONFIG = {
    "project": "illicocash",
    "dashboard_id": "19315p5VGdOfEfr_N8L8PoGBxOHLDRIDplPSGP8U8CIc",
    "bug_tracker_id": "1JVW980w6HpOxep8waSUSppYD2FqR9ET7iHIlOeouqME",
    "email": "qa@illicocash.com",
    "folder_id": "1ZISeqV64XxM1XGKt2BlVj2SGn00NVUBZ",
    "telegram_id": "5166959100",
    "telegram_name": "illicocash QA Analyst bot",
    "staff_datatable_id": "5Qdq9VHTMgIPJ5R2",
    "test_cases_datatable_id": "1dJ4AW7jGEUbgZNJsiw8Dc-82mlCSYrCB5H4NLwo9BQo"
}

# vaulsys configs (will be placeholders - update with actual values)
VAULSYS_CONFIG = {
    "project": "vaulsys",
    "dashboard_id": "",  # To be filled
    "bug_tracker_id": "",  # To be filled
    "email": "",  # To be filled
    "folder_id": "",  # To be filled
    "telegram_id": "",  # To be filled
    "telegram_name": "vaulsys QA bot",
    "staff_datatable_id": "",  # To be filled
    "test_cases_datatable_id": ""  # To be filled
}

# ussd configs (will be placeholders - update with actual values)
USSD_CONFIG = {
    "project": "ussd",
    "dashboard_id": "",  # To be filled
    "bug_tracker_id": "",  # To be filled
    "email": "",  # To be filled
    "folder_id": "",  # To be filled
    "telegram_id": "",  # To be filled
    "telegram_name": "ussd QA bot",
    "staff_datatable_id": "",  # To be filled
    "test_cases_datatable_id": ""  # To be filled
}

# Headers
HEADERS = {
    "Content-Type": "application/json",
    "X-N8N-API-KEY": N8N_API_KEY
}

def create_workflow():
    """Create the QA_Unified workflow"""

    workflow = {
        "name": "QA_Unified - Unified QA Workflow",
        "nodes": [
            # Telegram Trigger (project-aware)
            {
                "parameters": {
                    "updates": ["poll", "message"],
                    "additionalFields": {
                        "download": True,
                        "imageSize": "large",
                        "chatIds": "={{ $json.chat_id }}"
                    }
                },
                "type": "n8n-nodes-base.telegramTrigger",
                "typeVersion": 1.2,
                "position": [-800, -224],
                "id": "telegram_trigger",
                "name": "Telegram Trigger",
                "webhookId": "qa_unified_trigger",
                "credentials": {
                    "telegramApi": {
                        "id": "W8ld3O62OKQigPzH",
                        "name": "={{ $json.telegram_name }}"
                    }
                }
            },

            # Set Project Variable
            {
                "parameters": {
                    "assignments": [
                        {
                            "name": "project",
                            "value": "={{ $json.project || 'illicocash' }}"
                        },
                        {
                            "name": "chat_id",
                            "value": "={{ $('Telegram Trigger').item.json.message.chat.id }}"
                        },
                        {
                            "name": "message_text",
                            "value": "={{ $json.message.text }}"
                        }
                    ]
                },
                "type": "n8n-nodes-base.set",
                "typeVersion": 3.4,
                "position": [-480, 0],
                "id": "set_project",
                "name": "Set Project Variable"
            },

            # AI Agent
            {
                "parameters": {
                    "promptType": "define",
                    "text": "={{ $json.message_text }}",
                    "options": {
                        "systemMessage": "={{ $json.system_message }}"
                    }
                },
                "type": "@n8n/n8n-nodes-langchain.agent",
                "typeVersion": 3.1,
                "position": [-256, 0],
                "id": "ai_agent",
                "name": "AI Agent",
                "alwaysOutputData": False,
                "retryOnFail": True,
                "onError": "continueErrorOutput"
            },

            # Chat Model
            {
                "parameters": {
                    "model": {
                        "__rl": True,
                        "value": "glm-4.7",
                        "mode": "list",
                        "cachedResultName": "glm-4.7"
                    },
                    "responsesApiEnabled": False,
                    "options": {
                        "temperature": 0.3,
                        "timeout": 300000,
                        "maxRetries": 2
                    }
                },
                "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
                "typeVersion": 1.3,
                "position": [-416, 224],
                "id": "chat_model",
                "name": "QA Chat Model",
                "retryOnFail": True,
                "onError": "continueRegularOutput"
            },

            # Memory
            {
                "parameters": {
                    "sessionIdType": "customKey",
                    "sessionKey": "={{ $('Telegram Trigger').item.json.message.chat.id }}",
                    "contextWindowLength": 50
                },
                "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
                "typeVersion": 1.3,
                "position": [-864, 224],
                "id": "memory",
                "name": "Simple Memory"
            },

            # Send Success Message
            {
                "parameters": {
                    "chatId": "={{ $('Telegram Trigger').item.json.message.chat.id }}",
                    "text": "={{ $json.output }}",
                    "additionalFields": {
                        "appendAttribution": False,
                        "parse_mode": "HTML"
                    }
                },
                "type": "n8n-nodes-base.telegram",
                "typeVersion": 1.2,
                "position": [192, 0],
                "id": "send_success",
                "name": "Send Success Message",
                "webhookId": "qa_send_success",
                "alwaysOutputData": False,
                "onError": "continueRegularOutput"
            },

            # Send Error Message
            {
                "parameters": {
                    "chatId": "={{ $('Telegram Trigger').item.json.message.chat.id }}",
                    "text": "={{ $json.error }}",
                    "additionalFields": {
                        "appendAttribution": False,
                        "parse_mode": "HTML"
                    }
                },
                "type": "n8n-nodes-base.telegram",
                "typeVersion": 1.2,
                "position": [192, 224],
                "id": "send_error",
                "name": "Send Error Message",
                "webhookId": "qa_send_error",
                "onError": "continueRegularOutput"
            }
        ],
        "connections": {
            "Telegram Trigger": {
                "main": [
                    [
                        {
                            "node": "Set Project Variable",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Set Project Variable": {
                "main": [
                    [
                        {
                            "node": "AI Agent",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Simple Memory": {
                "ai_memory": [
                    [
                        {
                            "node": "AI Agent",
                            "type": "ai_memory",
                            "index": 0
                        }
                    ]
                ]
            },
            "QA Chat Model": {
                "ai_languageModel": [
                    [
                        {
                            "node": "AI Agent",
                            "type": "ai_languageModel",
                            "index": 0
                        }
                    ]
                ]
            },
            "AI Agent": {
                "main": [
                    [
                        {
                            "node": "Send Success Message",
                            "type": "main",
                            "index": 0
                        }
                    ],
                    [
                        {
                            "node": "Send Error Message",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "authors": "Nelson Mazonzika",
        "tags": [
            {
                "name": "QA Unified"
            }
        ]
    }

    # Save workflow to temp file
    with open('/tmp/qa_unified_workflow.json', 'w') as f:
        json.dump(workflow, f, indent=2)

    print("✅ Workflow structure created successfully!")
    print("   File saved to: /tmp/qa_unified_workflow.json")
    print()
    print("Next steps:")
    print("1. Review the workflow at /tmp/qa_unified_workflow.json")
    print("2. Import it into n8n via the UI or API")
    print("3. Add project-specific configurations (dashboard, bug tracker, email, etc.)")
    print("4. Test with each project")

    return workflow

if __name__ == "__main__":
    try:
        workflow = create_workflow()
        print("\n🎉 Workflow structure created successfully!")
        print("\nYou now have:")
        print("- A new n8n workflow structure named 'QA_Unified'")
        print("- Core AI Agent logic")
        print("- Project variable routing")
        print("- Project-specific template")

        print("\n⚠️  Next: Add project-specific configurations")
        print("   - vaulsys: dashboard=vaulsys_Dashboard, bug_tracker=vaulsys_Bug_Tracker")
        print("   - ussd: dashboard=ussd_Dashboard, bug_tracker=ussd_Bug_Tracker")
        print("   - Update email addresses and Telegram bot IDs")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
