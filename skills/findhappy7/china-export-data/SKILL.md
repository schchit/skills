---
name: china-export-data
description: Access and retrieve China's official export statistics from authoritative sources. Provides step-by-step guidance for querying trade data by HS code, destination country, time period, and other dimensions. Essential for baseline market research and verification.
---

# China Export Data

**Purpose**: Provide straightforward access to official Chinese export statistics for research, verification, and baseline market analysis.

**Target Users**: Researchers, analysts, students, small business owners, and anyone needing factual China export data without advanced analytics requirements.

---

## Official Data Sources

### Source 1: UN Comtrade Database

**Website**: https://comtradeplus.un.org/

**What it contains**:
- China's exports reported to the UN by partner countries
- Mirror data (what partner countries report importing from China)
- Global coverage with standardized HS codes
- Historical data from 1962 to present

**Best for**:
- Comparing China with other exporting countries
- Analyzing China's exports to specific destination markets
- Long-term historical trend analysis
- Cross-country benchmarking

**Access methods**:

| Method | URL | Requirements | Best For |
|--------|-----|--------------|----------|
| Web Interface | https://comtradeplus.un.org/lab?r=156 | Free | One-off queries |
| API | https://comtradeapi.un.org/docs/v1 | Registration + API key | Automated queries |
| Bulk Download | Premium subscription | Paid subscription | Large datasets |

**API Registration**:
1. Visit https://uncomtrade.org/docs/api-subscription-keys/
2. Create account
3. Request API key for "comtrade - v1" (free tier: 100 calls/hour)
4. Premium tier available for unlimited access

### Source 2: China Customs Statistics

**Website**: http://stats.customs.gov.cn/indexEn

**What it contains**:
- Official export statistics from China's General Administration of Customs
- More granular data than UN Comtrade
- Port-level breakdowns
- Trade mode classifications
- Domestic destination information

**Best for**:
- Most authoritative China-specific data
- Port and regional analysis within China
- Recent monthly data (1-2 month lag)
- Detailed product classifications

**Navigation Guide**:

```
English Interface Navigation:

Home (http://stats.customs.gov.cn/indexEn)
├── Query by HS Code
│   ├── Select Year/Month
│   ├── Select HS Code (Chapter → Heading → Subheading)
│   ├── Select Trade Flow (Export/Import)
│   └── Select Filters (optional)
├── Query by Country/Region
│   ├── Select Partner Country
│   ├── Select Time Period
│   └── Select Product Category
└── Query by Customs Port
    ├── Select Port
    ├── Select Time Period
    └── Select Product/Partner
```

---

## How to Query Data

### Step-by-Step: UN Comtrade Web Query

```
Step 1: Access Query Builder
→ Go to https://comtradeplus.un.org/lab?r=156
   (Pre-filtered for China as reporter)

Step 2: Select Trade Flow
→ Click "Flow" dropdown
→ Select "Exports" (or "Re-exports" if needed)

Step 3: Select Partner Country
→ Click "Partner" field
→ Search and select destination country
→ Or select "All" for global exports

Step 4: Select Product (HS Code)
→ Click "Commodity Code" field
→ Choose classification level:
   • HS 2-digit (broad category, e.g., "84 - Machinery")
   • HS 4-digit (specific heading)
   • HS 6-digit (detailed subheading)
→ Enter or select code

Step 5: Select Time Period
→ Choose "Year" (single or range)
→ For monthly data, select specific months

Step 6: Run Query
→ Click "Preview" for quick view
→ Click "Download" for CSV/Excel export

Step 7: Interpret Results
Columns explained:
• Reporter: Exporting country (China)
• Partner: Importing country
• Trade Value (USD): Export value in US dollars
• Netweight (kg): Quantity in kilograms
• Quantity: Alternative unit (if applicable)
```

### Step-by-Step: China Customs Web Query

```
Step 1: Access English Interface
→ Go to http://stats.customs.gov.cn/indexEn

Step 2: Choose Query Type
→ "Query by HS Code" for product-focused search
→ "Query by Country/Region" for market-focused search
→ "Query by Customs Port" for logistics analysis

Step 3: Set Parameters
For HS Code Query:
→ Select Year and Month (or range)
→ Click HS Code selector
   • Expand chapters (01-97)
   • Select 2-digit chapter
   • Select 4-digit heading
   • Select 6-digit subheading (optional)
→ Select Trade Flow: "Export"
→ Apply additional filters (optional):
   • Trade Mode (General, Processing, etc.)
   • Customs Port
   • Domestic Destination
   • Transport Mode

Step 4: Execute Query
→ Click "Query" button
→ Wait for results (may take 10-30 seconds)

Step 5: Review Results
→ Table shows: HS Code, Description, Unit, Quantity, Value
→ Click column headers to sort
→ Use pagination for large result sets

Step 6: Export Data
→ Click "Export" or download icon
→ Choose format (Excel/CSV)
→ Save to local drive
```

---

## Data Dictionary

### Common Fields Explained

