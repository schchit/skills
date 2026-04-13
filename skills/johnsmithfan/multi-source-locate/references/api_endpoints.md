# Geolocation API Endpoints

Reference for geolocation APIs used by multi-source-locate.

## IP Geolocation APIs

### ip-api.com

Free, no API key required.

- **Endpoint**: `http://ip-api.com/json/`
- **Rate Limit**: 45 requests/minute (free)
- **Accuracy**: ~5km typical

**Request:**
```
GET http://ip-api.com/json/
```

**Response:**
```json
{
  "status": "success",
  "country": "United States",
  "countryCode": "US",
  "region": "CA",
  "regionName": "California",
  "city": "Mountain View",
  "zip": "94035",
  "lat": 37.386,
  "lon": -122.0838,
  "timezone": "America/Los_Angeles",
  "isp": "Google LLC",
  "org": "Google LLC",
  "as": "AS15169 Google LLC",
  "query": "8.8.8.8"
}
```

### ipinfo.io

Free tier available.

- **Endpoint**: `https://ipinfo.io/json`
- **Rate Limit**: 50,000 requests/month (free)
- **Accuracy**: ~10km

**Request:**
```
GET https://ipinfo.io/json?token=YOUR_TOKEN
```

**Response:**
```json
{
  "ip": "8.8.8.8",
  "hostname": "dns.google",
  "city": "Mountain View",
  "region": "California",
  "country": "US",
  "loc": "37.386,-122.0838",
  "org": "AS15169 Google LLC",
  "postal": "94035",
  "timezone": "America/Los_Angeles"
}
```

### ipgeolocation.io

Free tier available.

- **Endpoint**: `https://api.ipgeolocation.io/ipgeo`
- **Rate Limit**: 30,000 requests/month (free)
- **Accuracy**: ~8km

**Request:**
```
GET https://api.ipgeolocation.io/ipgeo?apiKey=YOUR_KEY
```

**Response:**
```json
{
  "ip": "8.8.8.8",
  "latitude": "37.38600",
  "longitude": "-122.08380",
  "city": "Mountain View",
  "state_prov": "California",
  "country_name": "United States",
  "country_code2": "US",
  "isp": "Google LLC",
  "time_zone": {
    "name": "America/Los_Angeles"
  }
}
```

## WiFi/Cellular Geolocation APIs

### Google Geolocation API

Most accurate, requires API key and billing.

- **Endpoint**: `https://www.googleapis.com/geolocation/v1/geolocate`
- **Cost**: $5 per 1000 requests (after free tier)
- **Accuracy**: 10-100m (WiFi), 100m-3km (cellular)

**WiFi Request:**
```json
POST https://www.googleapis.com/geolocation/v1/geolocate?key=YOUR_KEY

{
  "wifiAccessPoints": [
    {
      "macAddress": "01:23:45:67:89:AB",
      "signalStrength": -43,
      "channel": 11
    },
    {
      "macAddress": "01:23:45:67:89:CD",
      "signalStrength": -57
    }
  ]
}
```

**Cellular Request:**
```json
{
  "cellTowers": [
    {
      "cellId": 42,
      "locationAreaCode": 415,
      "mobileCountryCode": 310,
      "mobileNetworkCode": 260,
      "age": 0,
      "signalStrength": -60,
      "timingAdvance": 15
    }
  ]
}
```

**Response:**
```json
{
  "location": {
    "lat": 37.4218,
    "lng": -122.0840
  },
  "accuracy": 30.0
}
```

### Unwired Labs (unwiredlabs.com)

Free tier available, good for WiFi positioning.

- **Endpoint**: `https://us1.unwiredlabs.com/v2/process.php`
- **Rate Limit**: 10,000 requests/day (free)
- **Accuracy**: 30-300m

**Request:**
```json
POST https://us1.unwiredlabs.com/v2/process.php

{
  "token": "YOUR_TOKEN",
  "wifi": [
    {
      "bssid": "01:23:45:67:89:AB",
      "signal": -43
    }
  ],
  "cell": [
    {
      "mcc": 310,
      "mnc": 260,
      "lac": 415,
      "cid": 42
    }
  ]
}
```

**Response:**
```json
{
  "status": "ok",
  "lat": 37.4218,
  "lon": -122.0840,
  "accuracy": 50,
  "fallback": "wifi"
}
```

### Mozilla Location Service (MLS)

**Note**: Mozilla shut down MLS in 2024. This is kept for reference.

Historically provided free WiFi/cellular geolocation using crowdsourced data.

## Combining Sources

### Accuracy Comparison

| Source | Typical Accuracy | Best For |
|--------|------------------|----------|
| GPS | 3-10m | Outdoor, clear sky |
| WiFi | 10-100m | Indoor, urban |
| Cellular | 100m-3km | Rural, GPS denied |
| IP | 1-50km | Quick city detection |

### Weight Calculation

Use inverse variance weighting:

```python
weight = 1.0 / (accuracy ** 2)
```

This gives higher weight to more accurate sources.

### Confidence Scoring

Factors affecting confidence:

1. **Number of sources**: More = higher confidence
2. **Agreement**: Sources agreeing = higher confidence
3. **Source quality**: GPS > WiFi > Cellular > IP
4. **Accuracy**: Lower accuracy value = higher confidence

## Rate Limits Summary

| API | Free Tier | Paid Tier |
|-----|-----------|-----------|
| ip-api.com | 45/min | $13/mo for unlimited |
| ipinfo.io | 50k/mo | $249/mo for 1M |
| ipgeolocation.io | 30k/mo | $15/mo for 150k |
| Google Geolocation | $200 credit/mo | $5/1k requests |
| Unwired Labs | 10k/day | Custom |

## Error Handling

### Common Errors

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 429 | Rate limited | Wait and retry |
| 403 | Invalid API key | Check credentials |
| 400 | Bad request | Validate payload |
| 404 | Not found | Check endpoint |
| 503 | Service unavailable | Fallback to other API |

### Fallback Chain

1. Try primary API
2. If rate limited, try secondary API
3. If all fail, return cached result (if available)
4. If no cache, return error with partial results
