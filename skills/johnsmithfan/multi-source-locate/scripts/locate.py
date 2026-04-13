#!/usr/bin/env python3
"""
Multi-source geolocation tool.
Combines GPS, IP, WiFi, and cellular positioning for accurate location.
"""

import argparse
import json
import sys
import time
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import subprocess
import urllib.request
import urllib.error
import ssl


@dataclass
class LocationResult:
    """Single source location result."""
    latitude: float
    longitude: float
    accuracy: float  # meters
    method: str
    weight: float = 0.0
    timestamp: str = ""
    raw_data: Optional[Dict[str, Any]] = None


# ─── SYSTEM LOCATION (Windows / macOS built-in) ──────────────────────────────

def get_system_location(timeout: int = 20) -> Optional[LocationResult]:
    """Get location from OS built-in location service.
    
    Windows:  PowerShell [System.Device.Location.GeoCoordinateWatcher]
    macOS:    CoreLocation through system_profiler / defaults
    Linux:    geoclue2 via dbus
    """
    if sys.platform == 'win32':
        return _get_windows_system_location(timeout)
    elif sys.platform == 'darwin':
        return _get_macos_system_location(timeout)
    else:
        return _get_linux_geoclue_location(timeout)


def _get_windows_system_location(timeout: int) -> Optional[LocationResult]:
    """Use Windows GeoCoordinateWatcher via PowerShell script file."""
    import tempfile, os as _os

    ps_script = (
        "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n"
        "Add-Type -AssemblyName System.Device.Location\n"
        f"$watcher = [System.Device.Location.GeoCoordinateWatcher]::new()\n"
        f"$watcher.TryStart($false, {timeout * 1000})\n"
        "$sw = [Diagnostics.Stopwatch]::StartNew()\n"
        "while ($watcher.Position -eq $null -and $sw.ElapsedMilliseconds -lt "
        f"{timeout * 1000}) {{ Start-Sleep -Milliseconds 200 }}\n"
        "$pos = $watcher.Position\n"
        "if ($pos -ne $null -and -not $pos.Location.IsUnknown) {\n"
        "    $lat = $pos.Location.Latitude\n"
        "    $lon = $pos.Location.Longitude\n"
        "    $acc = $pos.Location.HorizontalAccuracy\n"
        "    if ($acc -le 0) { $acc = 100 }\n"
        '    Write-Output "$lat|$lon|$acc"\n'
        "} else {\n"
        '    Write-Output "UNKNOWN"\n'
        "}\n"
        "$watcher.Stop()\n"
    )

    # Write to temp file to avoid quote/escape issues
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(suffix='.ps1')
        os_fd = _os.fdopen(fd, 'w', encoding='utf-8')
        os_fd.write(ps_script)
        os_fd.close()

        result = subprocess.run(
            ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
             '-File', tmp],
            capture_output=True,
            text=True,
            timeout=timeout + 5,
            encoding='utf-8',
            errors='ignore'
        )
        output = result.stdout.strip()
        if output and output != 'UNKNOWN':
            parts = output.split('|')
            if len(parts) >= 3 and parts[0] and parts[1] and parts[2]:
                lat = float(parts[0])
                lon = float(parts[1])
                acc = float(parts[2])
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return LocationResult(
                        latitude=lat, longitude=lon,
                        accuracy=acc, method='system',
                        timestamp=datetime.now(timezone.utc).isoformat()
                    )
    except Exception as e:
        print(f"System location (Windows) failed: {e}", file=sys.stderr)
    finally:
        if tmp and _os.path.exists(tmp):
            _os.unlink(tmp)
    return None


