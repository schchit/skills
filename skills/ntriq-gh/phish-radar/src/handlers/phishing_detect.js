/**
 * Phishing Detection Handler
 * Analyzes URLs/domains for phishing indicators
 */

import { URL } from 'url';
import { getBrandInfo, KNOWN_BRANDS } from '../data/known_brands.js';
import { getTLDRisk } from '../data/suspicious_tlds.js';
import {
  getARecords,
  getMXRecords,
  getSSLCertificate,
  isLetSEncryptCert,
  getSOA,
  getCountryFromIP,
} from '../utils/dns_client.js';
import { levenshteinDistance, countHomoglyphSubstitutions } from '../utils/levenshtein.js';

/**
 * Extract domain from URL
 */
function extractDomain(urlOrDomain) {
  try {
    if (urlOrDomain.startsWith('http://') || urlOrDomain.startsWith('https://')) {
      return new URL(urlOrDomain).hostname;
    }
    return urlOrDomain;
  } catch (error) {
    return urlOrDomain;
  }
}

/**
 * Extract TLD from domain
 */
function extractTLD(domain) {
  const parts = domain.split('.');
  if (parts.length >= 2) {
    return parts[parts.length - 1];
  }
  return '';
}

/**
 * Calculate domain age in days
 */
async function calculateDomainAge(domain) {
  try {
    const soa = await getSOA(domain);
    if (soa && soa.serial) {
      // SOA serial is often the date, but not always
      // More reliable: check certificate or use WHOIS
      // For now, return null as we need real WHOIS data
      return null;
    }
    return null;
  } catch (error) {
    return null;
  }
}

/**
 * Normalize domain name for comparison (remove hyphens, numbers, special chars)
 * Processes each hyphen-separated segment separately
 */
function normalizeDomainName(domain) {
  // Split by hyphen and process each segment
  const segments = domain.toLowerCase().split('-');
  return segments.map(seg => seg.replace(/\d/g, '')).join('');
}

/**
 * Check for typosquatting against known brands
 */
function checkTyposquat(domain) {
  const results = {
    typosquat_of: null,
    typosquat_distance: null,
    homoglyph_detected: false,
    homoglyph_count: 0,
  };

  const domainWithoutTld = domain.split('.')[0].toLowerCase();
  const segments = domainWithoutTld.split('-'); // Split by hyphen for multi-part domains
  const normalizedDomain = normalizeDomainName(domainWithoutTld);

  // Check against all known brands
  for (const [brandDomain, brandInfo] of Object.entries(KNOWN_BRANDS)) {
    const brandName = brandDomain.split('.')[0].toLowerCase();

    // Check original domain
    let distance = levenshteinDistance(domainWithoutTld, brandName);
    let minDistance = distance;

    // Check individual segments (for hyphenated domains like paypa1-secure)
    for (const segment of segments) {
      const segmentNormalized = segment.replace(/\d/g, '');
      const segDist = levenshteinDistance(segmentNormalized, brandName);
      if (segDist < minDistance) {
        minDistance = segDist;
      }
    }

    // Check normalized version
    const normalizedDistance = levenshteinDistance(normalizedDomain, brandName);
    if (normalizedDistance < minDistance) {
      minDistance = normalizedDistance;
    }

    if (minDistance <= 2 && minDistance > 0) {
      results.typosquat_of = brandDomain;
      results.typosquat_distance = minDistance;
      break; // Found a match, stop searching
    }

    // Homoglyph detection
    if (domainWithoutTld.length === brandName.length) {
      const homoglyphCount = countHomoglyphSubstitutions(brandName, domainWithoutTld);
      if (homoglyphCount > 0 && distance <= 2) {
        results.homoglyph_detected = true;
        results.homoglyph_count = homoglyphCount;
      }
    }
  }

  return results;
}

/**
 * Main phishing detection function
 */
