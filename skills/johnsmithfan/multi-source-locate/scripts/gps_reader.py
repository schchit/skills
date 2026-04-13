#!/usr/bin/env python3
"""
NMEA GPS reader module.
Parses GPS data from serial ports or gpsd daemon.
"""

import sys
import time
import threading
from typing import Optional, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GPSPosition:
    """GPS position with metadata."""
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed: Optional[float] = None  # knots
    course: Optional[float] = None  # degrees true
    hdop: Optional[float] = None  # horizontal dilution
    satellites: Optional[int] = None
    timestamp: Optional[datetime] = None
    fix_quality: int = 0  # 0=invalid, 1=GPS, 2=DGPS


class NMEAParser:
    """NMEA 0183 sentence parser."""
    
    def __init__(self):
        self.position = GPSPosition(
            latitude=0.0,
            longitude=0.0
        )
    
    def parse(self, sentence: str) -> Optional[GPSPosition]:
        """Parse an NMEA sentence and return position if updated."""
        if not sentence or not sentence.startswith('$'):
            return None
        
        # Validate checksum
        if '*' in sentence:
            try:
                data, checksum = sentence.split('*')
                data = data[1:]  # Remove $
                calc_sum = 0
                for c in data:
                    calc_sum ^= ord(c)
                
                if int(checksum, 16) != calc_sum:
                    return None
            except ValueError:
                return None
        
        # Parse by sentence type
        fields = sentence.split(',')
        sentence_type = fields[0][3:]  # Remove $GP
        
        if sentence_type == 'RMC':
            return self._parse_rmc(fields)
        elif sentence_type == 'GGA':
            return self._parse_gga(fields)
        elif sentence_type == 'GSA':
            return self._parse_gsa(fields)
        elif sentence_type == 'GSV':
            return self._parse_gsv(fields)
        elif sentence_type == 'VTG':
            return self._parse_vtg(fields)
        
        return None
    
    def _parse_coord(self, value: str, direction: str) -> Optional[float]:
        """Parse NMEA coordinate (DDMM.MMMM or DDDMM.MMMM)."""
        if not value or not direction:
            return None
        
        try:
            # Find decimal point position
            dot_idx = value.index('.')
            # Degrees are everything before last 2 digits before decimal
            deg_len = dot_idx - 2
            
            degrees = float(value[:deg_len])
            minutes = float(value[deg_len:])
            
            decimal = degrees + minutes / 60.0
            
            if direction in ('S', 'W'):
                decimal = -decimal
            
            return decimal
        except (ValueError, IndexError):
            return None
    
    def _parse_time(self, value: str) -> Optional[datetime]:
        """Parse NMEA time (HHMMSS or HHMMSS.ss)."""
        if not value or len(value) < 6:
            return None
        
        try:
            hour = int(value[0:2])
            minute = int(value[2:4])
            second = int(float(value[4:]))
            
            return datetime.utcnow().replace(
                hour=hour, minute=minute, second=second
            )
        except ValueError:
            return None
    
    def _parse_rmc(self, fields: list) -> Optional[GPSPosition]:
        """
        Parse RMC (Recommended Minimum) sentence.
        $GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
        """
        if len(fields) < 12:
            return None
        
        # Status: A=valid, V=warning
        if fields[2] != 'A':
            return None
        
        lat = self._parse_coord(fields[3], fields[4])
        lon = self._parse_coord(fields[5], fields[6])
        
        if lat is None or lon is None:
            return None
        
        self.position.latitude = lat
        self.position.longitude = lon
        
        # Speed (knots)
        if fields[7]:
            try:
                self.position.speed = float(fields[7])
            except ValueError:
                pass
        
        # Course (degrees true)
        if fields[8]:
            try:
                self.position.course = float(fields[8])
            except ValueError:
                pass
        
        # Timestamp
        self.position.timestamp = self._parse_time(fields[1])
        self.position.fix_quality = 1
        
        return self.position
    
    def _parse_gga(self, fields: list) -> Optional[GPSPosition]:
        """
        Parse GGA (Global Positioning System Fix Data) sentence.
        $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
        """
        if len(fields) < 15:
            return None
        
        # Fix quality: 0=invalid, 1=GPS fix, 2=DGPS fix
        try:
            fix_quality = int(fields[6])
        except ValueError:
            return None
        
        if fix_quality == 0:
            return None
        
        lat = self._parse_coord(fields[2], fields[3])
        lon = self._parse_coord(fields[4], fields[5])
        
        if lat is None or lon is None:
            return None
        
        self.position.latitude = lat
        self.position.longitude = lon
        self.position.fix_quality = fix_quality
        
        # Number of satellites
        if fields[7]:
            try:
                self.position.satellites = int(fields[7])
            except ValueError:
                pass
        
        # HDOP
        if fields[8]:
            try:
                self.position.hdop = float(fields[8])
            except ValueError:
                pass
        
        # Altitude
        if fields[9]:
            try:
                self.position.altitude = float(fields[9])
            except ValueError:
                pass
        
        # Timestamp
        self.position.timestamp = self._parse_time(fields[1])
        
        return self.position
    
    def _parse_gsa(self, fields: list) -> Optional[GPSPosition]:
        """
        Parse GSA (GPS DOP and active satellites) sentence.
        $GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39
        """
        if len(fields) < 18:
            return None
        
        # HDOP
        if fields[16]:
            try:
                self.position.hdop = float(fields[16])
            except ValueError:
                pass
        
        return None  # GSA doesn't provide position
    
    def _parse_gsv(self, fields: list) -> Optional[GPSPosition]:
        """Parse GSV (satellites in view) sentence."""
        # GSV provides satellite info, not position
        return None
    
    def _parse_vtg(self, fields: list) -> Optional[GPSPosition]:
        """
        Parse VTG (Track Made Good and Ground Speed) sentence.
        $GPVTG,054.7,T,034.4,M,005.5,N,010.2,K*48
        """
        if len(fields) < 9:
            return None
        
        # Course (degrees true)
        if fields[1]:
            try:
                self.position.course = float(fields[1])
            except ValueError:
                pass
        
        # Speed (knots)
        if fields[5]:
            try:
                self.position.speed = float(fields[5])
            except ValueError:
                pass
        
        return None  # VTG doesn't provide position


