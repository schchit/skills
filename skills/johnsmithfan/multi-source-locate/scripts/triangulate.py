#!/usr/bin/env python3
"""
Weighted triangulation module.
Combines multiple location estimates into a single best estimate.
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass
class LocationEstimate:
    """A single location estimate from one source."""
    latitude: float
    longitude: float
    accuracy: float  # meters (1 sigma)
    method: str
    weight: float = 0.0
    timestamp: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class TriangulatedLocation:
    """Combined location from multiple sources."""
    latitude: float
    longitude: float
    accuracy: float  # meters
    confidence: float  # 0.0 to 1.0
    method: str
    sources: Dict[str, Dict[str, Any]]
    timestamp: str
    disagreement: float  # meters - max distance between sources


def triangulate(
    estimates: List[LocationEstimate],
    weights: Optional[Dict[str, float]] = None
) -> TriangulatedLocation:
    """
    Combine multiple location estimates using weighted average.
    
    Args:
        estimates: List of location estimates from different sources
        weights: Optional manual weights per method (overrides accuracy-based)
    
    Returns:
        TriangulatedLocation with combined estimate and confidence
    """
    if not estimates:
        raise ValueError("No location estimates provided")
    
    # Single source case
    if len(estimates) == 1:
        est = estimates[0]
        return TriangulatedLocation(
            latitude=est.latitude,
            longitude=est.longitude,
            accuracy=est.accuracy,
            confidence=_single_source_confidence(est),
            method=est.method,
            sources={est.method: _estimate_to_dict(est)},
            timestamp=est.timestamp or datetime.now(timezone.utc).isoformat(),
            disagreement=0.0
        )
    
    # Calculate weights
    for est in estimates:
        if weights and est.method in weights:
            est.weight = weights[est.method]
        else:
            # Weight based on inverse variance (1/accuracy^2)
            est.weight = 1.0 / (est.accuracy ** 2)
    
    # Normalize weights
    total_weight = sum(est.weight for est in estimates)
    
    # Calculate weighted centroid
    weighted_lat = sum(est.latitude * est.weight for est in estimates) / total_weight
    weighted_lon = sum(est.longitude * est.weight for est in estimates) / total_weight
    
    # Calculate disagreement (max distance from centroid)
    max_disagreement = 0.0
    for est in estimates:
        dist = haversine_distance(
            est.latitude, est.longitude,
            weighted_lat, weighted_lon
        )
        max_disagreement = max(max_disagreement, dist)
    
    # Estimate combined accuracy
    # Use the minimum accuracy of sources, but increase if sources disagree
    best_accuracy = min(est.accuracy for est in estimates)
    
    # If sources disagree more than the best accuracy, increase uncertainty
    if max_disagreement > best_accuracy:
        combined_accuracy = math.sqrt(best_accuracy ** 2 + (max_disagreement / 2) ** 2)
    else:
        combined_accuracy = best_accuracy
    
    # Calculate confidence score
    confidence = _calculate_confidence(
        estimates, weighted_lat, weighted_lon, 
        combined_accuracy, max_disagreement
    )
    
    # Build sources dict
    sources = {}
    for est in estimates:
        sources[est.method] = {
            'lat': est.latitude,
            'lon': est.longitude,
            'accuracy': est.accuracy,
            'weight': est.weight / total_weight
        }
    
    return TriangulatedLocation(
        latitude=weighted_lat,
        longitude=weighted_lon,
        accuracy=combined_accuracy,
        confidence=confidence,
        method='triangulated',
        sources=sources,
        timestamp=datetime.now(timezone.utc).isoformat(),
        disagreement=max_disagreement
    )


def _single_source_confidence(est: LocationEstimate) -> float:
    """Calculate confidence for a single source."""
    # Base confidence by method
    method_confidence = {
        'gps': 0.9,
        'wifi': 0.7,
        'cellular': 0.5,
        'ip': 0.3,
    }
    
    base = method_confidence.get(est.method, 0.5)
    
    # Adjust by accuracy
    if est.accuracy <= 10:
        return min(base + 0.05, 0.95)
    elif est.accuracy <= 50:
        return base
    elif est.accuracy <= 500:
        return base * 0.9
    else:
        return base * 0.7


def _calculate_confidence(
    estimates: List[LocationEstimate],
    center_lat: float,
    center_lon: float,
    combined_accuracy: float,
    disagreement: float
) -> float:
    """
    Calculate confidence score for combined result.
    
    Factors:
    - Number of sources (more = better)
    - Agreement between sources (less disagreement = better)
    - Quality of sources (GPS > WiFi > Cellular > IP)
    """
    # Source count factor (max at 4 sources)
    source_factor = min(len(estimates) / 4.0, 1.0)
    
    # Method quality factor
    method_scores = {
        'gps': 1.0,
        'wifi': 0.8,
        'cellular': 0.6,
        'ip': 0.4,
    }
    
    # Weighted average of method scores
    total_weight = sum(est.weight for est in estimates)
    method_factor = sum(
        method_scores.get(est.method, 0.5) * est.weight 
        for est in estimates
    ) / total_weight
    
    # Agreement factor
    # Perfect agreement = 1.0, disagreement > accuracy = reduced
    if combined_accuracy > 0:
        agreement_factor = max(0.0, 1.0 - disagreement / (combined_accuracy * 3))
    else:
        agreement_factor = 1.0
    
    # Accuracy factor
    # Better accuracy = higher confidence
    if combined_accuracy <= 10:
        accuracy_factor = 1.0
    elif combined_accuracy <= 100:
        accuracy_factor = 0.9
    elif combined_accuracy <= 1000:
        accuracy_factor = 0.7
    else:
        accuracy_factor = 0.5
    
    # Combine factors
    confidence = (
        source_factor * 0.25 +
        method_factor * 0.30 +
        agreement_factor * 0.25 +
        accuracy_factor * 0.20
    )
    
    return min(max(confidence, 0.0), 1.0)


def haversine_distance(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> float:
    """
    Calculate the great-circle distance between two points.
    
    Args:
        lat1, lon1: First point (degrees)
        lat2, lon2: Second point (degrees)
    
    Returns:
        Distance in meters
    """
    R = 6371000  # Earth radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def bearing(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> float:
    """
    Calculate the bearing from point 1 to point 2.
    
    Returns:
        Bearing in degrees (0-360)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)
    
    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
    
    theta = math.atan2(x, y)
    
    return (math.degrees(theta) + 360) % 360


