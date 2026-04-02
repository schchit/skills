# Phish Radar Module Reference

Complete module-by-module documentation for the phish-radar actor.

## Core Modules

### src/main.js (Entry Point)
**Purpose:** MCP server entry point and tool router
**Exports:** None (runs as Actor)
**Imports:**
- `apify` - Apify Actor framework
- `./handlers/phishing_detect.js` - phishingDetect()
- `./handlers/domain_trust.js` - domainTrust()
- `./handlers/brand_monitor.js` - brandMonitor()

**Key Functions:**
- `processTool(toolName, input)` - Route requests to handlers
- `main()` - Actor entry point

**Tools Defined:**
1. `phishing_detect` - Check URL/domain for phishing
2. `domain_trust` - Calculate domain trust score
3. `brand_monitor` - Find lookalike domains

---

## Handler Modules

### src/handlers/phishing_detect.js
**Purpose:** Analyze URLs/domains for phishing indicators
**Exports:** `phishingDetect(urlOrDomain)`

**Functions:**
- `phishingDetect(urlOrDomain)` - Main analysis function
  - Returns: { verdict, confidence, phishing_score, signals, action, details }
- `extractDomain(urlOrDomain)` - Parse domain from URL
- `extractTLD(domain)` - Get TLD from domain
- `checkTyposquat(domain)` - Detect brand similarity
- `buildDetailsMessage(verdict, signals, score)` - Human-readable summary

**Signals Analyzed:**
- Typosquatting (Levenshtein distance)
- Homoglyphs (visual similarity)
- Domain age
- SSL certificate type
- MX/SPF/DKIM/DMARC records
- Hosting country
- TLD risk

**Score Algorithm:**
- Typosquat distance 1: +35
- Typosquat distance 2: +25
- Homoglyph: +20
- Suspicious TLD: +15
- Free SSL + typosquat: +15
- No MX + typosquat: +10
- Hosting in RU + typosquat: +10
- Has MX: -5
- Trusted CA: -5

**Verdicts:**
- PHISHING (≥70): Block
- SUSPICIOUS (40-69): Review
- SAFE (<40): Allow

---

### src/handlers/domain_trust.js
**Purpose:** Calculate domain trustworthiness score
**Exports:** `domainTrust(domain)`

**Functions:**
- `domainTrust(domain)` - Main scoring function
  - Returns: { domain, trust_score, trust_level, factors }
- `extractTLD(domain)` - Get TLD
- `categorizeSSLType(cert)` - DV/OV/EV classification
- `analyzeNameservers(nsRecords)` - Reputation analysis

**Factors (100 points max):**
- Email infrastructure: 25 points (MX, SPF, DKIM, DMARC)
- SSL certificate: 20 points (EV > OV > DV)
- TLD reputation: 20 points (legitimate +10, suspicious -15)
- Nameservers: 15 points (known vs cheap)
- DNS records: 5 points (A records present)

**Trust Levels:**
- HIGHLY_TRUSTED (≥80)
- TRUSTED (60-79)
- NEUTRAL (40-59)
- SUSPICIOUS (20-39)
- UNTRUSTED (<20)

---

### src/handlers/brand_monitor.js
**Purpose:** Detect lookalike domains targeting brands
**Exports:** `brandMonitor(brandDomain, limit)`

**Functions:**
- `brandMonitor(brandDomain, limit)` - Find lookalikes
  - Returns: { brand, lookalikes_found, domains[] }
- `extractParts(brandDomain)` - Parse brand name and TLD
- `generateTyposquatCandidates(domain)` - Create variants
  - Single character substitutions (homoglyphs)
  - Deletions
  - Insertions
  - Keyword additions
  - Transpositions
- `generateTLDVariations()` - TLD list for testing
- `assessRisk(original, lookalike, type)` - Risk classification

**Attack Types Detected:**
1. Homoglyph - Visual substitutions
2. Deletion - Missing character
3. Insertion - Added character
4. Keyword_addition - Security words added
5. Transposition - Swapped characters

**Risk Levels:**
- HIGH: Distance 1, homoglyphs, keyword_addition with security words
- MEDIUM: Distance 2, keyword_addition, suspicious TLD
- LOW: Otherwise

---

## Utility Modules

### src/utils/dns_client.js
**Purpose:** DNS queries and SSL certificate inspection
**Exports:**
- `getARecords(domain)` - A records (IPs)
- `getMXRecords(domain)` - Mail server records
- `getNSRecords(domain)` - Nameserver records
- `getTXTRecords(domain)` - Text records
- `hasSPF(domain)` - SPF record detection
- `hasDMARC(domain)` - DMARC record detection
- `hasDKIM(domain)` - DKIM record detection
- `getSSLCertificate(domain, port)` - SSL cert info
- `isLetSEncryptCert(domain)` - Let's Encrypt detection
- `domainExists(domain)` - A record check
- `getReverseDNS(ip)` - Reverse DNS
- `getCNAME(domain)` - CNAME record
- `getSOA(domain)` - SOA record
- `completeDNSCheck(domain)` - All checks at once
- `getCountryFromIP(ip)` - Simplified GeoIP

