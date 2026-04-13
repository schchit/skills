---
name: essential-tools
description: Catalogue d'outils installables a la demande. Utilise quand l'utilisateur tape /tools ou quand tu as besoin d'un package non disponible.
version: 1.2.0
author: qapten
---

# Essential Tools

Catalogue d'outils pre-references et versionnes, installables a la demande par categorie ou individuellement.

## Contexte de securite

Ces packages s'executent dans un conteneur Docker isole (OpenClaw) avec des limites de ressources (memoire, CPU, PIDs) et un reseau Docker dedie. L'installation n'affecte que le conteneur de l'utilisateur, pas le systeme hote.

**Garanties supplementaires :**

- Installations toujours en `--no-save` (npm) ou `--user` (pip) — ephemere, pas de pollution persistante
- Aucune installation globale (`-g` / `--global` interdits)
- Aucune requete HTTP vers des cibles internes : `localhost`, `127.0.0.0/8`, `169.254.169.254` (metadata cloud), `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
- Respect de `robots.txt` lors du scraping
- Aucune exfiltration de donnees vers des services tiers de partage

## Commande /tools

| Commande | Action |
|----------|--------|
| `/tools` | Afficher le catalogue des outils disponibles par categorie |
| `/tools install <categorie>` | Installer tous les packages d'une categorie |
| `/tools install <package>` | Installer un package specifique |
| `/tools status` | Voir les packages deja installes |

## Catalogue

### docs — Generation de documents

Commande d'installation :

```bash
npm install --no-save pptxgenjs@3.12.0 docx@9.5.0 exceljs@4.4.0 pdfkit@0.16.0 pdf-parse@1.1.1 csv-parse@5.6.0 csv-stringify@6.5.2
```

| Package | Usage |
|---------|-------|
| `pptxgenjs@3.12.0` | Creer des presentations PowerPoint (.pptx) |
| `docx@9.5.0` | Creer des documents Word (.docx) |
| `exceljs@4.4.0` | Creer des tableurs Excel (.xlsx) |
| `pdfkit@0.16.0` | Generer des PDF |
| `pdf-parse@1.1.1` | Lire et extraire le texte de PDF existants |
| `csv-parse@5.6.0` + `csv-stringify@6.5.2` | Lire / ecrire des CSV |

### images — Traitement d'images

```bash
npm install --no-save sharp@0.33.5 qrcode@1.5.4
```

| Package | Usage |
|---------|-------|
| `sharp@0.33.5` | Redimensionner, convertir, compresser des images |
| `qrcode@1.5.4` | Generer des QR codes |

### web — Scraping et veille

```bash
npm install --no-save cheerio@1.0.0 axios@1.7.9 rss-parser@3.13.0 xml2js@0.6.2
```

| Package | Usage |
|---------|-------|
| `cheerio@1.0.0` | Parser du HTML (scraping leger sans navigateur) |
| `axios@1.7.9` | Requetes HTTP robustes avec retry |
| `rss-parser@3.13.0` | Lire des flux RSS / Atom |
| `xml2js@0.6.2` | Parser du XML (BOAMP, TED, etc.) |

> **Securite reseau** : ces librairies ne doivent jamais cibler `localhost`, des plages privees (`10/8`, `172.16/12`, `192.168/16`) ou des endpoints de metadata cloud (`169.254.169.254`). Toute URL doit etre fournie par l'utilisateur ou provenir d'un domaine public.

### utils — Utilitaires

```bash
npm install --no-save lodash@4.17.21 dayjs@1.11.13 archiver@7.0.1 turndown@7.2.0 form-data@4.0.1
```

| Package | Usage |
|---------|-------|
| `lodash@4.17.21` | Manipulation avancee de donnees |
| `dayjs@1.11.13` | Dates, fuseaux horaires, formatage |
| `archiver@7.0.1` | Creer des archives ZIP |
| `turndown@7.2.0` | Convertir HTML en Markdown |
| `form-data@4.0.1` | Upload multipart (envoi fichiers Telegram) |

> Pour convertir JSON en CSV, utiliser `csv-stringify` (deja dans la categorie `docs`) — plus stable que `json2csv` qui n'a pas de release stable.

### python — Outils Python

```bash
pip install --user pandas==2.2.3 matplotlib==3.10.0 openpyxl==3.1.5 requests==2.32.3 beautifulsoup4==4.12.3
```

| Package | Usage |
|---------|-------|
| `pandas==2.2.3` | Analyse et manipulation de donnees |
| `matplotlib==3.10.0` | Graphiques et visualisations |
| `openpyxl==3.1.5` | Lire / ecrire Excel depuis Python |
| `requests==2.32.3` | Requetes HTTP (memes restrictions reseau que `axios`) |
| `beautifulsoup4==4.12.3` | Parsing HTML depuis Python |

### send — Envoi de fichiers vers Telegram

Pas d'installation de packages. Utilise la CLI OpenClaw integree.

```bash
openclaw message send --channel telegram --target <chat_id> --media <chemin_du_fichier>
```

- **Fichiers cibles** : placer dans `/tmp/openclaw/media/outbound/`
- **Chat ID** : utiliser le chat ID **fourni par l'utilisateur courant** dans la conversation. Ne jamais hardcoder un identifiant.
- **Types autorises (allowlist)** : `xlsx`, `xls`, `docx`, `doc`, `pptx`, `ppt`, `pdf`, `csv`, `txt`, `md`, `json`, `xml`, `png`, `jpg`, `jpeg`, `gif`, `webp`, `svg`, `zip`
- **Types interdits (denylist)** : tout fichier executable ou script — `.exe`, `.bat`, `.sh`, `.cmd`, `.ps1`, `.js`, `.py`, `.bin`, `.app`, `.msi`, `.dmg`, `.apk`, `.deb`, `.rpm`, `.jar`

Exemple :

```bash
openclaw message send --channel telegram --target $TELEGRAM_CHAT_ID --media /tmp/openclaw/media/outbound/rapport.xlsx
```

> **Interdiction stricte** : ne jamais utiliser de services tiers de partage (`tmpfiles.org`, `file.io`, `transfer.sh`, pastebin, gist, etc.) — risque securite, exfiltration et malware.

## Comportement

### Installation a la demande

Quand l'utilisateur demande une tache necessitant un package du catalogue :

1. **Verifier** si le package est deja installe (`npm list <pkg>` ou `pip show <pkg>`)
2. **Si manquant** : annoncer explicitement `J'installe <package>@<version> pour <raison precise>` et **attendre une confirmation explicite par package** (pas une confirmation groupee)
3. **Une fois confirme**, installer le package avec la version **exacte** specifiee dans ce catalogue, en mode `--no-save` (npm) ou `--user` (pip)
4. Executer la tache demandee
5. **Ne jamais** installer un package absent du catalogue sans une confirmation explicite et un avertissement clair sur le risque supply-chain

### Restrictions de securite

- **Versions epinglees** : installer TOUJOURS la version exacte listee (ex: `npm install --no-save sharp@0.33.5`, jamais `npm install sharp`)
- **Pas d'install globale** : jamais de `-g` / `--global`, jamais de modification du `package.json` persistant
- **Catalogue ferme** : seuls les packages listes sont autorises en installation rapide
- **Registres officiels uniquement** : `registry.npmjs.org` et `pypi.org` exclusivement
- **Pas de scripts post-install custom** : refuser tout package qui declenche un `postinstall` non documente

### Affichage du catalogue

Quand l'utilisateur tape `/tools` :

- Afficher les categories avec une description courte de chaque outil
- Indiquer lesquels sont deja installes (✅) ou non (⬚)

---

Skill creee le 7 avril 2026 par Qapten — version 1.2.0 (audit de securite).
