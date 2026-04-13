#!/usr/bin/env python3
"""
IP geolocation client module.
Queries multiple IP geolocation APIs for location.
"""

import json
import sys
import urllib.request
import urllib.error
import ssl
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class IPLocation:
    """IP geolocation result."""
    ip: str
    latitude: float
    longitude: float
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    isp: Optional[str] = None
    org: Optional[str] = None
    timezone: Optional[str] = None
    accuracy: float = 5000.0  # meters
    source: str = 'unknown'


def get_ip_location() -> Optional[IPLocation]:
    """
    Get location from IP address using multiple APIs.
    Queries several APIs and returns the most reliable result.
    """
    apis = [
        _query_ip_api_com,
        _query_ipinfo_io,
        _query_ipgeolocation,
        _query_ipwhois,
    ]
    
    results = []
    
    for api_func in apis:
        try:
            result = api_func()
            if result:
                results.append(result)
        except Exception as e:
            print(f"API {api_func.__name__} failed: {e}", file=sys.stderr)
    
    if not results:
        return None
    
    # If multiple results, use the one with smallest claimed accuracy
    # or cross-validate if they agree
    if len(results) == 1:
        return results[0]
    
    # Check if results agree (within 50km)
    valid_results = []
    for r in results:
        # Check against first result
        dist = _haversine_distance(
            results[0].latitude, results[0].longitude,
            r.latitude, r.longitude
        )
        if dist < 50000:  # 50km
            valid_results.append(r)
    
    if valid_results:
        # Return the one with best accuracy claim
        return min(valid_results, key=lambda x: x.accuracy)
    
    # Results disagree, return the one with smallest accuracy
    return min(results, key=lambda x: x.accuracy)


def _query_ip_api_com() -> Optional[IPLocation]:
    """
    Query ip-api.com (free, no key required, 45 req/min).
    
    Response:
    {
      "status": "success",
      "country": "United States",
      "countryCode": "US",
      "region": "CA",
      "regionName": "California",
      "city": "Mountain View",
      "lat": 37.386,
      "lon": -122.0838,
      "isp": "Google LLC",
      "org": "Google LLC",
      "timezone": "America/Los_Angeles"
    }
    """
    url = "http://ip-api.com/json/"
    
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'multi-source-locate/1.0'}
        )
        
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            if data.get('status') != 'success':
                return None
            
            return IPLocation(
                ip=data.get('query', ''),
                latitude=float(data['lat']),
                longitude=float(data['lon']),
                city=data.get('city'),
                region=data.get('regionName'),
                country=data.get('country'),
                country_code=data.get('countryCode'),
                isp=data.get('isp'),
                org=data.get('org'),
                timezone=data.get('timezone'),
                accuracy=5000.0,  # ~5km typical
                source='ip-api.com'
            )
    except Exception:
        return None


def _query_ipinfo_io() -> Optional[IPLocation]:
    """
    Query ipinfo.io (free tier: 50k req/month).
    
    Response:
    {
      "ip": "8.8.8.8",
      "hostname": "dns.google",
      "city": "Mountain View",
      "region": "California",
      "country": "US",
      "loc": "37.386,-122.0838",
      "org": "AS15169 Google LLC",
      "timezone": "America/Los_Angeles"
    }
    """
    url = "https://ipinfo.io/json"
    
    # Check for API key
    api_key = os.environ.get('IPINFO_API_KEY')
    if api_key:
        url = f"https://ipinfo.io/json?token={api_key}"
    
    try:
        ctx = ssl.create_default_context()
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'multi-source-locate/1.0'}
        )
        
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            if 'loc' not in data:
                return None
            
            lat, lon = map(float, data['loc'].split(','))
            
            # Parse org for ISP
            org = data.get('org', '')
            isp = org.split(' ', 1)[1] if ' ' in org else org
            
            return IPLocation(
                ip=data.get('ip', ''),
                latitude=lat,
                longitude=lon,
                city=data.get('city'),
                region=data.get('region'),
                country_code=data.get('country'),
                isp=isp,
                org=org,
                timezone=data.get('timezone'),
                accuracy=10000.0,  # ~10km
                source='ipinfo.io'
            )
    except Exception:
        return None


