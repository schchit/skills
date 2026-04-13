#!/usr/bin/env python3
"""
WiFi BSSID scanner module.
Scans for nearby WiFi networks and collects BSSIDs for geolocation.
"""

import subprocess
import sys
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class WiFiAccessPoint:
    """WiFi access point info."""
    ssid: str
    bssid: str  # MAC address
    signal: int  # dBm or percentage
    channel: Optional[int] = None
    frequency: Optional[int] = None  # MHz
    encryption: Optional[str] = None


def scan_wifi() -> List[WiFiAccessPoint]:
    """
    Scan for nearby WiFi networks.
    Returns list of WiFiAccessPoint objects.
    """
    if sys.platform == 'win32':
        return _scan_windows()
    elif sys.platform == 'darwin':
        return _scan_macos()
    else:
        return _scan_linux()


def _scan_windows() -> List[WiFiAccessPoint]:
    """
    Scan WiFi on Windows using netsh.
    
    Output format:
    SSID 1 : NetworkName
        Network type             : Infrastructure
        Authentication          : WPA2-Personal
        Encryption              : CCMP
        BSSID 1                 : aa:bb:cc:dd:ee:ff
             Signal             : 80%
             Channel            : 6
    """
    aps = []
    
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='ignore'
        )
        
        current_ap = None
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            
            # SSID line
            match = re.match(r'SSID \d+\s*:\s*(.+)', line)
            if match:
                if current_ap:
                    aps.append(current_ap)
                current_ap = WiFiAccessPoint(
                    ssid=match.group(1).strip(),
                    bssid='',
                    signal=0
                )
                continue
            
            if not current_ap:
                continue
            
            # BSSID line
            match = re.match(r'BSSID \d+\s*:\s*([0-9a-fA-F:]+)', line)
            if match:
                if current_ap.bssid:  # Save previous BSSID for this SSID
                    aps.append(current_ap)
                    current_ap = WiFiAccessPoint(
                        ssid=current_ap.ssid,
                        bssid='',
                        signal=0
                    )
                current_ap.bssid = match.group(1).upper()
                continue
            
            # Signal line
            match = re.match(r'Signal\s*:\s*(\d+)%', line)
            if match:
                # Convert percentage to dBm (approximate)
                pct = int(match.group(1))
                current_ap.signal = pct
                continue
            
            # Channel line
            match = re.match(r'Channel\s*:\s*(\d+)', line)
            if match:
                current_ap.channel = int(match.group(1))
                continue
            
            # Encryption
            match = re.match(r'Encryption\s*:\s*(\w+)', line)
            if match:
                current_ap.encryption = match.group(1)
        
        if current_ap and current_ap.bssid:
            aps.append(current_ap)
    
    except Exception as e:
        print(f"WiFi scan failed: {e}", file=sys.stderr)
    
    return aps


