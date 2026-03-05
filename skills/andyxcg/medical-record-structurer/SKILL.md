---
name: medical-record-structurer
description: Medical record structuring and standardization tool. Converts doctor's oral or handwritten medical records into standardized electronic medical records (EMR). Supports voice/text input, automatic field recognition, and structured output. Use when processing medical records, clinical notes, patient histories, or converting unstructured medical data into standardized formats. Includes skillpay.me payment integration for pay-per-use monetization.
version: 1.0.3
---

# Medical Record Structurer

A professional medical record processing tool that transforms unstructured medical notes (voice or text) into standardized electronic medical records.

## Features

1. **Voice/Text Input Processing** - Accepts doctor's口述 or handwritten notes
2. **AI-Powered Field Extraction** - Automatically identifies and extracts medical fields
3. **Standardized EMR Output** - Generates structured electronic medical records
4. **Payment Integration** - skillpay.me integration for monetization (0.001 USDT per use)

## Quick Start

### Process a medical record:

```python
from scripts.process_record import process_medical_record
import os

# Set API key via environment variable
os.environ["SKILLPAY_API_KEY"] = "your-api-key"

# Process with user_id for billing
result = process_medical_record(
    input_text="患者张三，男，45岁，主诉头痛3天...",
    user_id="user_123"
)

# Check result
if result["success"]:
    print("结构化病历:", result["structured_record"])
    print("剩余余额:", result["balance"])
else:
    print("错误:", result["error"])
    if "paymentUrl" in result:
        print("充值链接:", result["paymentUrl"])
```

### API Usage:

```bash
# Set API key via environment variable
export SKILLPAY_API_KEY="your-api-key"

# Run with user_id for billing
python scripts/process_record.py \
  --input "患者张三，男，45岁，主诉头痛3天..." \
  --user-id "user_123"
```

## Configuration

The skill uses SkillPay billing integration:
- Provider: skillpay.me
- Price: 0.001 USDT per request
- Chain: BNB Chain
- API Key: Set via `SKILLPAY_API_KEY` environment variable
- Skill ID: Set via `SKILLPAY_SKILL_ID` environment variable

## Output Format

Structured medical record includes:
- Patient demographics (name, age, gender)
- Chief complaint
- History of present illness
- Past medical history
- Physical examination
- Diagnosis
- Treatment plan
- Medications
- Follow-up instructions

## References

- For detailed field specifications: see [references/emr-schema.md](references/emr-schema.md)
- For payment API details: see [references/skillpay-api.md](references/skillpay-api.md)