def _get_macos_system_location(timeout: int) -> Optional[LocationResult]:
    """Use macOS CoreLocation via osascript / system_profiler."""
    # Try cllocationd via launchctl
    try:
        result = subprocess.run(
            ['system_profiler', 'SPBluetoothDataType', '-json'],
            capture_output=True, text=True, encoding='utf-8', timeout=10
        )
    except Exception:
        pass
    
    # Fallback: use curl to Apple's location service (approximate)
    try:
        result = subprocess.run(
            ['curl', '-s', '--max-time', '5',
             'https://captive.apple.com/generation_204'],
            capture_output=True, text=True, encoding='utf-8', timeout=7
        )
        # macOS can get location from network in some configs
        # Check headers for location
        for line in result.stdout.splitlines():
            if 'x-apple-rawl' in line.lower() or 'x-geo' in line.lower():
                pass  # parse if found
    except Exception:
        pass
    
    return None


def _get_linux_geoclue_location(timeout: int) -> Optional[LocationResult]:
    """Query geoclue2 over D-Bus for system location (Linux)."""
    lat, lon = None, None

    # Try dbus-send to query GeoClue2 Manager
    try:
        result = subprocess.run(
            ['dbus-send', '--session', '--dest=org.freedesktop.GeoClue2',
             '--print-reply', '--type=method_call',
             '/org/freedesktop/GeoClue2/Manager',
             'org.freedesktop.GeoClue2.Manager.GetClient'],
            capture_output=True, text=True, timeout=timeout, encoding='utf-8'
        )
        # Parse latitude/longitude from dbus output
        for line in result.stdout.splitlines():
            if 'double' in line.lower():
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        val = float(parts[-1])
                        if -90 <= val <= 90:
                            lat = val
                        elif -180 <= val <= 180:
                            lon = val
                    except ValueError:
                        continue
    except Exception:
        pass

    if lat is not None and lon is not None:
        lat, lon = validate_coordinates(lat, lon)
        if lat is not None:
            return LocationResult(
                latitude=lat, longitude=lon,
                accuracy=100, method='system',
                timestamp=datetime.now(timezone.utc).isoformat(),
                raw_data={'source': 'geoclue2'}
            )
    return None



def get_gps_location(timeout: int = 30) -> Optional[LocationResult]:
    """Get location from GPS hardware (NMEA source)."""
    # Try common GPS sources
    gps_sources = [
        # gpsd on localhost
        ("gpsd", _get_gpsd_location),
        # Serial ports (Windows/Linux)
        ("serial", _get_serial_gps_location),
    ]
    
    for source_name, source_func in gps_sources:
        try:
            result = source_func(timeout)
            if result:
                return result
        except Exception as e:
            print(f"GPS source {source_name} failed: {e}", file=sys.stderr)
    
    return None


def _get_gpsd_location(timeout: int) -> Optional[LocationResult]:
    """Query gpsd daemon for location."""
    try:
        import socket
        import json as json_mod
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(('localhost', 2947))
        
        # Request WATCH mode
        sock.send(b'?WATCH={"enable":true,"json":true}\n')
        
        start = time.time()
        while time.time() - start < timeout:
            data = sock.recv(4096).decode('utf-8', errors='ignore')
            for line in data.strip().split('\n'):
                if line.startswith('{'):
                    try:
                        msg = json_mod.loads(line)
                        if msg.get('class') == 'TPV' and 'lat' in msg and 'lon' in msg:
                            lat = msg['lat']
                            lon = msg['lon']
                            acc = msg.get('eph', 10.0)  # Horizontal error estimate
                            return LocationResult(
                                latitude=lat,
                                longitude=lon,
                                accuracy=max(acc, 3.0),
                                method='gps',
                                timestamp=datetime.now(timezone.utc).isoformat()
                            )
                    except json_mod.JSONDecodeError:
                        continue
        sock.close()
    except Exception:
        pass
    return None


def _get_serial_gps_location(timeout: int) -> Optional[LocationResult]:
    """Read NMEA from serial port."""
    import glob
    
    # Common serial port patterns
    patterns = [
        '/dev/ttyUSB*', '/dev/ttyACM*',  # Linux
        'COM*',  # Windows (handled separately)
    ]
    
    ports = []
    for pattern in patterns:
        ports.extend(glob.glob(pattern))
    
    # Windows COM ports
    if sys.platform == 'win32':
        for i in range(1, 20):
            ports.append(f'COM{i}')
    
    for port in ports:
        try:
            result = _read_nmea_port(port, timeout)
            if result:
                return result
        except Exception:
            continue
    
    return None


