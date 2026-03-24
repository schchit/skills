---
name: n8n
description: >
  Gestion sécurisée des workflows n8n via API REST. Utilise ce skill pour : lister, cloner, 
  tester, modifier et promouvoir des workflows. Actions critiques (suppression, promotion en prod) 
  nécessitent une validation admin. Phrases déclencheuses : "list workflows", "clone workflow", 
  "test workflow", "crée un workflow", "modifie workflow n8n", "exécute workflow".
requires:
  bins: [python3]
  env:
    - N8N_URL
    - N8N_API_TOKEN
    - ADMIN_EMAIL
emoji: ⚙️
---

# n8n Skill — Workflow Management Sécurisé

Gère les workflows n8n via API REST avec sécurité intégrée.

## Prérequis

- `python3` avec `requests` installé
- Variables d'environnement configurées :
  - `N8N_URL` — URL de l'instance n8n
  - `N8N_API_TOKEN` — Clé API n8n
  - `ADMIN_EMAIL` — Email de l'admin (nel@illicocash.com)

## Configuration

Les variables sont dans le fichier `.env` du skill :
```
/data/.openclaw/workspace/skills/n8n/scripts/.env
```

## Commandes disponibles

Toutes les commandes utilisent le header `X-N8N-API-KEY` (format n8n, pas Bearer).

### Lister les workflows
```bash
python3 scripts/skill.py list
```

### Obtenir un workflow
```bash
python3 scripts/skill.py get <workflow_id>
```

### Cloner un workflow (crée une copie _test)
```bash
python3 scripts/skill.py clone <workflow_id> [--suffix "_test"]
```

### Exécuter un workflow en mode test
```bash
python3 scripts/skill.py execute <workflow_id> [--input '{"key":"value"}']
```

### Tests de santé sur une exécution
```bash
python3 scripts/skill.py check <execution_id>
```

### Promouvoir un workflow test vers production
```bash
python3 scripts/skill.py promote <test_id> <original_id>
```

### Supprimer un workflow (admin uniquement)
```bash
python3 scripts/skill.py delete <workflow_id> --confirm
```

### Créer un workflow
```bash
python3 scripts/skill.py create --file workflow.json
```

### Activer/Désactiver un workflow
```bash
python3 scripts/skill.py activate <workflow_id>
python3 scripts/skill.py deactivate <workflow_id>
```

### Historique des exécutions
```bash
python3 scripts/skill.py history <workflow_id> [--limit 10]
```

## Règles de Sécurité

1. **Actions critiques** (delete, promote) nécessitent `--confirm` + vérification admin
2. **Clone avant modification** : toute modification crée d'abord une copie `_test`
3. **Tests de santé** automatiques après exécution (erreurs de nodes, durée, outputs)
4. **Rollback** : l'original est désactivé, pas supprimé (récupérable)
5. **Pas de suppression sans confirmation explicite**

## Workflow de Test avant Production

```
1. Clone le workflow → <name>_test
2. Exécute la copie test
3. Vérifie les sanity checks
4. Si OK → demande confirmation admin
5. Si confirmé → promeut en production
6. Sinon → supprime la copie test
```

## Sanity Checks

Vérifications automatiques après chaque exécution :
- ❌ Aucun node ne doit avoir d'erreur
- ⏱️ Durée d'exécution < 5 secondes (configurable)
- 📊 Vérification des outputs des nodes

## Ressources

- `scripts/skill.py` — Script principal
- `scripts/.env` — Variables d'environnement
- `references/` — Documentation API n8n