**Implementation:**
- Node.js `dns/promises` for DNS queries
- `tls` module for SSL connections
- Parallel execution via Promise.all()
- 5-second timeout on SSL connections
- Error handling with graceful defaults

**Return Types:**
- Records: Array of strings
- Booleans: true/false with DNS validation
- Certificate: Object with subject, issuer, dates
- Comprehensive check: Object with all fields

---

### src/utils/levenshtein.js
**Purpose:** String similarity and homoglyph detection
**Exports:**
- `levenshteinDistance(str1, str2)` - Edit distance (0+)
- `similarityScore(str1, str2)` - Percentage (0-100)
- `isHomoglyph(char1, char2)` - Boolean
- `countHomoglyphSubstitutions(original, suspect)` - Count

**Algorithm:**
- Levenshtein: Dynamic programming O(n*m)
- Homoglyph detection: Character-by-character comparison

**Homoglyph Map:**
```
0 ↔ O/o
1 ↔ l/L/I/|
5 ↔ S
8 ↔ B
rn ↔ m
```

**Use Cases:**
- Distance 1 = Strong typosquat indicator
- Distance 2 = Possible typosquat
- Homoglyphs = High-confidence phishing signal

---

## Data Modules

### src/data/known_brands.js
**Purpose:** Database of major brands for typosquat detection
**Exports:**
- `KNOWN_BRANDS` - Object with 80+ domains
- `getBrandInfo(domain)` - Lookup function
- `getAllBrands()` - Return all as array

**Structure:**
```javascript
{
  'domain.com': {
    name: 'Brand Name',
    category: 'category',
    risk_level: 'high|medium|low'
  }
}
```

**Categories:**
- Financial Services (PayPal, Stripe, Square, Banks)
- Tech Companies (Apple, Google, Microsoft, etc.)
- Cryptocurrency (Coinbase, Kraken, Binance)
- Cloud Providers (AWS, Azure, Google Cloud)
- E-commerce (Amazon, eBay, Shopify)
- Communication (Discord, Slack, Zoom)
- Productivity (Dropbox, LastPass)

**Extensibility:**
- Add new brands easily to KNOWN_BRANDS object
- Update categories as needed
- Risk levels guide phishing score calculation

---

### src/data/suspicious_tlds.js
**Purpose:** Database of high-risk TLDs
**Exports:**
- `SUSPICIOUS_TLDS` - Object with 40+ TLDs
- `getTLDRisk(tld)` - Lookup with reason
- `isSuspiciousTLD(tld)` - Boolean check
- `getAllSuspiciousTLDs()` - HIGH risk only

**Structure:**
```javascript
{
  'tld': {
    risk: 'HIGH|MEDIUM|LOW',
    reason: 'explanation'
  }
}
```

**Risk Categories:**

HIGH RISK (abuse-prone):
- Generic: xyz, top, click, bid, download, trade
- Free: tk, ml, ga, cf
- Sanctioned: ru, su, ir, kp, sy
- Cryptocurrency: btc, eth, crypto

MEDIUM RISK:
- pw, cc, ws

LOW RISK:
- Legitimate extensions (io, app, dev, cloud)
- Country codes (de, ch, nl)

**Usage:**
- Adds 15 points to phishing score if HIGH
- Subtracts 15 points from trust score
- Used in brand monitoring risk assessment

---

## Integration Flow

```
User Request (HTTP/JSON)
         ↓
    main.js (Router)
         ↓
   processTool()
    /    |    \
   /     |     \
phishing_detect  domain_trust  brand_monitor
   |                |                |
   ↓                ↓                ↓
[Parallel DNS Queries via dns_client.js]
   |                |                |
   ↓                ↓                ↓
[String Analysis via levenshtein.js]
   |                |                |
   ↓                ↓                ↓
[Data Lookup via known_brands.js & suspicious_tlds.js]
   |                |                |
   ↓                ↓                ↓
[Score Calculation & Risk Assessment]
   |                |                |
   ↓                ↓                ↓
JSON Response with Results
```

---

## Performance Characteristics

### Time Complexity
- Levenshtein distance: O(n*m) where n,m = string lengths
- Brand checking: O(brands × strings) = O(80 × 2) = O(160)
- Typosquat generation: O(domain_length)
- DNS checks: O(1) per record type (parallel)

### Space Complexity
- Known brands: O(80 domains)
- Suspicious TLDs: O(40 TLDs)
- Typosquat candidates: O(domain_length^2)
- DNS records: O(number of records)

### Response Times
- Phishing detect: 2-5s (includes DNS + SSL)
- Domain trust: 1-3s (DNS only)
- Brand monitor (20 domains): 8-15s (batch DNS)

---

## Testing Imports

All modules have been tested for import compatibility:
```
✅ phishing_detect.js
✅ domain_trust.js
✅ brand_monitor.js
✅ dns_client.js
✅ levenshtein.js
✅ known_brands.js
✅ suspicious_tlds.js
```

No circular dependencies.
All ES module imports validated.

---

## Future Module Additions

Possible future modules:
1. `whois_client.js` - WHOIS lookups for domain age
2. `geoip_client.js` - MaxMind integration for IP location
3. `reputation_client.js` - Integration with phishing/malware DBs
4. `certificate_transparency.js` - CT log queries
5. `machine_learning.js` - Pattern recognition