def _read_nmea_port(port: str, timeout: int) -> Optional[LocationResult]:
    """Read and parse NMEA sentences from a port."""
    import serial
    
    try:
        ser = serial.Serial(port, 4800, timeout=1)
        start = time.time()
        nmea_parser = NMEAParser()
        
        while time.time() - start < timeout:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if line.startswith('$'):
                loc = nmea_parser.parse(line)
                if loc:
                    ser.close()
                    return LocationResult(
                        latitude=loc[0],
                        longitude=loc[1],
                        accuracy=10.0,
                        method='gps',
                        timestamp=datetime.now(timezone.utc).isoformat()
                    )
        ser.close()
    except Exception:
        pass
    return None


class NMEAParser:
    """Simple NMEA sentence parser for GPRMC and GPGGA."""
    
    def __init__(self):
        self.last_valid = None
    
    def parse(self, sentence: str) -> Optional[tuple]:
        """Parse NMEA sentence, return (lat, lon) or None."""
        if not sentence.startswith('$'):
            return None
        
        try:
            # Calculate checksum
            parts = sentence.split('*')
            if len(parts) != 2:
                return None
            
            data = parts[0][1:]  # Remove $
            checksum = int(parts[1], 16)
            
            calc_sum = 0
            for c in data:
                calc_sum ^= ord(c)
            
            if calc_sum != checksum:
                return None
            
            fields = data.split(',')
            
            if fields[0] == 'GPRMC':
                return self._parse_rmc(fields)
            elif fields[0] == 'GPGGA':
                return self._parse_gga(fields)
            
        except Exception:
            pass
        return None
    
    def _parse_rmc(self, fields: List[str]) -> Optional[tuple]:
        """Parse GPRMC sentence."""
        if len(fields) < 12 or fields[2] != 'A':  # A = valid
            return None
        
        lat = self._parse_coord(fields[3], fields[4])
        lon = self._parse_coord(fields[5], fields[6])
        
        if lat is not None and lon is not None:
            self.last_valid = (lat, lon)
            return (lat, lon)
        return None
    
    def _parse_gga(self, fields: List[str]) -> Optional[tuple]:
        """Parse GPGGA sentence."""
        if len(fields) < 10:
            return None
        
        lat = self._parse_coord(fields[2], fields[3])
        lon = self._parse_coord(fields[4], fields[5])
        
        if lat is not None and lon is not None:
            self.last_valid = (lat, lon)
            return (lat, lon)
        return None
    
    def _parse_coord(self, value: str, direction: str) -> Optional[float]:
        """Parse NMEA coordinate (DDMM.MMMM or DDDMM.MMMM)."""
        if not value or not direction:
            return None
        
        try:
            # Find decimal point
            dot = value.index('.')
            deg_len = dot - 2 if dot > 2 else 2
            
            degrees = float(value[:deg_len])
            minutes = float(value[deg_len:])
            
            decimal = degrees + minutes / 60.0
            
            if direction in ('S', 'W'):
                decimal = -decimal
            
            return decimal
        except Exception:
            return None


def get_ip_location() -> Optional[LocationResult]:
    """Get location from IP geolocation APIs."""
    apis = [
        ('ip-api.com', _get_ip_api_com),
        ('ipinfo.io', _get_ipinfo_io),
        ('ipgeolocation.io', _get_ipgeolocation),
    ]
    
    results = []
    for name, func in apis:
        try:
            result = func()
            if result:
                results.append(result)
        except Exception as e:
            print(f"IP API {name} failed: {e}", file=sys.stderr)
    
    if not results:
        return None
    
    # If multiple results, cross-validate and average
    if len(results) == 1:
        return results[0]
    
    # Weighted average based on claimed accuracy
    total_weight = 0
    weighted_lat = 0
    weighted_lon = 0
    
    for r in results:
        w = 1.0 / r.accuracy
        weighted_lat += r.latitude * w
        weighted_lon += r.longitude * w
        total_weight += w
    
    return LocationResult(
        latitude=weighted_lat / total_weight,
        longitude=weighted_lon / total_weight,
        accuracy=max(r.accuracy for r in results),
        method='ip',
        timestamp=datetime.now(timezone.utc).isoformat()
    )


