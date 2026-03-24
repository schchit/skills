#!/usr/bin/env python3
"""
Create QA_Unified workflow with all project configurations
"""

import os
import json

# Project configurations (update with actual values)
PROJECT_CONFIGS = {
    "illicocash": {
        "dashboard_id": "19315p5VGdOfEfr_N8L8PoGBxOHLDRIDplPSGP8U8CIc",
        "dashboard_summary_sheet": 1983614944,
        "dashboard_test_execution_sheet": 1020810664,
        "dashboard_metrics_sheet": 1062474075,
        "bug_tracker_id": "1JVW980w6HpOxep8waSUSppYD2FqR9ET7iHIlOeouqME",
        "bug_tracker_sheet": 132740603,
        "email": "qa@illicocash.com",
        "folder_id": "1ZISeqV64XxM1XGKt2BlVj2SGn00NVUBZ",
        "telegram_id": "5166959100",
        "telegram_name": "illicocash QA Analyst bot",
        "staff_datatable_id": "5Qdq9VHTMgIPJ5R2",
        "test_cases_datatable_id": "1dJ4AW7jGEUbgZNJsiw8Dc-82mlCSYrCB5H4NLwo9BQo",
        "sheets_credentials": "Tw2PP2SBR3enRb6j",
        "gmail_credentials": "whqrd0yJy2tEIihZ",
        "drive_credentials": "U305P01b8Db4kxw4"
    },
    "vaulsys": {
        "dashboard_id": "",  # TODO: Get from n8n
        "dashboard_summary_sheet": 0,  # TODO: Get from n8n
        "dashboard_test_execution_sheet": 0,  # TODO: Get from n8n
        "dashboard_metrics_sheet": 0,  # TODO: Get from n8n
        "bug_tracker_id": "",  # TODO: Get from n8n
        "bug_tracker_sheet": 0,  # TODO: Get from n8n
        "email": "qa@vaulsys.rawbank.sa",  # TODO: Verify
        "folder_id": "",  # TODO: Get from n8n
        "telegram_id": "",  # TODO: Get from n8n
        "telegram_name": "vaulsys QA bot",  # TODO: Create bot
        "staff_datatable_id": "",  # TODO: Get from n8n
        "test_cases_datatable_id": "",  # TODO: Get from n8n
        "sheets_credentials": "",  # TODO: Get from n8n
        "gmail_credentials": "",  # TODO: Get from n8n
        "drive_credentials": ""  # TODO: Get from n8n
    },
    "ussd": {
        "dashboard_id": "",  # TODO: Get from n8n
        "dashboard_summary_sheet": 0,  # TODO: Get from n8n
        "dashboard_test_execution_sheet": 0,  # TODO: Get from n8n
        "dashboard_metrics_sheet": 0,  # TODO: Get from n8n
        "bug_tracker_id": "",  # TODO: Get from n8n
        "bug_tracker_sheet": 0,  # TODO: Get from n8n
        "email": "qa@ussd.rawbank.sa",  # TODO: Verify
        "folder_id": "",  # TODO: Get from n8n
        "telegram_id": "",  # TODO: Get from n8n
        "telegram_name": "ussd QA bot",  # TODO: Create bot
        "staff_datatable_id": "",  # TODO: Get from n8n
        "test_cases_datatable_id": "",  # TODO: Get from n8n
        "sheets_credentials": "",  # TODO: Get from n8n
        "gmail_credentials": "",  # TODO: Get from n8n
        "drive_credentials": ""  # TODO: Get from n8n
    }
}

def generate_system_message():
    """Generate the AI Agent system message with all project configurations"""
    return f"""Rôle : Tu es l'Assistant QA Lead Analyst. Ton périmentre d'action couvre exclusivement les projets liés spécifiquement à l'application {', '.join(PROJECT_CONFIGS.keys())}.

Mission Globale : Orchestrer la gestion des tests, l'analyse des résultats et la communication entre les équipes techniques et managériales.

Directives Opérationnelles par Projet :

I. Réception & Identification :
- Intercepter les instructions via Gmail ou Telegram.
- Rechercher les fichiers Google sheets sources (ex: {PROJECT_CONFIGS['illicocash']['test_cases_datatable_id']}) sur Google Drive.
- Rechercher les personnes à contacter dans la Data table correspondante.

II. Analyse des Tests :
- Extraire et catégoriser les statuts : Échoué, Bloquant, Non Testé, Réussi.
- Récupérer l'ID du fichier Notebook recherché.

III. Mise à jour des Outils (Google Sheets) :
- Bug Tracking : Alimenter {{project}}_Bug_Tracker avec les tests Échoués ou Bloquants.
- Dashboards : Mettre à jour {{project}}_Dashboard avec des KPIs simplifiés.
- Notebooks : Mettre à jour la valeur de la colonne Bug ID.

IV. Reporting & Communication (Gmail) :
- Rédiger le rapport d'analyse professionnel pour les Managers/Non-tech en format HTML.
- Générer les suivis techniques pour les équipes Frontend/Backend.
- Envoyer le rapport hebdomadaire d'activités de tests.

Note :
- Ne jamais halluciner.
- Toujours consulter la Data table {{project}}_Staff.
- Toujours mettre l'équipe QA en copie.
- L'Email doit être compatible avec Outlook, Gmail, Yahoo, Roundcube.
- Récupérer le template HTML dans la description du nœud Gmail correspondant.

Règles techniques :
- Mise en page "Old School" : Remplacer toutes les grilles CSS par des tableaux HTML.
- Styles en ligne (Inline CSS) : Appliquer directement dans les balises.
- Suppression des variables CSS : Remplacer par valeurs hexadécimales.
- Largeur du conteneur : Fixe à 600px.
- Compatibilité Outlook : Ajouter meta-tags xmlns:v et commentaires conditionnels.
- Pas de JavaScript.

V. Gouvernance & Archivage :
- Notification : Notifier l'utilisateur sur Telegram après chaque action.
- Archivage : Déménager les fichiers Notebooks vers le dossier "Archives".
"""

