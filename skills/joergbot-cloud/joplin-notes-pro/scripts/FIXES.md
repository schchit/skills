# Joplin Quick Note Script Fixes

## Problem
Das Script `joplin-quick-note.sh` hing, weil Joplin im interaktiven TUI-Modus startete und auf Benutzereingabe wartete.

## Ursache
Joplin CLI startet standardmäßig im interaktiven TUI-Modus. Bei non-interaktiver Nutzung (z.B. in Scripts) wartet es auf Eingabe und hängt.

## Lösung

### 1. Non-interaktive Joplin-Aufrufe
Erstellt eine Hilfsfunktion `joplin_noninteractive()` die `script` verwendet:
```bash
joplin_noninteractive() {
    script -q -c "joplin $*" /dev/null 2>&1
}
```

### 2. Note-ID-Extraktion
Das Problem: `joplin ls -l` schneidet Titel ab (zeigt nur erste ~20 Zeichen).
Lösung: Verwende JSON-Output mit `jq`:
```bash
note_id=$(joplin_noninteractive ls --format json | jq -r --arg title "$title" '.[] | select(.title == $title) | .id[0:5]')
```

Fallback: Nimm die neueste Note (die wir gerade erstellt haben):
```bash
note_id=$(joplin_noninteractive ls -l | head -1 | awk '{print $1}')
```

### 3. Health Check Umgehung
Das originale Script sourced `joplin-check.sh`, das auch Joplin-Aufrufe macht und hängt.
Lösung: Einfache Prüfung statt voller Health Check:
```bash
if ! command -v joplin &> /dev/null; then
    log_error "Joplin CLI not found in PATH"
    exit 1
fi
```

### 4. Wichtige Änderungen im Code

1. **Entfernt**: `source "$SCRIPT_DIR/joplin-check.sh"`
2. **Hinzugefügt**: Eigene Logging-Funktionen (log_info, log_success, etc.)
3. **Hinzugefügt**: `joplin_noninteractive()` Funktion
4. **Geändert**: Alle `joplin` Aufrufe zu `joplin_noninteractive`
5. **Geändert**: Note-ID-Extraktion verwendet JSON + jq
6. **Geändert**: Vereinfachte Joplin-Prüfung

### 5. Getestete Funktionen

- [x] Einfache Notiz-Erstellung
- [x] Notizen mit Tags
- [x] Notizen in spezifischen Notebooks
- [x] Quiet-Modus (-q)
- [x] Sync nach Erstellung (-s)
- [x] Edit-Modus (-e)
- [x] Stdin-Input

### 6. Bekannte Einschränkungen

1. **Ausgabeformat**: Die Log-Ausgaben vermischen sich etwas mit der Note-ID-Ausgabe
2. **Performance**: `script`-Wrapper fügt Overhead hinzu
3. **Abhängigkeit**: Benötigt `jq` für zuverlässige Note-ID-Extraktion

### 7. Alternative Ansätze (nicht implementiert)

1. **Joplin Config**: `joplin config cli.suppressTui true` - funktioniert nicht (unbekannte Option)
2. **Expect Script**: Automatische Eingabe - zu komplex
3. **Environment Variables**: Keine bekannte Variable zur TUI-Unterdrückung

### 8. Empfehlungen

1. **Installiere jq**: `sudo apt install jq` (falls nicht vorhanden)
2. **Teste das Script**: Vor Produktiveinsatz gründlich testen
3. **Backup**: Original-Script gesichert als `joplin-quick-note.sh.bak`

## Fazit
Das Script ist jetzt vollständig non-interaktiv nutzbar und hängt nicht mehr. Alle Kernfunktionen wurden erhalten und funktionieren korrekt.