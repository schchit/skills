---
name: multi-source-locate
description: Multi-source geolocation via GPS, System built-in, IP, WiFi, and cellular triangulation. Use when the user asks to determine their location, locate a device, get current coordinates, or needs accurate positioning using multiple data sources. Supports GPS (high accuracy), System built-in location (Windows GeoCoordinateWatcher / macOS CoreLocation / Linux GeoClue2), IP geolocation (city-level), WiFi positioning (indoor/urban), and cellular tower triangulation (outdoor fallback). Provides confidence scores and accuracy estimates for each method. Also used as the location backend for the locate-weather Skill.
---

# Multi-Source Locate

Multi-source geolocation combining GPS, System built-in, IP, WiFi, and cellular data for accurate positioning with confidence scoring.

> **Used by**: `locate-weather` Skill — provides the geolocation engine for its "fixed-point weather forecast" feature.

## When to Use

- User asks "where am I" or "get my location"
- Need device coordinates with accuracy estimate
- GPS unavailable or inaccurate (indoor, urban canyon)
- Cross-validate location from multiple sources
- Fallback positioning when primary method fails

## Quick Start

```bash
# Get location using all available methods (default order: gps, system, ip, wifi, cellular)
python scripts/locate.py

# Use specific method(s)
python scripts/locate.py --method gps
python scripts/locate.py --method system
python scripts/locate.py --method ip
python scripts/locate.py --method wifi
python scripts/locate.py --method gps,system,ip,wifi

# Output format
python scripts/locate.py --format json    # machine-readable
python scripts/locate.py --format text    # human-readable
```

## Location Methods

### 1. GPS (Highest Accuracy)

- **Accuracy**: 3-10m outdoors, degraded indoors
- **Requirements**: GPS hardware, sky visibility
- **Best for**: Outdoor navigation, mapping
- **Fallback**: WiFi positioning indoors

```bash
python scripts/locate.py --method gps --timeout 30
```

### 2. System Built-in Location

- **Accuracy**: 10m–1km (OS-dependent)
- **Requirements**: OS location service enabled, user permission
- **Best for**: Reliable OS-managed indoor/outdoor location without API keys
- **Platforms**: Windows (GeoCoordinateWatcher), macOS (CoreLocation), Linux (GeoClue2)

```bash
python scripts/locate.py --method system --timeout 20
```

### 3. IP Geolocation (City-Level)

- **Accuracy**: 1-50km (varies by ISP)
- **Requirements**: Internet connection
- **Best for**: Quick city/country detection
- **Data sources**: Multiple IP geolocation APIs with cross-validation

```bash
python scripts/locate.py --method ip
```

### 4. WiFi Positioning (Indoor/Urban)

- **Accuracy**: 10-100m
- **Requirements**: WiFi adapter, nearby APs
- **Best for**: Indoor, urban environments
- **Method**: BSSID lookup via geolocation APIs

```bash
python scripts/locate.py --method wifi
```

### 5. Cellular Triangulation (Fallback)

- **Accuracy**: 100m-3km
- **Requirements**: Cell modem, tower visibility
- **Best for**: Rural areas, GPS denied
- **Method**: MCC/MNC/LAC/CellID lookup

```bash
python scripts/locate.py --method cellular
```

## Triangulation Algorithm

When multiple methods are available, the skill:

1. Collects coordinates from each successful method
2. Weights by inverse variance (accuracy-based weighting)
3. Computes weighted centroid as final position
4. Estimates combined accuracy from residual dispersion
5. Reports confidence score (0-100%)

### Output Format

```json
{
  "latitude": 39.9042,
  "longitude": 116.4074,
  "accuracy_meters": 15,
  "confidence": 0.92,
  "method": "triangulated",
  "sources": {
    "gps": {"lat": 39.9045, "lon": 116.4071, "accuracy": 5, "weight": 0.6},
    "wifi": {"lat": 39.9039, "lon": 116.4078, "accuracy": 30, "weight": 0.3},
    "ip": {"lat": 39.9042, "lon": 116.4074, "accuracy": 5000, "weight": 0.1}
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## API Keys (Optional)

For enhanced accuracy, configure API keys in environment:

```bash
# Google Geolocation API (WiFi/Cellular)
export GOOGLE_GEOLOCATION_API_KEY="your-key"

# Mozilla Location Service
export MLS_API_KEY="your-key"

# Unwired Labs
export UNWIRED_API_KEY="your-key"
```

Without API keys, the skill uses:
- Free IP geolocation APIs (ip-api.com, ipinfo.io)
- Local GPS via serial/Bluetooth NMEA
- Public BSSID databases where available

## Platform Notes

### Windows
- **System**: Uses `[System.Device.Location.GeoCoordinateWatcher]` via PowerShell (Wi-Fi + IP + GPS fusion, 10m–1km)
- GPS: Requires USB/Bluetooth GPS receiver or NMEA source
- WiFi: Uses `netsh wlan show networks mode=bssid`
- Cellular: Requires cellular modem AT command access

### macOS
- **System**: CoreLocation via `locationd` daemon (approximate via `system_profiler`)
- GPS: Uses CoreLocation framework
- WiFi: Uses `airport -s` for BSSID scanning
- Cellular: Limited on desktop, full on iPhone

### Linux
- **System**: Queries `org.freedesktop.GeoClue2` via D-Bus (Wi-Fi + cell fusion)
- GPS: Reads from `/dev/ttyUSB*` or gpsd
- WiFi: Uses `iwlist scan` or NetworkManager
- Cellular: Uses ModemManager AT interface

## Resources

### scripts/
- `locate.py` - Main location acquisition script
- `gps_reader.py` - NMEA GPS parser
- `wifi_scanner.py` - WiFi BSSID collector
- `cell_scanner.py` - Cellular tower info collector
- `ip_lookup.py` - IP geolocation client
- `triangulate.py` - Weighted centroid calculation

### references/
- `nmea_sentences.md` - NMEA sentence format reference
- `api_endpoints.md` - Geolocation API documentation
