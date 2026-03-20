---
name: agricultural-output-forecasting
description: Agricultural Product Output Forecasting Based on Big Data. Predicts crop yields and agricultural output using historical data, weather patterns, and market trends. Use when forecasting agricultural production, estimating crop yields, analyzing farming trends, or making data-driven decisions in agriculture.
version: 1.1.1
---

# Agricultural Output Forecasting

> **Version**: 1.1.0  
> **Category**: Agriculture / Analytics  
> **Billing**: SkillPay (1 token per call, ~0.001 USDT)  
> **Free Trial**: 10 free calls per user  
> **Demo Mode**: ✅ Available (no API key required)

A big data-driven agricultural product output forecasting tool that helps farmers, agronomists, and agricultural businesses predict crop yields and production outputs.

## Features

1. **Yield Prediction** - Forecast crop yields based on historical data and current conditions
2. **Weather Impact Analysis** - Factor in weather patterns and climate data
3. **Market Trend Integration** - Consider market prices and demand trends
4. **Multi-Crop Support** - Support for various agricultural products (grains, vegetables, fruits, etc.)
5. **SkillPay Billing** - Pay-per-use monetization (1 token per call, ~0.001 USDT)
6. **Free Trial** - 10 free calls for every new user
7. **Demo Mode** - Try without API key, returns simulated forecasts
8. **Historical Data** - Track and compare with past forecasts
9. **CSV Export** - Export forecast data to CSV format
10. **Multi-language Support** - Chinese and English output

## Support / 支持

If you find this skill helpful, you can support the developer:

**EVM Address**: `0xf8ea28c182245d9f66f63749c9bbfb3cfc7d4815`

Your support helps maintain and improve this skill!

## Demo Mode

Try the skill without any API key:

```bash
python scripts/forecast.py --demo --crop wheat --area 100 --region "华北平原" --season spring
```

Demo mode returns realistic simulated agricultural forecasts to demonstrate the output format.

## Free Trial

Each user gets **10 free calls** before billing begins. During the trial:
- No payment required
- Full feature access
- Trial status returned in API response

```python
{
    "success": True,
    "trial_mode": True,      # Currently in free trial
    "trial_remaining": 7,    # 7 free calls left
    "balance": None,         # No balance needed in trial
    "forecast": {...}
}
```

After 10 free calls, normal billing applies.

## Quick Start

### Demo Mode (No API Key):

```bash
python scripts/forecast.py --demo --crop wheat --area 100 --region "华北平原" --season spring
```

### Forecast agricultural output:

```python
from scripts.forecast import forecast_output
import os

# Set environment variables (only needed after trial)
os.environ["SKILLPAY_API_KEY"] = "your-api-key"
os.environ["SKILLPAY_SKILL_ID"] = "your-skill-id"

# Forecast wheat yield
result = forecast_output(
    crop_type="wheat",
    area_hectares=100,
    region="North China Plain",
    season="spring",
    user_id="user_123"
)

# Check result
if result["success"]:
    print("预测产量:", result["forecast"])
    if result.get("trial_mode"):
        print(f"免费试用剩余: {result['trial_remaining']} 次")
    else:
        print("剩余余额:", result["balance"])
else:
    print("错误:", result["error"])
    if "paymentUrl" in result:
        print("充值链接:", result["paymentUrl"])
```

### View Forecast History:

```bash
python scripts/forecast.py --history --limit 10
```

### Export to CSV:

```bash
python scripts/forecast.py --history --limit 20 --export forecasts.csv
```

### Language Selection:

```bash
# Chinese output (default)
python scripts/forecast.py --crop rice --area 50 --region "长江三角洲" --season summer --user-id "user_123" --language zh

# English output
python scripts/forecast.py --crop rice --area 50 --region "Yangtze Delta" --season summer --user-id "user_123" --language en
```

## Environment Variables

This skill requires the following environment variables:

### Required Variables (After Trial)

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SKILLPAY_API_KEY` | Your SkillPay API key for billing | After trial | `skp_abc123...` |
| `SKILLPAY_SKILL_ID` | Your Skill ID from SkillPay dashboard | After trial | `skill_def456...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key for weather data | - |
| `WEATHERAPI_KEY` | WeatherAPI key for alternative weather data | - |
| `USDA_API_KEY` | USDA API key for US agricultural data | - |
| `OPENAI_API_KEY` | OpenAI API key for enhanced forecasting | - |
| `CACHE_DURATION_MINUTES` | Cache duration for weather/market data | `60` |
| `MAX_FORECAST_AREA` | Maximum area in hectares per request | `10000` |

See `.env.example` for a complete list of environment variables.

## Configuration

The skill uses SkillPay billing integration:
- Provider: skillpay.me
- Pricing: 1 token per call (~0.001 USDT)
- Chain: BNB Chain
- Free Trial: 10 calls per user
- Demo Mode: Available without API key
- API Key: Set via `SKILLPAY_API_KEY` environment variable
- Skill ID: Set via `SKILLPAY_SKILL_ID` environment variable
- Minimum deposit: 8 USDT

## Supported Crops

- Grains: wheat, rice, corn, barley, sorghum
- Vegetables: tomato, potato, cabbage, cucumber
- Fruits: apple, orange, grape, peach
- Others: soybean, cotton, sugarcane

## Output Format

Forecast results include:
- Predicted yield (tons/hectare)
- Confidence interval
- Weather impact factor
- Market price prediction
- Risk assessment
- Recommendations
- Historical comparison

### Response Format

```python
{
    "success": True,
    "demo_mode": False,         # True if in demo mode
    "trial_mode": False,        # True during free trial
    "trial_remaining": 0,       # Remaining free calls
    "balance": 95.5,            # User balance (None during trial/demo)
    "forecast": {
        "forecast_id": "AGR_20240306120000",
        "crop_type": "wheat",
        "yield_forecast": {...},
        "risk_assessment": {...},
        "recommendations": [...],
        "historical_comparison": {...}
    }
}
```

## Security Considerations

### Data Privacy
- Agricultural data is treated as confidential business information
- No personally identifiable information (PII) is collected
- Weather and market data is cached to minimize API calls

### API Key Security
- Never commit API keys to version control
- Use environment variables for all sensitive configuration
- Rotate API keys regularly

## References

- For forecast methodology: see [references/forecast-methodology.md](references/forecast-methodology.md)
- For billing API details: see [references/skillpay-billing.md](references/skillpay-billing.md)
- For full documentation: see [README.md](README.md)

## Changelog

### v1.1.0
- Added demo mode (no API key required)
- Added forecast history tracking
- Added CSV export functionality
- Added historical data comparison
- Added multi-language support (zh/en)
- Unified environment variable naming to `SKILLPAY_API_KEY` and `SKILLPAY_SKILL_ID`

### v1.0.1
- Initial stable release
- SkillPay billing integration
- Free trial support
