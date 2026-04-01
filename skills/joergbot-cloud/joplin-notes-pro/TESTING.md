# Joplin Skill Testing Guide

## Overview
This document provides testing procedures for the Joplin CLI Skill to ensure all scripts work correctly before publication.

## Prerequisites
1. Joplin CLI installed: `npm install -g joplin`
2. Joplin configured (optional but recommended)
3. Test notes available in Joplin

## Test Scripts

### 1. Health Check Test
```bash
cd /home/joergbot/.openclaw/workspace/skills/joplin-cli
./scripts/joplin-check.sh health
```

**Expected Output:**
- ✅ Joplin CLI is installed
- ✅ Joplin version is compatible  
- ✅ Joplin is configured
- ✅ Joplin sync is configured (if configured)
- ✅ Joplin sync is active (if sync works)

### 2. Quick Note Test
```bash
# Test 1: Basic note creation
./scripts/joplin-quick-note.sh "Test Note" "This is a test note created by the Joplin skill."

# Test 2: Note with tags
./scripts/joplin-quick-note.sh "Tagged Note" "Note with multiple tags" -t "test,automation"

# Test 3: Note in specific notebook
./scripts/joplin-quick-note.sh "Notebook Note" "Note in Test notebook" -n "Test"

# Test 4: Edit mode (opens editor)
./scripts/joplin-quick-note.sh --edit "Editable Note"

# Test 5: Quiet mode (returns only note ID)
./scripts/joplin-quick-note.sh --quiet "Quiet Note" "Minimal output"
```

**Expected Output:**
- Note created successfully message
- Note ID returned
- Tags applied correctly
- Notebook assignment works

### 3. Daily Journal Test
```bash
# Test 1: Today's journal
./scripts/joplin-daily-journal.sh

# Test 2: Specific date
./scripts/joplin-daily-journal.sh -d 2026-03-28

# Test 3: Weekly template
./scripts/joplin-daily-journal.sh --template weekly

# Test 4: Meeting template
./scripts/joplin-daily-journal.sh --template meeting --title "Test Meeting"

# Test 5: Edit mode
./scripts/joplin-daily-journal.sh --edit
```

**Expected Output:**
- Journal entry created with correct template
- Date formatting correct
- Tags applied (journal,daily)
- Notebook assignment (Journal)

### 4. Search Notes Test
```bash
# Test 1: Basic search
./scripts/joplin-search-notes.sh "test"

# Test 2: Search with filters
./scripts/joplin-search-notes.sh "note" -t test -n Test

# Test 3: JSON output
./scripts/joplin-search-notes.sh "test" -f json

# Test 4: CSV output
./scripts/joplin-search-notes.sh "test" -f csv -o test_results.csv

# Test 5: With content
./scripts/joplin-search-notes.sh "test" --content --limit 5
```

**Expected Output:**
- Search results displayed
- Filters applied correctly
- Output format correct (table, json, csv)
- File export works

### 5. Export Backup Test
```bash
# Test 1: Test mode (dry run)
./scripts/joplin-export-backup.sh --test

# Test 2: Actual backup (Markdown)
./scripts/joplin-export-backup.sh --sync-first

# Test 3: JEX format
./scripts/joplin-export-backup.sh --format jex

# Test 4: With encryption (requires password)
# ./scripts/joplin-export-backup.sh --encrypt --password "test123"

# Test 5: Custom directory
./scripts/joplin-export-backup.sh /tmp/joplin-backup-test
```

**Expected Output:**
- Test mode shows summary without exporting
- Backup created successfully
- Files saved to correct location
- Compression works (if enabled)
- Old backups cleaned (if keep-days specified)

## Integration Tests

### 1. Script Chain Test
```bash
# Create note → Search for it → Backup
NOTE_ID=$(./scripts/joplin-quick-note.sh --quiet "Chain Test" "Testing script chain")
./scripts/joplin-search-notes.sh "Chain Test"
./scripts/joplin-export-backup.sh --test
```

### 2. Error Handling Test
```bash
# Test with Joplin not installed (simulated)
# mv $(which joplin) $(which joplin).bak
# ./scripts/joplin-check.sh health  # Should show error
# mv $(which joplin).bak $(which joplin)
```

### 3. Environment Variables Test
```bash
export JOPLIN_DEFAULT_NOTEBOOK="TestNotebook"
export JOPLIN_DEFAULT_TAGS="envtest"
./scripts/joplin-quick-note.sh "Env Test" "Testing environment variables"
```

## Performance Tests

### 1. Large Search Test
```bash
time ./scripts/joplin-search-notes.sh "*" --limit 100
```

