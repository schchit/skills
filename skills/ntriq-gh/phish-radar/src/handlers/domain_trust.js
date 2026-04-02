/**
 * Domain Trust Score Handler
 * Calculate domain trustworthiness (0-100)
 */

import { getTLDRisk } from '../data/suspicious_tlds.js';
import {
  completeDNSCheck,
  getSSLCertificate,
  isLetSEncryptCert,
  getNSRecords,
} from '../utils/dns_client.js';

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
 * Categorize SSL certificate type
 */
function categorizeSSLType(cert) {
  if (!cert) return 'NONE';

  const subject = cert.subject || {};
  const cn = subject.CN || '';

  // EV (Extended Validation) - would have specific markers
  if (subject.O && subject.C && cn) {
    return 'EV';
  }

  // OV (Organization Validation) - has organization
  if (subject.O) {
    return 'OV';
  }

  // DV (Domain Validation) - only domain, most common for attacks
  if (cn) {
    return 'DV';
  }

  return 'UNKNOWN';
}

/**
 * Analyze nameserver reputation
 */
function analyzeNameservers(nsRecords) {
  const trustworthy = [
    'ns.google.com',
    'ns.cloudflare.com',
    'ns1.digitalocean.com',
    'ns.aws.com',
    'ns.azure.com',
  ];

  const suspicious = [
    'cheap-hosting',
    'spam-host',
    'bulletproof-hosting',
    'bulletproof',
    'free-dns',
  ];

  let trustScore = 0;
  let suspiciousFlags = 0;

  for (const ns of nsRecords) {
    const nsLower = ns.toLowerCase();

    if (trustworthy.some(t => nsLower.includes(t))) {
      trustScore += 15;
    }

    if (suspicious.some(s => nsLower.includes(s))) {
      suspiciousFlags += 20;
    }
  }

  return {
    trust_adjustment: trustScore,
    suspicious_count: suspiciousFlags,
  };
}

/**
 * Main domain trust calculation
 */
export async function domainTrust(domain) {
  const tld = extractTLD(domain);

  try {
    // Run all checks in parallel
    const [dnsData, sslCert, isLetEncrypt, nsRecords] = await Promise.all([
      completeDNSCheck(domain),
      getSSLCertificate(domain),
      isLetSEncryptCert(domain),
      getNSRecords(domain),
    ]);

    // Build factors object
    const factors = {
      domain_age_days: null, // Would require WHOIS API
      has_mx: dnsData.mx_records.length > 0,
      has_spf: dnsData.has_spf,
      has_dkim: dnsData.has_dkim,
      has_dmarc: dnsData.has_dmarc,
      ssl_type: categorizeSSLType(sslCert),
      ssl_issuer: sslCert?.issuerCommonName || sslCert?.issuer?.CN || 'None',
      has_ssl: !!sslCert,
      tld_risk: getTLDRisk(tld).risk,
      nameservers: nsRecords,
      a_records_count: dnsData.a_records.length,
    };

    // Calculate trust score (0-100)
    let trustScore = 50; // Start at neutral

    // Email infrastructure (25 points possible)
    if (factors.has_mx) trustScore += 10;
    if (factors.has_spf) trustScore += 5;
    if (factors.has_dkim) trustScore += 5;
    if (factors.has_dmarc) trustScore += 5;

    // SSL Certificate (20 points possible)
    if (factors.has_ssl) {
      trustScore += 8;
      if (factors.ssl_type === 'EV') {
        trustScore += 12;
      } else if (factors.ssl_type === 'OV') {
        trustScore += 8;
      } else if (factors.ssl_type === 'DV') {
        trustScore += 4;
        if (isLetEncrypt) {
          trustScore -= 2; // Slight deduction for free cert
        }
      }
    }

    // TLD Risk (20 points possible)
    if (factors.tld_risk === 'HIGH') {
      trustScore -= 15;
    } else if (factors.tld_risk === 'MEDIUM') {
      trustScore -= 8;
    } else {
      trustScore += 10;
    }

    // Nameserver analysis (15 points possible)
    const nsAnalysis = analyzeNameservers(nsRecords);
    trustScore += nsAnalysis.trust_adjustment;
    trustScore -= nsAnalysis.suspicious_count;

    // DNS records
    if (factors.a_records_count > 0) {
      trustScore += 5;
    }

    // Clamp score
    trustScore = Math.max(0, Math.min(100, trustScore));

    // Determine trust level
    let trustLevel = 'UNTRUSTED';
    if (trustScore >= 80) {
      trustLevel = 'HIGHLY_TRUSTED';
    } else if (trustScore >= 60) {
      trustLevel = 'TRUSTED';
    } else if (trustScore >= 40) {
      trustLevel = 'NEUTRAL';
    } else if (trustScore >= 20) {
      trustLevel = 'SUSPICIOUS';
    }

    return {
      domain,
      trust_score: trustScore,
      trust_level: trustLevel,
      factors,
    };
  } catch (error) {
    console.error(`Domain trust calculation error for ${domain}:`, error);
    return {
      domain,
      trust_score: 0,
      trust_level: 'UNKNOWN',
      error: error.message,
      factors: {},
    };
  }
}