def _get_ip_api_com() -> Optional[LocationResult]:
    """Query ip-api.com (free, no key required)."""
    url = "http://ip-api.com/json/?fields=status,lat,lon,city,country,isp"
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'multi-source-locate/1.0'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            
            if data.get('status') != 'success':
                return None
            
            return LocationResult(
                latitude=data['lat'],
                longitude=data['lon'],
                accuracy=5000.0,  # ~5km typical
                method='ip',
                timestamp=datetime.now(timezone.utc).isoformat(),
                raw_data={'city': data.get('city'), 'country': data.get('country')}
            )
    except Exception:
        return None


def _get_ipinfo_io() -> Optional[LocationResult]:
    """Query ipinfo.io (free tier: 50k req/month)."""
    url = "https://ipinfo.io/json"
    
    ctx = ssl.create_default_context()
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'multi-source-locate/1.0'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            
            if 'loc' not in data:
                return None
            
            lat, lon = map(float, data['loc'].split(','))
            
            return LocationResult(
                latitude=lat,
                longitude=lon,
                accuracy=10000.0,  # ~10km
                method='ip',
                timestamp=datetime.now(timezone.utc).isoformat(),
                raw_data={'city': data.get('city'), 'country': data.get('country')}
            )
    except Exception:
        return None


def _get_ipgeolocation() -> Optional[LocationResult]:
    """Query ipgeolocation.io (free tier available)."""
    url = "https://api.ipgeolocation.io/ipgeo?apiKey=free"
    
    ctx = ssl.create_default_context()
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'multi-source-locate/1.0'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            
            lat = data.get('latitude')
            lon = data.get('longitude')
            
            if lat is None or lon is None:
                return None
            
            return LocationResult(
                latitude=float(lat),
                longitude=float(lon),
                accuracy=8000.0,
                method='ip',
                timestamp=datetime.now(timezone.utc).isoformat(),
                raw_data={'city': data.get('city'), 'country': data.get('country_name')}
            )
    except Exception:
        return None


def get_wifi_location() -> Optional[LocationResult]:
    """Get location from WiFi BSSID geolocation."""
    bssids = _scan_wifi_bssids()
    
    if not bssids:
        return None
    
    # Try geolocation APIs with BSSID data
    result = _geolocate_wifi(bssids)
    
    if result:
        return result
    
    return None


def _scan_wifi_bssids() -> List[Dict[str, Any]]:
    """Scan for nearby WiFi networks and collect BSSIDs."""
    bssids = []
    
    if sys.platform == 'win32':
        # Windows: netsh wlan show networks mode=bssid
        # NOTE: use encoding='utf-8' with errors='ignore' to handle Chinese SSIDs
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',       # force UTF-8 (Windows default is GBK)
                errors='ignore'          # skip undecodable bytes (Chinese SSIDs)
            )
            
            current_ssid = None
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('SSID'):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        current_ssid = parts[1].strip()
                elif 'BSSID' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        bssid = parts[1].strip().upper()
                        if bssid and bssid not in [b.get('bssid') for b in bssids]:
                            bssids.append({'ssid': current_ssid, 'bssid': bssid})
                elif 'Signal' in line and bssids:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        try:
                            signal = int(parts[1].strip().rstrip('%'))
                            bssids[-1]['signal'] = signal
                        except ValueError:
                            pass
        except Exception as e:
            print(f"WiFi scan failed: {e}", file=sys.stderr)
    
    elif sys.platform == 'darwin':
        # macOS: airport -s
        try:
            result = subprocess.run(
                ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8', errors='ignore'
            )
            
            for line in result.stdout.split('\n')[1:]:  # Skip header
                parts = line.split()
                if len(parts) >= 6:
                    bssid = parts[1].upper()
                    signal = int(parts[2])
                    bssids.append({'ssid': parts[0], 'bssid': bssid, 'signal': signal})
        except Exception as e:
            print(f"WiFi scan failed: {e}", file=sys.stderr)
    
    else:
        # Linux: nmcli or iwlist
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,BSSID,SIGNAL', 'device', 'wifi', 'list'],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8', errors='ignore'
            )
            
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.split(':')
                    if len(parts) >= 3:
                        ssid = parts[0]
                        bssid = parts[1].upper()
                        try:
                            signal = int(parts[2])
                        except ValueError:
                            signal = 0
                        bssids.append({'ssid': ssid, 'bssid': bssid, 'signal': signal})
        except Exception as e:
            print(f"WiFi scan failed: {e}", file=sys.stderr)
    
    return bssids