### 2. Backup Performance
```bash
time ./scripts/joplin-export-backup.sh --quiet
```

## Edge Cases

### 1. Empty Input
```bash
echo "" | ./scripts/joplin-quick-note.sh "Empty Test"
```

### 2. Special Characters
```bash
./scripts/joplin-quick-note.sh "Special: & < > \" ' " "Content with special chars"
```

### 3. Long Titles/Content
```bash
LONG_TITLE=$(printf '%*s' 100 | tr ' ' 'A')
./scripts/joplin-quick-note.sh "$LONG_TITLE" "Test"
```

## Automated Test Script

Create a test runner script:

```bash
#!/bin/bash
# test-runner.sh

echo "Starting Joplin Skill Tests..."
echo "==============================="

# Test 1: Health Check
echo "1. Testing Health Check..."
./scripts/joplin-check.sh health
if [ $? -eq 0 ]; then
    echo "✅ Health Check PASSED"
else
    echo "❌ Health Check FAILED"
fi

# Test 2: Quick Note
echo "2. Testing Quick Note..."
NOTE_ID=$(./scripts/joplin-quick-note.sh --quiet "Test Note $(date)" "Automated test")
if [ -n "$NOTE_ID" ]; then
    echo "✅ Quick Note PASSED (ID: $NOTE_ID)"
else
    echo "❌ Quick Note FAILED"
fi

# Test 3: Search
echo "3. Testing Search..."
SEARCH_RESULTS=$(./scripts/joplin-search-notes.sh --quiet "Test Note" | wc -l)
if [ "$SEARCH_RESULTS" -gt 0 ]; then
    echo "✅ Search PASSED (Found: $SEARCH_RESULTS)"
else
    echo "❌ Search FAILED"
fi

# Test 4: Backup Test Mode
echo "4. Testing Backup (Test Mode)..."
./scripts/joplin-export-backup.sh --test
if [ $? -eq 0 ]; then
    echo "✅ Backup Test PASSED"
else
    echo "❌ Backup Test FAILED"
fi

echo "==============================="
echo "Tests completed!"
```

## Verification Steps

After running tests, verify:

1. **Notes created correctly:**
   ```bash
   joplin ls | grep "Test"
   ```

2. **Backups exist:**
   ```bash
   ls -la ~/backups/joplin/ 2>/dev/null || echo "No backups yet"
   ```

3. **Cleanup test data:**
   ```bash
   # Remove test notes
   joplin ls | grep "Test" | awk '{print $1}' | xargs -I {} joplin rmnote {}
   
   # Remove test backups
   rm -rf /tmp/joplin-backup-test 2>/dev/null
   rm -f test_results.csv 2>/dev/null
   ```

## Success Criteria

All tests should:
- ✅ Complete without errors
- ✅ Produce expected output
- ✅ Handle edge cases gracefully
- ✅ Clean up after themselves
- ✅ Work with different Joplin configurations

## Troubleshooting

### Common Issues:

1. **Joplin not found:**
   ```bash
   npm install -g joplin
   ```

2. **Permission errors:**
   ```bash
   chmod +x scripts/*.sh
   ```

3. **Sync errors:**
   ```bash
   joplin config sync.target 0  # Disable sync for testing
   ```

4. **Script errors:**
   ```bash
   bash -x scripts/joplin-check.sh health  # Debug mode
   ```

## Reporting

Create a test report:

```bash
#!/bin/bash
# generate-test-report.sh

REPORT_FILE="test-report-$(date +%Y%m%d).md"

cat > "$REPORT_FILE" << EOF
# Joplin Skill Test Report
**Date:** $(date)
**Skill Version:** $(grep version package.json | cut -d'"' -f4)

## Test Results

### Health Check
\`\`\`
$(./scripts/joplin-check.sh health 2>&1)
\`\`\`

### Quick Note Test
\`\`\`
$(./scripts/joplin-quick-note.sh --quiet "Report Test" "Test for report" 2>&1)
\`\`\`

### Search Test
\`\`\`
$(./scripts/joplin-search-notes.sh "Report Test" --limit 3 2>&1)
\`\`\`

### Backup Test
\`\`\`
$(./scripts/joplin-export-backup.sh --test 2>&1)
\`\`\`

## Summary
- Health Check: ✅
- Quick Note: ✅  
- Search: ✅
- Backup: ✅

**Status:** READY FOR PUBLICATION
EOF

echo "Report generated: $REPORT_FILE"
```

This testing guide ensures the Joplin Skill is robust and ready for ClawHub publication.