def _query_ipgeolocation() -> Optional[IPLocation]:
    """
    Query ipgeolocation.io (free tier: 30k req/month).
    
    Response:
    {
      "ip": "8.8.8.8",
      "latitude": "37.38600",
      "longitude": "-122.08380",
      "city": "Mountain View",
      "state_prov": "California",
      "country_name": "United States",
      "country_code2": "US",
      "isp": "Google LLC",
      "time_zone": {"name": "America/Los_Angeles"}
    }
    """
    # Free API key for basic usage
    api_key = os.environ.get('IPGEOLOCATION_API_KEY', 'free')
    url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}"
    
    try:
        ctx = ssl.create_default_context()
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'multi-source-locate/1.0'}
        )
        
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            lat = data.get('latitude')
            lon = data.get('longitude')
            
            if lat is None or lon is None:
                return None
            
            tz = data.get('time_zone', {})
            
            return IPLocation(
                ip=data.get('ip', ''),
                latitude=float(lat),
                longitude=float(lon),
                city=data.get('city'),
                region=data.get('state_prov'),
                country=data.get('country_name'),
                country_code=data.get('country_code2'),
                isp=data.get('isp'),
                org=data.get('organization'),
                timezone=tz.get('name') if isinstance(tz, dict) else None,
                accuracy=8000.0,
                source='ipgeolocation.io'
            )
    except Exception:
        return None


def _query_ipwhois() -> Optional[IPLocation]:
    """
    Query ipwhois.app (free, no key required).
    
    Response:
    {
      "ip": "8.8.8.8",
      "city": "Mountain View",
      "region": "California",
      "country": "US",
      "country_name": "United States",
      "latitude": 37.386,
      "longitude": -122.0838,
      "isp": "Google LLC",
      "timezone": "America/Los_Angeles"
    }
    """
    url = "https://ipwhois.app/json/"
    
    try:
        ctx = ssl.create_default_context()
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'multi-source-locate/1.0'}
        )
        
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            if 'latitude' not in data or 'longitude' not in data:
                return None
            
            return IPLocation(
                ip=data.get('ip', ''),
                latitude=float(data['latitude']),
                longitude=float(data['longitude']),
                city=data.get('city'),
                region=data.get('region'),
                country=data.get('country_name'),
                country_code=data.get('country'),
                isp=data.get('isp'),
                timezone=data.get('timezone'),
                accuracy=7000.0,
                source='ipwhois.app'
            )
    except Exception:
        return None


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in meters using Haversine formula."""
    import math
    
    R = 6371000  # Earth radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def get_public_ip() -> Optional[str]:
    """Get the public IP address."""
    services = [
        "https://api.ipify.org",
        "https://icanhazip.com",
        "https://ifconfig.me/ip",
    ]
    
    for url in services:
        try:
            ctx = ssl.create_default_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'curl'})
            with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
                return resp.read().decode('utf-8').strip()
        except Exception:
            continue
    
    return None


if __name__ == '__main__':
    print("Getting IP location...\n")
    
    ip = get_public_ip()
    if ip:
        print(f"Public IP: {ip}\n")
    
    location = get_ip_location()
    
    if location:
        print(f"Location from {location.source}:")
        print(f"  Coordinates: {location.latitude:.4f}, {location.longitude:.4f}")
        print(f"  City: {location.city or 'N/A'}")
        print(f"  Region: {location.region or 'N/A'}")
        print(f"  Country: {location.country or 'N/A'} ({location.country_code or 'N/A'})")
        print(f"  ISP: {location.isp or 'N/A'}")
        print(f"  Timezone: {location.timezone or 'N/A'}")
        print(f"  Accuracy: ~{location.accuracy/1000:.0f} km")
    else:
        print("Failed to get IP location")
