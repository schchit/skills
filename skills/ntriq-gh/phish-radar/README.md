# Phish Radar - Phishing Detection & Brand Monitoring MCP Server

Real-time phishing detection and brand monitoring system for AI agents. Analyzes URLs and domains for phishing indicators, typosquatting, homoglyphs, and lookalike domains.

## Features

### 1. **Phishing Detection** (`phishing_detect`)
Comprehensive URL/domain analysis with:
- **Typosquatting detection** - Identifies domains similar to known brands (Levenshtein distance)
- **Homoglyph detection** - Catches visually similar character substitutions (0/O, 1/l/I, etc.)
- **Domain age analysis** - Detects recently registered suspicious domains
- **SSL certificate inspection** - Flags free certificates (Let's Encrypt) when combined with brand similarity
- **DNS records** - Checks for MX, SPF, DKIM, DMARC records
- **Hosting location** - Identifies suspicious geography patterns

**Score: 0-100 phishing confidence**
- **PHISHING (70+)**: Block immediately
- **SUSPICIOUS (40-69)**: Review recommended
- **SAFE (<40)**: Low risk

### 2. **Domain Trust Score** (`domain_trust`)
Evaluates domain trustworthiness (0-100) based on:
- Email infrastructure (MX, SPF, DKIM, DMARC) - 25 points
- SSL certificate type (EV > OV > DV) - 20 points
- TLD reputation - 20 points
- Nameserver reputation - 15 points
- DNS records - 5 points

**Levels:**
- **HIGHLY_TRUSTED (80+)**: Enterprise-grade domain
- **TRUSTED (60-79)**: Legitimate domain
- **NEUTRAL (40-59)**: Unproven domain
- **SUSPICIOUS (20-39)**: Warning signs present
- **UNTRUSTED (<20)**: High-risk domain

### 3. **Brand Monitor** (`brand_monitor`)
Detects lookalike domains targeting your brand:
- **Typosquats** - Single character swaps/deletions (paypa1.com vs paypal.com)
- **Homoglyphs** - Visually confusing substitutions
- **Keyword additions** - Security-related additions (paypal-secure.com)
- **TLD variations** - Same domain on different extensions (paypal.xyz)

Returns high-risk domains that actually exist with full risk assessment.

## Usage

### Example 1: Check a Suspicious URL
```json
{
  "toolName": "phishing_detect",
  "input": {
    "url": "https://paypa1-secure.com/login"
  }
}
```

**Response:**
```json
{
  "url": "https://paypa1-secure.com/login",
  "domain": "paypa1-secure.com",
  "verdict": "PHISHING",
  "confidence": 0.97,
  "phishing_score": 94,
  "signals": {
    "typosquat_of": "paypal.com",
    "typosquat_distance": 1,
    "homoglyph_detected": true,
    "homoglyph_count": 1,
    "domain_age_days": 3,
    "ssl_issuer": "Let's Encrypt",
    "ssl_free_cert": true,
    "has_mx_records": false,
    "suspicious_tld": false,
    "dns_a_records": ["185.234.xx.xx"],
    "hosting_country": "RU"
  },
  "action": "BLOCK",
  "details": "High-confidence phishing domain detected (score: 94). Domain is a typosquat of paypal.com (distance: 1). Contains 1 homoglyph character substitution. Uses free SSL certificate (Let's Encrypt) - commonly abused. No MX records configured - not set up for legitimate email."
}
```

### Example 2: Check Domain Trust
```json
{
  "toolName": "domain_trust",
  "input": {
    "domain": "stripe.com"
  }
}
```

**Response:**
```json
{
  "domain": "stripe.com",
  "trust_score": 92,
  "trust_level": "HIGHLY_TRUSTED",
  "factors": {
    "domain_age_days": null,
    "has_mx": true,
    "has_spf": true,
    "has_dkim": true,
    "has_dmarc": true,
    "ssl_type": "EV",
    "ssl_issuer": "DigiCert",
    "has_ssl": true,
    "tld_risk": "LOW",
    "nameservers": ["ns1.stripe.com", "ns2.stripe.com"],
    "a_records_count": 4
  }
}
```

### Example 3: Monitor Brand Lookalikes
```json
{
  "toolName": "brand_monitor",
  "input": {
    "brand_domain": "stripe.com",
    "limit": 10
  }
}
```

**Response:**
```json
{
  "brand": "stripe.com",
  "brand_name": "stripe",
  "lookalikes_found": 8,
  "domains": [
    {
      "domain": "str1pe.com",
      "exists": true,
      "risk": "HIGH",
      "type": "homoglyph",
      "tld_risk": "LOW"
    },
    {
      "domain": "stripe-secure.com",
      "exists": true,
      "risk": "HIGH",
      "type": "keyword_addition",
      "tld_risk": "LOW"
    },
    {
      "domain": "stripee.com",
      "exists": true,
      "risk": "MEDIUM",
      "type": "insertion",
      "tld_risk": "LOW"
    }
  ],
  "analysis_time_ms": 2847
}
```

## Implementation Details

### No External API Dependencies
- **DNS Queries**: Native Node.js `dns/promises` module
- **SSL Certificates**: Node.js `tls` module for direct connections
- **WHOIS**: Direct TCP port 43 protocol (future enhancement)
- **GeoIP**: Simplified IP-to-country mapping (for production, integrate MaxMind)

### Known Brands Database
Includes 80+ major brands across:
- Financial Services (PayPal, Stripe, Square, etc.)
- Tech Companies (Apple, Google, Microsoft, etc.)
- Cryptocurrency (Coinbase, Kraken, Binance, etc.)
- Cloud Providers (AWS, Azure, Google Cloud, etc.)
- E-commerce (Amazon, eBay, Shopify, etc.)

Easily extensible in `src/data/known_brands.js`.

### Suspicious TLDs
Monitors 40+ high-risk TLDs commonly used in phishing:
- Cheap registration TLDs: `.xyz`, `.top`, `.click`, `.bid`
- Free TLDs: `.tk`, `.ml`, `.ga`, `.cf`
- Cryptocurrency scams: `.btc`, `.eth`, `.crypto`
- Sanctioned regions: `.ru`, `.ir`, `.kp`

## Phishing Score Calculation

### High-Risk Signals (Add Points)
- Typosquat distance 1: +35 points
- Typosquat distance 2: +25 points
- Homoglyph detected: +20 points
- Suspicious TLD: +15 points
- Free SSL + typosquat: +15 points
- No MX + typosquat: +10 points
- Hosting in RU + typosquat: +10 points

### Low-Risk Signals (Subtract Points)
- Has MX records: -5 points
- Trusted CA cert: -5 points

**Final Score Clamped: 0-100**

## Confidence Levels

- **70+ (PHISHING)**: 0.70-0.99 confidence → **BLOCK**
- **40-69 (SUSPICIOUS)**: 0.50-0.95 confidence → **REVIEW**
- **<40 (SAFE)**: 0.95+ confidence → **ALLOW**

## Pricing

- **$0.05 per tool call** (per domain/URL analyzed)
- Bulk monitoring: $0.05 × number of domains checked

Example: Monitoring 100 brand lookalikes = $5.00 per execution

## Implementation Notes

### Security Considerations
- **No WHOIS PII collection**: Personal information (owner names, emails) excluded per GDPR
- **No certificate validation bypass**: Uses system trust stores
- **Rate limiting**: Implement externally to avoid DNS query floods
- **Timeout protection**: 5-second SSL connection timeout

### Performance
- Parallel DNS queries for speed
- Batch processing for large domain lists (10 concurrent)
- Caching at application level (not in Actor)

### Future Enhancements
1. **WHOIS Integration**: For domain registration date analysis
2. **GeoIP Database**: MaxMind for accurate IP location
3. **SSL Certificate History**: Certificate Transparency logs
4. **Reputation Scoring**: Integration with Phishing/Malware databases
5. **Machine Learning**: Pattern recognition for new phishing techniques

## API Signature

All tools follow MCP standard with JSON input/output.

### Tool Request Format
```json
{
  "toolName": "phishing_detect|domain_trust|brand_monitor",
  "input": {
    // tool-specific inputs
  }
}
```

### Error Response
```json
{
  "error": "Error description",
  "tool": "tool_name"
}
```

## Testing

```bash
# Local testing
npm install
node src/main.js

# With Apify SDK (when deployed)
apify call phish-radar --input input.json
```

## Maintenance

- Update `known_brands.js` quarterly with emerging platforms
- Monitor `suspicious_tlds.js` for new high-abuse extensions
- Review phishing signal weights annually based on threat patterns

## Support

For brand additions or TLD updates, modify:
- Brand list: `src/data/known_brands.js`
- TLD list: `src/data/suspicious_tlds.js`

---

**Version**: 1.0
**Node.js**: 18+
**License**: Private (ntriq)