def destination_point(
    lat: float, lon: float,
    distance: float, bearing_deg: float
) -> Tuple[float, float]:
    """
    Calculate destination point given start, distance, and bearing.
    
    Args:
        lat, lon: Start point (degrees)
        distance: Distance in meters
        bearing_deg: Bearing in degrees
    
    Returns:
        (lat, lon) of destination point
    """
    R = 6371000  # Earth radius in meters
    
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    brng_rad = math.radians(bearing_deg)
    
    delta = distance / R
    
    dest_lat = math.asin(
        math.sin(lat_rad) * math.cos(delta) +
        math.cos(lat_rad) * math.sin(delta) * math.cos(brng_rad)
    )
    
    dest_lon = lon_rad + math.atan2(
        math.sin(brng_rad) * math.sin(delta) * math.cos(lat_rad),
        math.cos(delta) - math.sin(lat_rad) * math.sin(dest_lat)
    )
    
    return math.degrees(dest_lat), math.degrees(dest_lon)


def _estimate_to_dict(est: LocationEstimate) -> Dict[str, Any]:
    """Convert estimate to dict for output."""
    d = {
        'lat': est.latitude,
        'lon': est.longitude,
        'accuracy': est.accuracy,
    }
    if est.raw_data:
        d.update(est.raw_data)
    return d


if __name__ == '__main__':
    # Test triangulation
    print("Testing triangulation...\n")
    
    # Simulate multiple sources
    estimates = [
        LocationEstimate(
            latitude=39.9045,
            longitude=116.4071,
            accuracy=5,
            method='gps'
        ),
        LocationEstimate(
            latitude=39.9039,
            longitude=116.4078,
            accuracy=30,
            method='wifi'
        ),
        LocationEstimate(
            latitude=39.9042,
            longitude=116.4074,
            accuracy=5000,
            method='ip'
        ),
    ]
    
    result = triangulate(estimates)
    
    print(f"Combined location:")
    print(f"  Latitude:  {result.latitude:.6f}")
    print(f"  Longitude: {result.longitude:.6f}")
    print(f"  Accuracy:  {result.accuracy:.1f} meters")
    print(f"  Confidence: {result.confidence:.0%}")
    print(f"  Disagreement: {result.disagreement:.1f} meters")
    print(f"\nSources:")
    for method, data in result.sources.items():
        print(f"  {method}: ({data['lat']:.4f}, {data['lon']:.4f}) ±{data['accuracy']:.0f}m (weight: {data['weight']:.2f})")