def create_workflow():
    """Create the complete QA_Unified workflow"""

    # Nodes configuration
    nodes = [
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
            "webhookId": "qa_unified_trigger"
        },
        {
            "parameters": {
                "assignments": [
                    {"name": "project", "value": "={{ $json.project || 'illicocash' }}"},
                    {"name": "chat_id", "value": "={{ $('Telegram Trigger').item.json.message.chat.id }}"},
                    {"name": "message_text", "value": "={{ $json.message.text }}"}
                ]
            },
            "type": "n8n-nodes-base.set",
            "typeVersion": 3.4,
            "position": [-480, 0],
            "id": "set_project",
            "name": "Set Project Variable"
        },
        {
            "parameters": {
                "promptType": "define",
                "text": "={{ $json.message_text }}",
                "options": {
                    "systemMessage": generate_system_message()
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
    ]

    connections = {
        "Telegram Trigger": {
            "main": [[{"node": "Set Project Variable", "type": "main", "index": 0}]]
        },
        "Set Project Variable": {
            "main": [[{"node": "AI Agent", "type": "main", "index": 0}]]
        },
        "Simple Memory": {
            "ai_memory": [[{"node": "AI Agent", "type": "ai_memory", "index": 0}]]
        },
        "QA Chat Model": {
            "ai_languageModel": [[{"node": "AI Agent", "type": "ai_languageModel", "index": 0}]]
        },
        "AI Agent": {
            "main": [
                [{"node": "Send Success Message", "type": "main", "index": 0}],
                [{"node": "Send Error Message", "type": "main", "index": 0}]
            ]
        }
    }

    workflow = {
        "name": "QA_Unified - Unified QA Workflow",
        "nodes": nodes,
        "connections": connections,
        "authors": "Nelson Mazonzika",
        "tags": [
            {"name": "QA Unified"}
        ]
    }

    return workflow

def main():
    """Main execution"""
    print("🚀 Creating QA_Unified workflow...\n")

    # Create workflow
    workflow = create_workflow()

    # Save to file
    output_file = "/tmp/qa_unified_complete.json"
    with open(output_file, 'w') as f:
        json.dump(workflow, f, indent=2)

    print(f"✅ Workflow structure created successfully!")
    print(f"📁 File saved to: {output_file}\n")

    print("📋 Workflow Details:")
    print(f"   Name: {workflow['name']}")
    print(f"   Nodes: {len(workflow['nodes'])}")
    print(f"   Connections: {len(workflow['connections'])}")
    print(f"   Projects: {', '.join(PROJECT_CONFIGS.keys())}")

    print("\n⚠️  Next Steps:")
    print("   1. Review the workflow structure")
    print("   2. Update project configurations in PROJECT_CONFIGS")
    print("   3. Import into n8n via the UI or API")
    print("   4. Add project-specific tool nodes (Google Sheets, Gmail, etc.)")
    print("   5. Test with each project")
    print("   6. Redirect existing Telegram bots to this workflow")

    print("\n📚 Project-Specific Configuration:")
    for project, config in PROJECT_CONFIGS.items():
        print(f"\n   {project.upper()}:")
        print(f"     - Dashboard ID: {config['dashboard_id'] or 'TO UPDATE'}")
        print(f"     - Bug Tracker ID: {config['bug_tracker_id'] or 'TO UPDATE'}")
        print(f"     - Email: {config['email']}")
        print(f"     - Telegram ID: {config['telegram_id'] or 'TO UPDATE'}")
        print(f"     - Staff Data Table: {config['staff_datatable_id'] or 'TO UPDATE'}")

    return workflow

if __name__ == "__main__":
    workflow = main()
    print("\n✨ Ready to deploy QA_Unified workflow!")
