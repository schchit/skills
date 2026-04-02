/**
 * DNS and domain analysis utilities
 * Using Node.js built-in dns module for queries
 */

import { promises as dns } from 'dns';
import { createConnection } from 'net';
import { connect as tlsConnect } from 'tls';

/**
 * Query DNS A records
 */
export async function getARecords(domain) {
  try {
    const records = await dns.resolve4(domain);
    return records;
  } catch (error) {
    return [];
  }
}

/**
 * Query DNS MX records (mail server)
 */
export async function getMXRecords(domain) {
  try {
    const records = await dns.resolveMx(domain);
    return records || [];
  } catch (error) {
    return [];
  }
}

/**
 * Query DNS NS records (nameservers)
 */
export async function getNSRecords(domain) {
  try {
    const records = await dns.resolveNs(domain);
    return records || [];
  } catch (error) {
    return [];
  }
}

/**
 * Query DNS TXT records (SPF, DKIM, DMARC)
 */
export async function getTXTRecords(domain) {
  try {
    const records = await dns.resolveTxt(domain);
    return records.map(r => r.join(''));
  } catch (error) {
    return [];
  }
}

/**
 * Check for SPF record
 */
export async function hasSPF(domain) {
  const txtRecords = await getTXTRecords(domain);
  return txtRecords.some(record => record.toLowerCase().startsWith('v=spf1'));
}

/**
 * Check for DMARC record
 */
export async function hasDMARC(domain) {
  try {
    const txtRecords = await getTXTRecords(`_dmarc.${domain}`);
    return txtRecords.some(record => record.toLowerCase().startsWith('v=dmarc1'));
  } catch (error) {
    return false;
  }
}

/**
 * Check for DKIM record
 */
export async function hasDKIM(domain) {
  try {
    // Common DKIM selector
    const selectors = ['default', 'selector1', 'selector2', 'google', 'k1', 'mail'];
    for (const selector of selectors) {
      try {
        const txtRecords = await getTXTRecords(`${selector}._domainkey.${domain}`);
        if (txtRecords.some(record => record.includes('v=DKIM1'))) {
          return true;
        }
      } catch (e) {
        // Continue to next selector
      }
    }
    return false;
  } catch (error) {
    return false;
  }
}

/**
 * Get SSL certificate information
 */
export function getSSLCertificate(domain, port = 443) {
  return new Promise((resolve) => {
    const options = {
      host: domain,
      port: port,
      method: 'GET',
      rejectUnauthorized: false, // Allow self-signed certs
    };

    let resolved = false;

    const socket = tlsConnect(options, function() {
      if (resolved) return;

      const cert = socket.getPeerCertificate();
      socket.destroy();

      if (!cert || Object.keys(cert).length === 0) {
        resolved = true;
        resolve(null);
        return;
      }

      resolved = true;
      resolve({
        subject: cert.subject || {},
        issuer: cert.issuer || {},
        valid_from: cert.valid_from,
        valid_to: cert.valid_to,
        subjectAltName: cert.subjectAltName || '',
        issuerCommonName: cert.issuer?.CN,
        isSelfSigned: cert.fingerprint === cert.fingerprint256,
      });
    });

    socket.on('error', () => {
      if (!resolved) {
        resolved = true;
        resolve(null);
      }
    });

    socket.on('timeout', () => {
      socket.destroy();
      if (!resolved) {
        resolved = true;
        resolve(null);
      }
    });

    socket.setTimeout(3000, () => {
      socket.destroy();
      if (!resolved) {
        resolved = true;
        resolve(null);
      }
    });
  });
}

/**
 * Check if SSL certificate is from Let's Encrypt
 */
export async function isLetSEncryptCert(domain) {
  const cert = await getSSLCertificate(domain);
  if (!cert) return false;
  const issuer = cert.issuerCommonName || cert.issuer?.CN || '';
  return issuer.toLowerCase().includes("let's encrypt");
}

/**
 * Check if domain exists (has DNS records)
 */
export async function domainExists(domain) {
  try {
    const records = await getARecords(domain);
    return records.length > 0;
  } catch (error) {
    return false;
  }
}

/**
 * Get reverse DNS (PTR record)
 */
export async function getReverseDNS(ip) {
  try {
    const hostname = await dns.reverse(ip);
    return hostname;
  } catch (error) {
    return [];
  }
}

/**
 * Get DNS CNAME record
 */
export async function getCNAME(domain) {
  try {
    const records = await dns.resolveCname(domain);
    return records || [];
  } catch (error) {
    return [];
  }
}

/**
 * Get SOA record (Start of Authority)
 */
export async function getSOA(domain) {
  try {
    const records = await dns.resolveSoa(domain);
    return records;
  } catch (error) {
    return null;
  }
}

/**
 * Comprehensive DNS check
 */
export async function completeDNSCheck(domain) {
  const [aRecords, mxRecords, nsRecords, txtRecords, spf, dmarc, dkim, soa] = await Promise.all([
    getARecords(domain),
    getMXRecords(domain),
    getNSRecords(domain),
    getTXTRecords(domain),
    hasSPF(domain),
    hasDMARC(domain),
    hasDKIM(domain),
    getSOA(domain),
  ]);

  return {
    a_records: aRecords,
    mx_records: mxRecords.map(r => r.exchange),
    ns_records: nsRecords,
    txt_records: txtRecords,
    has_spf: spf,
    has_dmarc: dmarc,
    has_dkim: dkim,
    soa: soa,
  };
}

/**
 * Extract hosting country from IP (basic implementation)
 * Returns likely country code based on IP ranges (simplified)
 */
export function getCountryFromIP(ip) {
  // This is a very simplified version
  // In production, you'd use a GeoIP database like MaxMind
  if (!ip) return 'UNKNOWN';

  const parts = ip.split('.').map(Number);
  const firstOctet = parts[0];

  // Very basic mapping (not accurate for production)
  if (firstOctet >= 1 && firstOctet <= 9) return 'US';
  if (firstOctet >= 10 && firstOctet <= 11) return 'PRIVATE';
  if (firstOctet >= 185 && firstOctet <= 187) return 'RU';
  if (firstOctet >= 178 && firstOctet <= 182) return 'RU';
  if (firstOctet >= 203 && firstOctet <= 204) return 'CN';

  return 'UNKNOWN';
}
