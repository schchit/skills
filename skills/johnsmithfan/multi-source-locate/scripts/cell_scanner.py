#!/usr/bin/env python3
"""
Cellular tower scanner module.
Scans for cellular tower info for geolocation.
"""

import subprocess
import sys
import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CellTower:
    """Cellular tower information."""
    mcc: int  # Mobile Country Code
    mnc: int  # Mobile Network Code
    lac: int  # Location Area Code (2G/3G) or TAC (4G)
    cid: int  # Cell ID
    signal: int = 0  # Signal strength (dBm)
    rat: str = ''  # Radio Access Technology (GSM, UMTS, LTE, NR)
    arfcn: Optional[int] = None  # Absolute RF Channel Number
    pci: Optional[int] = None  # Physical Cell ID (LTE/NR)
    timing_advance: Optional[int] = None


def scan_cell_towers() -> List[CellTower]:
    """
    Scan for cellular tower information.
    Returns list of CellTower objects.
    """
    if sys.platform == 'win32':
        return _scan_windows()
    elif sys.platform == 'darwin':
        return _scan_macos()
    else:
        return _scan_linux()


def _scan_windows() -> List[CellTower]:
    """
    Scan cellular on Windows.
    Requires cellular modem with AT command interface.
    """
    towers = []
    
    # Try Windows Mobile Broadband API via PowerShell
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-NetAdapter | Where-Object {$_.MediaType -eq "MobileBroadband"} | Select-Object -First 1'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Found mobile broadband adapter
            # Try to get cell info via netsh mbn
            result2 = subprocess.run(
                ['netsh', 'mbn', 'show', 'caps', 'interface=*'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parse cell info if available
            # This is limited on Windows without specific modem drivers
    except Exception:
        pass
    
    # Alternative: Try AT commands via serial port
    # This requires a cellular modem exposed as COM port
    towers.extend(_scan_at_ports())
    
    return towers


def _scan_at_ports() -> List[CellTower]:
    """Scan cellular modems via AT commands."""
    towers = []
    
    # Common modem port patterns
    ports = []
    if sys.platform == 'win32':
        for i in range(1, 20):
            ports.append(f'COM{i}')
    else:
        import glob
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    
    for port in ports:
        try:
            tower = _query_modem_at(port)
            if tower:
                towers.append(tower)
        except Exception:
            continue
    
    return towers


def _query_modem_at(port: str) -> Optional[CellTower]:
    """Query modem via AT commands."""
    import serial
    import time
    
    try:
        ser = serial.Serial(port, 115200, timeout=2)
        
        # Try to get cell info
        # AT+COPS? - Get network operator
        # AT+CREG? - Get registration status
        # AT+CGREG? - Get GPRS registration
        # AT+CEREG? - Get EPS registration (LTE)
        
        ser.write(b'AT+COPS=3,2\r\n')  # Set numeric format
        time.sleep(0.5)
        ser.read(ser.in_waiting)
        
        ser.write(b'AT+COPS?\r\n')
        time.sleep(1)
        response = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
        
        # Parse +COPS: <mode>[,<format>,<oper>,<act>]
        match = re.search(r'\+COPS:\s*\d+,(\d+),(\d+),(\d+)', response)
        if match:
            # oper is PLMN = MCC + MNC
            plmn = match.group(2)
            mcc = int(plmn[:3])
            mnc = int(plmn[3:])
            rat_code = int(match.group(3))
            rat_map = {0: 'GSM', 2: 'UTRAN', 7: 'LTE', 13: 'NR'}
            rat = rat_map.get(rat_code, '')
        
        # Get LAC and CID (varies by modem)
        # For Qualcomm: AT+QNWCFG="lte_cell_info"
        # For Huawei: AT^HCSQ?
        # Generic: AT+CREG? (2G) or AT+CEREG? (LTE)
        
        ser.write(b'AT+CREG=2\r\n')  # Enable network registration URC
        time.sleep(0.5)
        ser.read(ser.in_waiting)
        
        ser.write(b'AT+CREG?\r\n')
        time.sleep(1)
        response = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
        
        # Parse +CREG: <n>,<stat>[,<lac>,<cid>]
        match = re.search(r'\+CREG:\s*\d+,\d+,([0-9a-fA-F]+),([0-9a-fA-F]+)', response)
        if match:
            lac = int(match.group(1), 16)
            cid = int(match.group(2), 16)
            
            ser.close()
            
            return CellTower(
                mcc=mcc if 'mcc' in dir() else 0,
                mnc=mnc if 'mnc' in dir() else 0,
                lac=lac,
                cid=cid,
                rat=rat if 'rat' in dir() else 'GSM'
            )
        
        # Try LTE registration
        ser.write(b'AT+CEREG=2\r\n')
        time.sleep(0.5)
        ser.read(ser.in_waiting)
        
        ser.write(b'AT+CEREG?\r\n')
        time.sleep(1)
        response = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
        
        # Parse +CEREG: <n>,<stat>[,<tac>,<cid>,<act>]
        match = re.search(r'\+CEREG:\s*\d+,\d+,([0-9a-fA-F]+),([0-9a-fA-F]+)', response)
        if match:
            tac = int(match.group(1), 16)
            cid = int(match.group(2), 16)
            
            ser.close()
            
            return CellTower(
                mcc=mcc if 'mcc' in dir() else 0,
                mnc=mnc if 'mnc' in dir() else 0,
                lac=tac,
                cid=cid,
                rat='LTE'
            )
        
        ser.close()
    
    except Exception:
        pass
    
    return None


def _scan_macos() -> List[CellTower]:
    """
    Scan cellular on macOS.
    Limited on desktop Macs; full support on iPhone.
    """
    towers = []
    
    # macOS doesn't expose cellular info on desktop
    # On iPhone, would use CoreTelephony framework
    
    return towers


def _scan_linux() -> List[CellTower]:
    """Scan cellular on Linux using ModemManager."""
    towers = []
    
    try:
        # List modems
        result = subprocess.run(
            ['mmcli', '-L'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Parse modem paths
        modem_paths = re.findall(r'/org/freedesktop/ModemManager1/Modem/\d+', result.stdout)
        
        for path in modem_paths:
            try:
                # Get modem info
                result = subprocess.run(
                    ['mmcli', '-m', path, '--output=json'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                data = json.loads(result.stdout)
                modem = data.get('modem', {})
                
                # Get 3GPP info
                gpp = modem.get('3gpp', {})
                
                mcc = gpp.get('mcc')
                mnc = gpp.get('mnc')
                
                # Get location
                result2 = subprocess.run(
                    ['mmcli', '-m', path, '--location-get'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Parse location output
                # 3GPP location:  mcc: 262, mnc: 1, lac: 5286, cid: 262851
                match = re.search(
                    r'3GPP location:\s*mcc:\s*(\d+),\s*mnc:\s*(\d+),\s*lac:\s*(\d+),\s*cid:\s*(\d+)',
                    result2.stdout
                )
                
                if match:
                    towers.append(CellTower(
                        mcc=int(match.group(1)),
                        mnc=int(match.group(2)),
                        lac=int(match.group(3)),
                        cid=int(match.group(4)),
                        rat='GSM'
                    ))
                
                # Try LTE cell info
                # mmcli -m 0 --signal-get
                result3 = subprocess.run(
                    ['mmcli', '-m', path, '--signal-get'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Parse LTE signal info
                # LTE:  rss: -65, rsrq: -9, rsrp: -95, snr: 14
                # This gives signal but not cell ID
                
            except Exception:
                continue
    
    except Exception as e:
        print(f"ModemManager scan failed: {e}", file=sys.stderr)
    
    return towers


def get_connected_cell() -> Optional[CellTower]:
    """Get the currently connected cell tower."""
    towers = scan_cell_towers()
    return towers[0] if towers else None


if __name__ == '__main__':
    print("Scanning cellular towers...\n")
    
    towers = scan_cell_towers()
    
    if towers:
        print(f"Found {len(towers)} cell towers:\n")
        for tower in towers:
            print(f"  MCC: {tower.mcc}, MNC: {tower.mnc}")
            print(f"  LAC/TAC: {tower.lac}, CID: {tower.cid}")
            print(f"  RAT: {tower.rat or 'Unknown'}")
            print(f"  Signal: {tower.signal} dBm")
            print()
    else:
        print("No cellular towers found")
        print("(This is normal on desktop systems without cellular modem)")