def _scan_macos() -> List[WiFiAccessPoint]:
    """
    Scan WiFi on macOS using airport utility.
    
    Output format (airport -s):
                 SSID BSSID             RSSI CHANNEL HT CC SECURITY
        MyNetwork aa:bb:cc:dd:ee:ff -70  6       Y  US WPA2(PSK)
    """
    aps = []
    
    airport_path = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'
    
    try:
        result = subprocess.run(
            [airport_path, '-s'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Skip header line
        lines = result.stdout.strip().split('\n')[1:]
        
        for line in lines:
            if not line.strip():
                continue
            
            # Parse fixed-width columns
            # SSID is up to 32 chars, then BSSID, RSSI, CHANNEL, etc.
            parts = line.split()
            
            if len(parts) >= 4:
                # Last parts are: RSSI CHANNEL HT CC SECURITY
                # RSSI is negative number
                ssid_parts = []
                bssid = None
                rssi = None
                channel = None
                
                for i, part in enumerate(parts):
                    # BSSID looks like xx:xx:xx:xx:xx:xx
                    if re.match(r'[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}', part):
                        ssid_parts = parts[:i]
                        bssid = part.upper()
                        if i + 1 < len(parts):
                            try:
                                rssi = int(parts[i + 1])
                            except ValueError:
                                pass
                        if i + 2 < len(parts):
                            try:
                                channel = int(parts[i + 2])
                            except ValueError:
                                pass
                        break
                
                if bssid:
                    aps.append(WiFiAccessPoint(
                        ssid=' '.join(ssid_parts) if ssid_parts else '',
                        bssid=bssid,
                        signal=rssi if rssi is not None else 0,
                        channel=channel
                    ))
    
    except Exception as e:
        print(f"WiFi scan failed: {e}", file=sys.stderr)
    
    return aps


def _scan_linux() -> List[WiFiAccessPoint]:
    """
    Scan WiFi on Linux using nmcli or iwlist.
    """
    # Try nmcli first (NetworkManager)
    aps = _scan_nmcli()
    
    if not aps:
        # Fallback to iwlist
        aps = _scan_iwlist()
    
    return aps


def _scan_nmcli() -> List[WiFiAccessPoint]:
    """
    Scan using nmcli (NetworkManager CLI).
    
    Output format (-t for terse, -f for fields):
    SSID:BSSID:SIGNAL:CHAN:SECURITY
    """
    aps = []
    
    try:
        result = subprocess.run(
            ['nmcli', '-t', '-f', 'SSID,BSSID,SIGNAL,CHAN,SECURITY', 'device', 'wifi', 'list'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split(':')
            
            if len(parts) >= 3:
                ssid = parts[0]
                bssid = parts[1].upper() if len(parts) > 1 else ''
                
                # Signal is 0-100 percentage
                signal = 0
                if len(parts) > 2:
                    try:
                        signal = int(parts[2])
                    except ValueError:
                        pass
                
                # Channel
                channel = None
                if len(parts) > 3 and parts[3]:
                    try:
                        channel = int(parts[3])
                    except ValueError:
                        pass
                
                # Security
                encryption = parts[4] if len(parts) > 4 else None
                
                if bssid:
                    aps.append(WiFiAccessPoint(
                        ssid=ssid,
                        bssid=bssid,
                        signal=signal,
                        channel=channel,
                        encryption=encryption
                    ))
    
    except Exception as e:
        print(f"nmcli scan failed: {e}", file=sys.stderr)
    
    return aps


def _scan_iwlist() -> List[WiFiAccessPoint]:
    """
    Scan using iwlist (wireless-tools).
    
    Output format:
          Cell 01 - Address: AA:BB:CC:DD:EE:FF
                    Channel:6
                    Frequency:2.437 GHz (Channel 6)
                    Quality=70/70  Signal level=-40 dBm
                    ESSID:"NetworkName"
    """
    aps = []
    
    try:
        # Find wireless interface
        result = subprocess.run(
            ['iw', 'dev'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        interface = None
        for line in result.stdout.split('\n'):
            if 'Interface' in line:
                interface = line.split()[-1]
                break
        
        if not interface:
            # Try common names
            for iface in ['wlan0', 'wlp2s0', 'wlp3s0']:
                result = subprocess.run(
                    ['ip', 'link', 'show', iface],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    interface = iface
                    break
        
        if not interface:
            return aps
        
        # Scan with iwlist
        result = subprocess.run(
            ['iwlist', interface, 'scan'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        current_ap = None
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            
            # Cell (new AP)
            match = re.match(r'Cell \d+\s*-\s*Address:\s*([0-9a-fA-F:]+)', line)
            if match:
                if current_ap:
                    aps.append(current_ap)
                current_ap = WiFiAccessPoint(
                    ssid='',
                    bssid=match.group(1).upper(),
                    signal=0
                )
                continue
            
            if not current_ap:
                continue
            
            # ESSID
            match = re.match(r'ESSID:"(.+)"', line)
            if match:
                current_ap.ssid = match.group(1)
                continue
            
            # Signal level
            match = re.search(r'Signal level=(-?\d+)\s*dBm', line)
            if match:
                current_ap.signal = int(match.group(1))
                continue
            
            # Channel
            match = re.match(r'Channel:(\d+)', line)
            if match:
                current_ap.channel = int(match.group(1))
                continue
            
            # Frequency
            match = re.match(r'Frequency:([\d.]+)\s*GHz', line)
            if match:
                freq_ghz = float(match.group(1))
                current_ap.frequency = int(freq_ghz * 1000)
        
        if current_ap:
            aps.append(current_ap)
    
    except Exception as e:
        print(f"iwlist scan failed: {e}", file=sys.stderr)
    
    return aps


def get_connected_ap() -> Optional[WiFiAccessPoint]:
    """Get the currently connected WiFi AP."""
    if sys.platform == 'win32':
        return _get_connected_windows()
    elif sys.platform == 'darwin':
        return _get_connected_macos()
    else:
        return _get_connected_linux()


def _get_connected_windows() -> Optional[WiFiAccessPoint]:
    """Get connected AP on Windows."""
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'interfaces'],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='ignore'
        )
        
        ssid = None
        bssid = None
        signal = 0
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            
            match = re.match(r'SSID\s*:\s*(.+)', line)
            if match:
                ssid = match.group(1).strip()
            
            match = re.match(r'BSSID\s*:\s*([0-9a-fA-F:]+)', line)
            if match:
                bssid = match.group(1).upper()
            
            match = re.match(r'Signal\s*:\s*(\d+)%', line)
            if match:
                signal = int(match.group(1))
        
        if ssid and bssid:
            return WiFiAccessPoint(ssid=ssid, bssid=bssid, signal=signal)
    
    except Exception:
        pass
    
    return None


def _get_connected_macos() -> Optional[WiFiAccessPoint]:
    """Get connected AP on macOS."""
    airport_path = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'
    
    try:
        result = subprocess.run(
            [airport_path, '-I'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        ssid = None
        bssid = None
        rssi = 0
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            
            if line.startswith('SSID:'):
                ssid = line.split(':', 1)[1].strip()
            elif line.startswith('BSSID:'):
                bssid = line.split(':', 1)[1].strip().upper()
            elif line.startswith('rssi:'):
                try:
                    rssi = int(line.split(':', 1)[1].strip())
                except ValueError:
                    pass
        
        if ssid and bssid:
            return WiFiAccessPoint(ssid=ssid, bssid=bssid, signal=rssi)
    
    except Exception:
        pass
    
    return None


def _get_connected_linux() -> Optional[WiFiAccessPoint]:
    """Get connected AP on Linux."""
    try:
        result = subprocess.run(
            ['nmcli', '-t', '-f', 'ACTIVE,SSID,BSSID,SIGNAL', 'device', 'wifi', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        for line in result.stdout.strip().split('\n'):
            parts = line.split(':')
            if parts[0] == 'yes' and len(parts) >= 3:
                return WiFiAccessPoint(
                    ssid=parts[1],
                    bssid=parts[2].upper(),
                    signal=int(parts[3]) if len(parts) > 3 else 0
                )
    
    except Exception:
        pass
    
    return None


if __name__ == '__main__':
    print("Scanning WiFi networks...\n")
    
    aps = scan_wifi()
    
    if aps:
        print(f"Found {len(aps)} access points:\n")
        for ap in sorted(aps, key=lambda x: -x.signal):
            ch_display = str(ap.channel) if ap.channel else '-'
            print(f"  {ap.ssid:32s} {ap.bssid}  Signal: {ap.signal:3d}  Ch: {ch_display:>2}")
    else:
        print("No access points found")
    
    print("\nConnected AP:")
    connected = get_connected_ap()
    if connected:
        print(f"  {connected.ssid} ({connected.bssid})")
    else:
        print("  Not connected")