def _geolocate_wifi(bssids: List[Dict[str, Any]]) -> Optional[LocationResult]:
    """Query geolocation API with WiFi BSSIDs."""
    # Google Geolocation API (requires key)
    # Mozilla Location Service (MLS) - free but deprecated
    # Unwired Labs - free tier available
    
    import os
    
    # Try Google if key available
    google_key = os.environ.get('GOOGLE_GEOLOCATION_API_KEY')
    if google_key:
        return _geolocate_google(bssids, google_key)
    
    # Try Unwired Labs
    unwired_key = os.environ.get('UNWIRED_API_KEY', 'free')
    return _geolocate_unwired(bssids, unwired_key)


def _geolocate_google(bssids: List[Dict[str, Any]], api_key: str) -> Optional[LocationResult]:
    """Query Google Geolocation API."""
    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={api_key}"
    
    wifi_aps = []
    for ap in bssids[:20]:  # Max 20 APs
        wifi_aps.append({
            'macAddress': ap['bssid'].replace(':', '').replace('-', ''),
            'signalStrength': ap.get('signal', -50)
        })
    
    payload = json.dumps({'wifiAccessPoints': wifi_aps}).encode()
    
    ctx = ssl.create_default_context()
    
    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            
            location = data.get('location', {})
            accuracy = data.get('accuracy', 100)
            
            return LocationResult(
                latitude=location.get('lat'),
                longitude=location.get('lng'),
                accuracy=float(accuracy),
                method='wifi',
                timestamp=datetime.now(timezone.utc).isoformat()
            )
    except Exception as e:
        print(f"Google geolocation failed: {e}", file=sys.stderr)
        return None


def _geolocate_unwired(bssids: List[Dict[str, Any]], api_key: str) -> Optional[LocationResult]:
    """Query Unwired Labs (unwiredlabs.com) geolocation."""
    url = "https://us1.unwiredlabs.com/v2/process.php"
    
    wifi_aps = []
    for ap in bssids[:20]:
        wifi_aps.append({
            'bssid': ap['bssid'],
            'signal': ap.get('signal', -50)
        })
    
    payload = json.dumps({
        'token': api_key,
        'wifi': wifi_aps
    }).encode()
    
    ctx = ssl.create_default_context()
    
    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            
            if data.get('status') != 'ok':
                return None
            
            return LocationResult(
                latitude=data.get('lat'),
                longitude=data.get('lon'),
                accuracy=float(data.get('accuracy', 100)),
                method='wifi',
                timestamp=datetime.now(timezone.utc).isoformat()
            )
    except Exception as e:
        print(f"Unwired geolocation failed: {e}", file=sys.stderr)
        return None


def get_cellular_location() -> Optional[LocationResult]:
    """Get location from cellular tower info."""
    cell_info = _scan_cell_towers()
    
    if not cell_info:
        return None
    
    return _geolocate_cell(cell_info)


