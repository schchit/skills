# NMEA Sentence Reference

NMEA 0183 is the standard protocol for GPS receivers. This reference covers the most common sentences used for position determination.

## Sentence Format

All NMEA sentences follow this format:

```
$TALKER,field1,field2,...*checksum
```

- **TALKER**: Two-character talker ID (GP=GPS, GL=GLONASS, GA=Galileo, BD=BeiDou)
- **Fields**: Comma-separated data fields
- **Checksum**: Two-character hexadecimal XOR of all characters between $ and *

### Checksum Calculation

```python
def nmea_checksum(sentence):
    """Calculate NMEA checksum."""
    data = sentence[1:sentence.index('*')]  # Remove $ and *checksum
    checksum = 0
    for char in data:
        checksum ^= ord(char)
    return format(checksum, '02X')
```

## Position Sentences

### RMC - Recommended Minimum Navigation

The most commonly used sentence for position and navigation.

```
$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
```

| Field | Description | Example |
|-------|-------------|---------|
| 1 | UTC Time (HHMMSS.ss) | 123519 = 12:35:19 |
| 2 | Status (A=Active, V=Void) | A |
| 3 | Latitude (DDMM.MMMM) | 4807.038 |
| 4 | N/S Indicator | N |
| 5 | Longitude (DDDMM.MMMM) | 01131.000 |
| 6 | E/W Indicator | E |
| 7 | Speed over ground (knots) | 022.4 |
| 8 | Course over ground (degrees) | 084.4 |
| 9 | Date (DDMMYY) | 230394 = March 23, 1994 |
| 10 | Magnetic variation (degrees) | 003.1 |
| 11 | Variation direction (E/W) | W |

### GGA - Global Positioning System Fix Data

Contains position, altitude, and fix quality.

```
$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
```

| Field | Description | Example |
|-------|-------------|---------|
| 1 | UTC Time | 123519 |
| 2 | Latitude | 4807.038 |
| 3 | N/S | N |
| 4 | Longitude | 01131.000 |
| 5 | E/W | E |
| 6 | Fix Quality | 1 |
| 7 | Satellites in use | 08 |
| 8 | HDOP | 0.9 |
| 9 | Altitude (MSL) | 545.4 |
| 10 | Altitude units | M (meters) |
| 11 | Geoid separation | 46.9 |
| 12 | Geoid units | M |
| 13 | DGPS age | (empty) |
| 14 | DGPS station ID | (empty) |

#### Fix Quality Values

| Value | Description |
|-------|-------------|
| 0 | Invalid/No fix |
| 1 | GPS fix (SPS) |
| 2 | DGPS fix |
| 3 | PPS fix |
| 4 | Real Time Kinematic |
| 5 | Float RTK |
| 6 | Estimated (dead reckoning) |
| 7 | Manual input mode |
| 8 | Simulation mode |

### GLL - Geographic Position

Simple position with time and status.

```
$GPGLL,4807.038,N,01131.000,E,123519,A*27
```

| Field | Description |
|-------|-------------|
| 1 | Latitude |
| 2 | N/S |
| 3 | Longitude |
| 4 | E/W |
| 5 | UTC Time |
| 6 | Status (A/V) |

## Satellite Information

### GSA - GPS DOP and Active Satellites

Dilution of precision and satellite list.

```
$GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39
```

| Field | Description |
|-------|-------------|
| 1 | Selection mode (A=Automatic, M=Manual) |
| 2 | Fix mode (1=No fix, 2=2D, 3=3D) |
| 3-14 | PRN of satellites used |
| 15 | PDOP |
| 16 | HDOP |
| 17 | VDOP |

### GSV - Satellites in View

Satellite details (may span multiple sentences).

```
$GPGSV,2,1,08,01,40,083,46,02,17,308,41,03,12,150,38,04,28,225,46*75
```

| Field | Description |
|-------|-------------|
| 1 | Total messages |
| 2 | Message number |
| 3 | Satellites in view |
| 4,5,6,7 | PRN, Elevation, Azimuth, SNR (repeated) |

## Navigation Data

### VTG - Track Made Good and Ground Speed

Course and speed information.

```
$GPVTG,054.7,T,034.4,M,005.5,N,010.2,K*48
```

| Field | Description |
|-------|-------------|
| 1 | Track true (degrees) |
| 2 | T (True) |
| 3 | Track magnetic |
| 4 | M (Magnetic) |
| 5 | Speed (knots) |
| 6 | N (Knots) |
| 7 | Speed (km/h) |
| 8 | K (km/h) |

### ZDA - Time and Date

UTC time and date with local time zone.

```
$GPZDA,123519,23,03,1994,00,00*6D
```

## Multi-Constellation Sentences

Modern GPS receivers support multiple satellite constellations:

| Talker | Constellation |
|--------|---------------|
| GP | GPS (US) |
| GL | GLONASS (Russia) |
| GA | Galileo (EU) |
| BD / GB | BeiDou (China) |
| QZ | QZSS (Japan) |
| GI | NavIC (India) |

### GNS - GNSS Fix Data

Combined fix data from multiple constellations.

```
$GPGNS,123519,4807.038,N,01131.000,E,A,A,08,0.9,545.4,M,46.9,M,,*42
```

## Coordinate Conversion

### NMEA to Decimal Degrees

NMEA coordinates are in DDMM.MMMM or DDDMM.MMMM format.

```python
def nmea_to_decimal(value, direction):
    """Convert NMEA coordinate to decimal degrees."""
    # Find decimal point
    dot = value.index('.')
    
    # Degrees are before last 2 digits before decimal
    deg_len = dot - 2
    degrees = float(value[:deg_len])
    minutes = float(value[deg_len:])
    
    decimal = degrees + minutes / 60.0
    
    if direction in ('S', 'W'):
        decimal = -decimal
    
    return decimal
```

### Decimal Degrees to NMEA

```python
def decimal_to_nmea(decimal, is_longitude=False):
    """Convert decimal degrees to NMEA format."""
    degrees = abs(int(decimal))
    minutes = (abs(decimal) - degrees) * 60.0
    
    # Format: DDMM.MMMM or DDDMM.MMMM
    if is_longitude:
        return f"{degrees:03d}{minutes:07.4f}"
    else:
        return f"{degrees:02d}{minutes:07.4f}"
```

## Common Issues

### No Fix (V Status)

- Indoor or obstructed sky view
- GPS receiver not initialized
- Antenna disconnected

### Inaccurate Position

- Low HDOP (>2.0)
- Few satellites (<6)
- Multipath interference
- Atmospheric delays

### Timestamp Issues

- GPS time rolls over every 1024 weeks
- Some receivers use local time instead of UTC
- Leap seconds not always accounted for

## GPSD Protocol

When using gpsd daemon, JSON messages are used instead of NMEA:

```json
{
  "class": "TPV",
  "device": "/dev/ttyUSB0",
  "mode": 3,
  "time": "2025-01-15T12:35:19.000Z",
  "lat": 48.1173,
  "lon": 11.5167,
  "alt": 545.4,
  "track": 84.4,
  "speed": 11.5,
  "eph": 10.0
}
```

Key fields:
- `mode`: 0=no fix, 1=no fix, 2=2D fix, 3=3D fix
- `eph`: Estimated horizontal error (meters)
- `epv`: Estimated vertical error (meters)