export async function phishingDetect(urlOrDomain) {
  const domain = extractDomain(urlOrDomain);
  const tld = extractTLD(domain);

  try {
    // Parallel DNS queries
    const [aRecords, mxRecords, sslCert, isLetEncrypt] = await Promise.all([
      getARecords(domain).catch(() => []),
      getMXRecords(domain).catch(() => []),
      getSSLCertificate(domain).catch(() => null),
      isLetSEncryptCert(domain).catch(() => false),
    ]);

    // Build signal analysis
    const signals = {
      typosquat_of: null,
      typosquat_distance: null,
      homoglyph_detected: false,
      homoglyph_count: 0,
      domain_age_days: null,
      ssl_issuer: null,
      ssl_free_cert: false,
      has_mx_records: mxRecords.length > 0,
      suspicious_tld: getTLDRisk(tld).risk === 'HIGH',
      dns_a_records: aRecords,
      hosting_country: aRecords.length > 0 ? getCountryFromIP(aRecords[0]) : 'UNKNOWN',
      domain_exists: aRecords.length > 0,
      has_ssl: !!sslCert,
    };

    // Check typosquatting
    const typosquatResult = checkTyposquat(domain);
    Object.assign(signals, typosquatResult);

    // Get SSL certificate info
    if (sslCert) {
      signals.ssl_issuer = sslCert.issuerCommonName || sslCert.issuer?.CN || 'Unknown';
      signals.ssl_free_cert = isLetEncrypt;
    }

    // Calculate phishing score (0-100)
    let phishingScore = 0;

    // High-risk signals
    if (signals.typosquat_distance === 1) phishingScore += 35; // Strong indicator
    if (signals.typosquat_distance === 2) phishingScore += 25;
    if (signals.homoglyph_detected) phishingScore += 20;
    if (signals.suspicious_tld) phishingScore += 15;
    if (signals.ssl_free_cert && signals.typosquat_of) phishingScore += 15; // Free cert + typosquat
    if (!signals.has_mx_records && signals.typosquat_of) phishingScore += 10;
    if (signals.hosting_country === 'RU' && signals.typosquat_of) phishingScore += 10;
    if (!signals.domain_exists && signals.typosquat_of) phishingScore += 15; // Non-existent domain with brand similarity

    // Reduce score for legitimate indicators
    if (signals.has_mx_records && !signals.typosquat_of) phishingScore -= 5;
    if (!signals.ssl_free_cert && signals.ssl_issuer !== 'Unknown' && !signals.typosquat_of) phishingScore -= 5;

    // Clamp score
    phishingScore = Math.max(0, Math.min(100, phishingScore));

    // Determine verdict and confidence
    let verdict = 'SAFE';
    let confidence = 0;

    if (phishingScore >= 70) {
      verdict = 'PHISHING';
      confidence = Math.min(0.99, (phishingScore - 70) / 30 + 0.7);
    } else if (phishingScore >= 40) {
      verdict = 'SUSPICIOUS';
      confidence = Math.min(0.95, (phishingScore - 40) / 30 + 0.5);
    } else {
      verdict = 'SAFE';
      confidence = Math.min(0.95, (100 - phishingScore) / 100);
    }

    // Determine action
    const action = verdict === 'PHISHING' ? 'BLOCK' : verdict === 'SUSPICIOUS' ? 'REVIEW' : 'ALLOW';

    // Build details message
    const details = buildDetailsMessage(verdict, signals, phishingScore);

    return {
      url: urlOrDomain,
      domain,
      verdict,
      confidence: Math.round(confidence * 100) / 100,
      phishing_score: phishingScore,
      signals,
      action,
      details,
    };
  } catch (error) {
    console.error(`Phishing detection error for ${domain}:`, error);
    return {
      url: urlOrDomain,
      domain,
      verdict: 'ERROR',
      confidence: 0,
      phishing_score: 0,
      signals: {},
      action: 'REVIEW',
      details: `Error during analysis: ${error.message}`,
      error: error.message,
    };
  }
}

/**
 * Build human-readable details message
 */
function buildDetailsMessage(verdict, signals, score) {
  const parts = [];

  if (verdict === 'PHISHING') {
    parts.push(`High-confidence phishing domain detected (score: ${score}).`);

    if (signals.typosquat_of) {
      parts.push(`Domain is a typosquat of ${signals.typosquat_of} (distance: ${signals.typosquat_distance}).`);
    }

    if (signals.homoglyph_detected) {
      parts.push(`Contains ${signals.homoglyph_count} homoglyph character substitutions.`);
    }

    if (signals.ssl_free_cert) {
      parts.push('Uses free SSL certificate (Let\'s Encrypt) - commonly abused.');
    }

    if (!signals.has_mx_records && signals.typosquat_of) {
      parts.push('No MX records configured - not set up for legitimate email.');
    }

    if (signals.suspicious_tld) {
      parts.push(`Registered under suspicious TLD (${signals.dns_a_records?.[0] ? getTLDRisk(signals.dns_a_records[0].split('.').pop()).reason : 'high-risk'})`);
    }
  } else if (verdict === 'SUSPICIOUS') {
    parts.push(`Suspicious domain characteristics detected (score: ${score}).`);

    if (signals.typosquat_of) {
      parts.push(`Resembles legitimate domain ${signals.typosquat_of}.`);
    }

    if (signals.suspicious_tld) {
      parts.push('Registered under high-risk TLD.');
    }

    if (signals.ssl_free_cert && signals.typosquat_of) {
      parts.push('Uses free SSL certificate with domain similarity.');
    }
  } else {
    parts.push('Domain appears legitimate based on current analysis.');

    if (signals.has_mx_records) {
      parts.push('Has proper MX records configured.');
    }

    if (signals.has_ssl && !signals.ssl_free_cert) {
      parts.push(`Signed by trusted CA: ${signals.ssl_issuer}`);
    }
  }

  return parts.join(' ');
}