def _scan_cell_towers() -> List[Dict[str, Any]]:
    """Scan for cellular tower info."""
    cells = []
    
    if sys.platform == 'win32':
        # Windows: Requires cellular modem with AT commands
        # This is complex and hardware-specific
        pass
    
    elif sys.platform == 'darwin':
        # macOS: CoreTelephony framework (requires iOS)
        pass
    
    else:
        # Linux: ModemManager
        try:
            result = subprocess.run(
                ['mmcli', '-m', '0', '--output=json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            data = json.loads(result.stdout)
            modem = data.get('modem', {})
            
            # Get 3GPP info
            gpp = modem.get('3gpp', {})
            if gpp:
                cells.append({
                    'mcc': gpp.get('mcc'),
                    'mnc': gpp.get('mnc'),
                    'lac': gpp.get('location-area-code'),
                    'cid': gpp.get('cell-id')
                })
        except Exception:
            pass
    
    return cells


def _geolocate_cell(cells: List[Dict[str, Any]]) -> Optional[LocationResult]:
    """Query geolocation API with cell tower info."""
    import os
    
    google_key = os.environ.get('GOOGLE_GEOLOCATION_API_KEY')
    if google_key and cells:
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={google_key}"
        
        cell_towers = []
        for cell in cells:
            cell_towers.append({
                'cellId': cell.get('cid'),
                'locationAreaCode': cell.get('lac'),
                'mobileCountryCode': cell.get('mcc'),
                'mobileNetworkCode': cell.get('mnc')
            })
        
        payload = json.dumps({'cellTowers': cell_towers}).encode()
        
        ctx = ssl.create_default_context()
        
        try:
            req = urllib.request.Request(
                url,
                data=payload,
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                data = json.loads(resp.read().decode())
                
                location = data.get('location', {})
                accuracy = data.get('accuracy', 1000)
                
                return LocationResult(
                    latitude=location.get('lat'),
                    longitude=location.get('lng'),
                    accuracy=float(accuracy),
                    method='cellular',
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
        except Exception as e:
            print(f"Cellular geolocation failed: {e}", file=sys.stderr)
    
    return None



def validate_coordinates(lat, lon):
    """Validate and clamp coordinates to valid ranges."""
    try:
        lat = float(lat)
        lon = float(lon)
        lat = max(-90.0, min(90.0, lat))
        lon = max(-180.0, min(180.0, lon))
        return lat, lon
    except (ValueError, TypeError):
        return None, None



@dataclass
class TriangulatedResult:
    """Combined multi-source location result."""
    latitude: float
    longitude: float
    accuracy_meters: float
    confidence: float
    method: str
    sources: Dict[str, Dict[str, Any]]
    timestamp: str


def triangulate(results: List[LocationResult]) -> TriangulatedResult:
    """Combine multiple location results using weighted average."""
    if not results:
        raise ValueError("No location results to triangulate")
    
    if len(results) == 1:
        r = results[0]
        r.weight = 1.0  # normalize: single source = 100% weight
        return TriangulatedResult(
            latitude=r.latitude,
            longitude=r.longitude,
            accuracy_meters=r.accuracy,
            confidence=0.5,  # Single source, moderate confidence
            method=r.method,
            sources={r.method: {
                'lat': r.latitude,
                'lon': r.longitude,
                'accuracy': r.accuracy,
                'weight': 1.0,
                'timestamp': r.timestamp,
                'method': r.method,
                'raw_data': r.raw_data,
            }},
            timestamp=r.timestamp
        )
    
    # Calculate weights based on accuracy (inverse variance)
    for r in results:
        r.weight = 1.0 / (max(r.accuracy, 1.0) ** 2)
    
    total_weight = sum(r.weight for r in results)
    
    # Weighted centroid
    weighted_lat = sum(r.latitude * r.weight for r in results) / total_weight
    weighted_lon = sum(r.longitude * r.weight for r in results) / total_weight
    
    # Estimate combined accuracy from residual dispersion
    if len(results) > 1:
        variance_lat = sum(r.weight * (r.latitude - weighted_lat) ** 2 for r in results) / total_weight
        variance_lon = sum(r.weight * (r.longitude - weighted_lon) ** 2 for r in results) / total_weight
        combined_variance = (variance_lat + variance_lon) / 2
        combined_accuracy = max(
            min(r.accuracy for r in results),  # Can't be better than best source
            (combined_variance ** 0.5) * 111000  # Convert degrees to meters (approx)
        )
    else:
        combined_accuracy = results[0].accuracy
    
    # Confidence score based on number of sources and agreement
    # More sources = higher confidence
    # Better agreement = higher confidence
    source_factor = min(len(results) / 4.0, 1.0)  # Max at 4 sources
    
    # Agreement factor: how well do sources agree?
    if len(results) > 1:
        max_disagreement = max(
            ((r.latitude - weighted_lat) ** 2 + (r.longitude - weighted_lon) ** 2) ** 0.5
            for r in results
        )
        max_disagreement_m = max_disagreement * 111000
        agreement_factor = max(0, 1.0 - max_disagreement_m / (combined_accuracy * 2))
    else:
        agreement_factor = 0.5  # Single source, no agreement to measure
    confidence = (source_factor * 0.4 + agreement_factor * 0.6)
    
    # Build sources dict
    sources = {}
    for r in results:
        sources[r.method] = {
            'lat': r.latitude,
            'lon': r.longitude,
            'accuracy': r.accuracy,
            'weight': r.weight / total_weight,
            'timestamp': r.timestamp,
            'method': r.method,
            'raw_data': r.raw_data,
        }
    
    return TriangulatedResult(
        latitude=weighted_lat,
        longitude=weighted_lon,
        accuracy_meters=combined_accuracy,
        confidence=confidence,
        method='triangulated',
        sources=sources,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


def format_output(result: TriangulatedResult, fmt: str = 'json') -> str:
    """Format result for output."""
    if fmt == 'json':
        return json.dumps(asdict(result), indent=2)
    else:
        lines = [
            f"Location: {result.latitude:.6f}, {result.longitude:.6f}",
            f"Accuracy: {result.accuracy_meters:.0f} meters",
            f"Confidence: {result.confidence:.0%}",
            f"Method: {result.method}",
            f"Sources: {', '.join(result.sources.keys())}",
            f"Timestamp: {result.timestamp}"
        ]
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Multi-source geolocation tool'
    )
    parser.add_argument(
        '--method', '-m',
        default='all',
        help='Location method(s): gps, ip, wifi, cellular, all (comma-separated)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'text'],
        default='json',
        help='Output format'
    )
    parser.add_argument(
        '--timeout', '-t',
        type=int,
        default=30,
        help='Timeout in seconds for GPS'
    )
    
    args = parser.parse_args()
    
    # Parse methods
    if args.method == 'all':
        methods = ['gps', 'system', 'ip', 'wifi', 'cellular']
    else:
        methods = [m.strip().lower() for m in args.method.split(',')]
    
    # Collect results
    results = []
    
    for method in methods:
        print(f"Trying {method}...", file=sys.stderr)
        
        if method == 'gps':
            r = get_gps_location(args.timeout)
        elif method == 'system':
            r = get_system_location(args.timeout)
        elif method == 'ip':
            r = get_ip_location()
        elif method == 'wifi':
            r = get_wifi_location()
        elif method == 'cellular':
            r = get_cellular_location()
        else:
            print(f"Unknown method: {method}", file=sys.stderr)
            continue
        
        if r:
            print(f"  {method}: {r.latitude:.4f}, {r.longitude:.4f} (±{r.accuracy:.0f}m)", file=sys.stderr)
            results.append(r)
        else:
            print(f"  {method}: failed", file=sys.stderr)
    
    if not results:
        print("Error: No location sources succeeded", file=sys.stderr)
        sys.exit(1)
    
    # Triangulate
    final = triangulate(results)
    
    # Output
    print(format_output(final, args.format))


if __name__ == '__main__':
    main()