class GPSReader:
    """GPS reader that handles serial port or gpsd connection."""
    
    def __init__(self, source: str = 'auto', callback: Optional[Callable] = None):
        """
        Initialize GPS reader.
        
        Args:
            source: 'auto', 'gpsd', or serial port path (e.g., '/dev/ttyUSB0', 'COM3')
            callback: Optional callback function for position updates
        """
        self.source = source
        self.callback = callback
        self.parser = NMEAParser()
        self.running = False
        self.thread = None
        self._serial = None
        self._socket = None
    
    def start(self) -> bool:
        """Start reading GPS data."""
        if self.running:
            return True
        
        if self.source == 'auto':
            # Try gpsd first, then serial ports
            if self._try_gpsd():
                self.running = True
                return True
            
            if self._try_serial():
                self.running = True
                return True
            
            return False
        
        elif self.source == 'gpsd':
            return self._try_gpsd()
        
        else:
            return self._try_serial(self.source)
    
    def _try_gpsd(self) -> bool:
        """Try to connect to gpsd daemon."""
        try:
            import socket
            
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(5)
            self._socket.connect(('localhost', 2947))
            self._socket.send(b'?WATCH={"enable":true,"json":true}\n')
            
            self.running = True
            self.thread = threading.Thread(target=self._read_gpsd, daemon=True)
            self.thread.start()
            return True
        except Exception:
            return False
    
    def _try_serial(self, port: Optional[str] = None) -> bool:
        """Try to open serial port."""
        import glob
        
        ports_to_try = []
        
        if port:
            ports_to_try = [port]
        else:
            # Auto-detect
            if sys.platform == 'win32':
                ports_to_try = [f'COM{i}' for i in range(1, 20)]
            else:
                ports_to_try = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        
        for p in ports_to_try:
            try:
                import serial
                self._serial = serial.Serial(p, 4800, timeout=1)
                self.running = True
                self.thread = threading.Thread(target=self._read_serial, daemon=True)
                self.thread.start()
                return True
            except Exception:
                continue
        
        return False
    
    def _read_gpsd(self):
        """Read from gpsd daemon."""
        import json
        
        buffer = ""
        
        while self.running and self._socket:
            try:
                data = self._socket.recv(4096).decode('utf-8', errors='ignore')
                buffer += data
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.startswith('{'):
                        try:
                            msg = json.loads(line)
                            if msg.get('class') == 'TPV' and 'lat' in msg and 'lon' in msg:
                                pos = GPSPosition(
                                    latitude=msg['lat'],
                                    longitude=msg['lon'],
                                    altitude=msg.get('alt'),
                                    speed=msg.get('speed'),
                                    course=msg.get('track'),
                                    timestamp=datetime.utcnow()
                                )
                                if self.callback:
                                    self.callback(pos)
                        except json.JSONDecodeError:
                            continue
            except Exception:
                break
    
    def _read_serial(self):
        """Read from serial port."""
        while self.running and self._serial:
            try:
                line = self._serial.readline().decode('ascii', errors='ignore').strip()
                if line.startswith('$'):
                    pos = self.parser.parse(line)
                    if pos and self.callback:
                        self.callback(pos)
            except Exception:
                break
    
    def stop(self):
        """Stop reading GPS data."""
        self.running = False
        
        if self._serial:
            self._serial.close()
            self._serial = None
        
        if self._socket:
            self._socket.close()
            self._socket = None
        
        if self.thread:
            self.thread.join(timeout=2)
    
    def get_position(self, timeout: float = 10.0) -> Optional[GPSPosition]:
        """Get a single position reading."""
        result = [None]
        event = threading.Event()
        
        def callback(pos):
            result[0] = pos
            event.set()
        
        old_callback = self.callback
        self.callback = callback
        
        if not self.running:
            if not self.start():
                return None
        
        if event.wait(timeout):
            self.callback = old_callback
            return result[0]
        
        self.callback = old_callback
        return None


if __name__ == '__main__':
    # Test GPS reader
    print("Testing GPS reader...")
    
    def on_position(pos):
        print(f"Position: {pos.latitude:.6f}, {pos.longitude:.6f}")
        print(f"  Altitude: {pos.altitude}m")
        print(f"  Speed: {pos.speed} knots")
        print(f"  Satellites: {pos.satellites}")
        print(f"  HDOP: {pos.hdop}")
    
    reader = GPSReader(callback=on_position)
    
    if reader.start():
        print("GPS reader started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        reader.stop()
    else:
        print("Failed to start GPS reader")