| Field | Description | Example |
|-------|-------------|---------|
| **HS Code** | Harmonized System product classification | 8517.12 (Phones) |
| **Trade Value** | Export value in US dollars | $1,234,567 |
| **Netweight** | Weight in kilograms | 50,000 kg |
| **Quantity** | Product-specific unit (if different from kg) | 10,000 units |
| **Trade Flow** | Direction of trade (Export/Import/Re-export) | Export |
| **Reporter** | Country reporting the data | China |
| **Partner** | Trading partner country | United States |
| **Customs Port** | Chinese port of departure | Shanghai |
| **Trade Mode** | Type of trade arrangement | General Trade |

### HS Code Structure

```
HS Code Hierarchy Example (Electronics):

85          ← Chapter (2-digit): Electrical machinery
  ↓
8517        ← Heading (4-digit): Telephone sets
  ↓
8517.12     ← Subheading (6-digit): Phones for cellular networks
  ↓
8517.12.00  ← Full code (8-digit): Detailed classification

Where to find HS codes:
• https://www.trade.gov/harmonized-system-hs-codes
• https://www.foreign-trade.com/reference/hscode.htm
• China Customs website HS code lookup
```

---

## Query Examples

### Example 1: China's Laptop Exports to USA (2023)

```
UN Comtrade Query:
├── Reporter: China (156)
├── Partner: United States (842)
├── Flow: Exports (2)
├── HS Code: 8471.30 (Laptops)
└── Period: 2023

China Customs Query:
├── HS Code: 8471.30
├── Trade Flow: Export
├── Partner: United States
└── Period: 2023
```

### Example 2: China's Top Export Products (Latest Month)

```
China Customs Query:
├── Query Type: Top Products
├── Trade Flow: Export
├── Period: Latest available month
└── Result: Sorted by trade value
```

### Example 3: China's Exports by Port

```
China Customs Query:
├── Query Type: By Customs Port
├── Select Port: All (or specific like Shanghai, Shenzhen)
├── HS Code: Your product
├── Trade Flow: Export
└── Period: Select time range
```

---

## Data Availability & Limitations

### Update Schedule

| Source | Frequency | Typical Lag | Coverage |
|--------|-----------|-------------|----------|
| UN Comtrade | Monthly | 1-3 months | 200+ countries |
| China Customs | Monthly | 1-2 months | China only |

### Known Limitations

| Limitation | Explanation | Workaround |
|------------|-------------|------------|
| Mirror data discrepancies | Partner countries may report different values | Compare both sources, use as range |
| Confidential data suppression | Some transactions not disclosed | Use aggregated categories |
| HS code revisions | Codes change every 5 years | Use concordance tables for historical comparison |
| Transshipment goods | Goods passing through China may be included | Filter by trade mode when possible |

### Data Quality Indicators

| Indicator | Good Quality | Questionable |
|-----------|--------------|--------------|
| Completeness | >95% of expected records | <80% coverage |
| Timeliness | <2 months lag | >6 months lag |
| Consistency | Matches mirror data within 20% | >50% discrepancy |

---

## Troubleshooting Common Issues

### Issue 1: "No data found"

**Possible causes**:
- HS code doesn't exist for selected period
- Too restrictive filters applied
- Data not yet reported

**Solutions**:
- Try broader HS code (2-digit instead of 6-digit)
- Remove optional filters
- Check if data for period is available

### Issue 2: "Query timeout"

**Possible causes**:
- Query too broad (all countries, all products)
- Server load high

**Solutions**:
- Narrow query scope
- Query in smaller batches
- Try during off-peak hours

### Issue 3: Inconsistent values between sources

**Possible causes**:
- Different reporting methodologies
- Timing differences
- Data revisions

**Solutions**:
- Document both values with sources
- Use ranges instead of precise figures
- Check metadata for known issues

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│              CHINA EXPORT DATA - QUICK ACCESS              │
├────────────────────────────────────────────────────────────┤
│ UN COMTRADE                                                │
│ URL: comtradeplus.un.org                                   │
│ Best for: Global comparison, historical data               │
│ API: 100 calls/hour (free)                                 │
├────────────────────────────────────────────────────────────┤
│ CHINA CUSTOMS                                              │
│ URL: stats.customs.gov.cn/indexEn                          │
│ Best for: Official China data, port details                │
│ Update: Monthly (1-2 month lag)                            │
├────────────────────────────────────────────────────────────┤
│ HS CODE LOOKUP                                             │
│ trade.gov/harmonized-system-hs-codes                       │
│ foreign-trade.com/reference/hscode.htm                     │
├────────────────────────────────────────────────────────────┤
│ NEED HELP?                                                 │
│ UN Comtrade: unstats.un.org/wiki/display/comtrade          │
│ China Customs: Contact via website                         │
└────────────────────────────────────────────────────────────┘
```

---

## Output Formats

When retrieving data, you can typically export as:

| Format | Extension | Best For |
|--------|-----------|----------|
| CSV | .csv | Data analysis in Excel, Python, R |
| Excel | .xlsx | Presentation, sharing with stakeholders |
| JSON | .json | API integration, web applications |
| PDF | .pdf | Reports, documentation |

**Recommended**: CSV for analysis, Excel for sharing
