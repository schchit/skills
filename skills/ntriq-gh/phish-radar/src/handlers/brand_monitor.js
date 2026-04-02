/**
 * Brand Monitor Handler
 * Detect lookalike domains (typosquats, homoglyphs, keyword additions)
 */

import { domainExists } from '../utils/dns_client.js';
import { getTLDRisk } from '../data/suspicious_tlds.js';
import { levenshteinDistance } from '../utils/levenshtein.js';

/**
 * Extract domain name and TLD
 */
function extractParts(brandDomain) {
  const parts = brandDomain.toLowerCase().split('.');
  if (parts.length < 2) {
    return { domain: brandDomain, tld: '' };
  }

  const tld = parts[parts.length - 1];
  const domain = parts.slice(0, -1).join('');

  return { domain, tld };
}

/**
 * Generate typosquat candidates
 */
function generateTyposquatCandidates(domain) {
  const candidates = [];

  // Single character substitutions (homoglyphs and similar)
  const substitutions = {
    'a': ['e', '4', '@'],
    'e': ['a', '3'],
    'i': ['1', 'l', '!'],
    'l': ['1', 'i'],
    'o': ['0', ''],
    's': ['5', 'z', '$'],
    'z': ['2', 's'],
    'b': ['8', 'd'],
    'g': ['9', 'q'],
  };

  for (let i = 0; i < domain.length; i++) {
    const char = domain[i];
    if (substitutions[char]) {
      for (const sub of substitutions[char]) {
        const candidate = domain.substring(0, i) + sub + domain.substring(i + 1);
        candidates.push({
          domain: candidate,
          type: 'homoglyph',
        });
      }
    }
  }

  // Single character deletions
  for (let i = 0; i < domain.length; i++) {
    candidates.push({
      domain: domain.substring(0, i) + domain.substring(i + 1),
      type: 'deletion',
    });
  }

  // Single character insertions (common extra chars)
  const insertChars = ['e', 'a', 'o', 'n', 'r', 's'];
  for (let i = 0; i <= domain.length; i++) {
    for (const char of insertChars) {
      candidates.push({
        domain: domain.substring(0, i) + char + domain.substring(i),
        type: 'insertion',
      });
    }
  }

  // Keyword additions (common attack pattern)
  const keywords = [
    'secure',
    'login',
    'verify',
    'confirm',
    'update',
    'admin',
    'support',
    'official',
    'real',
    'my',
    'get',
    'access',
    'check',
    'auth',
    'pay',
    'account',
  ];

  for (const keyword of keywords) {
    candidates.push({
      domain: keyword + domain,
      type: 'keyword_addition',
    });
    candidates.push({
      domain: domain + keyword,
      type: 'keyword_addition',
    });
  }

  // Adjacent key swaps
  for (let i = 0; i < domain.length - 1; i++) {
    candidates.push({
      domain: domain.substring(0, i) + domain[i + 1] + domain[i] + domain.substring(i + 2),
      type: 'transposition',
    });
  }

  return candidates;
}

/**
 * Generate TLD variations
 */
function generateTLDVariations() {
  return [
    'com', 'net', 'org', 'io', 'co', 'uk', 'ru', 'xyz', 'top', 'click',
    'app', 'dev', 'site', 'online', 'shop', 'store', 'cc', 'ws',
  ];
}

/**
 * Assess risk level of a lookalike domain
 */
function assessRisk(original, lookalike, type) {
  let risk = 'LOW';

  const distance = levenshteinDistance(original, lookalike);

  // Homoglyphs are very dangerous
  if (type === 'homoglyph') {
    risk = 'HIGH';
  }
  // Very close matches are dangerous
  else if (distance === 1) {
    risk = 'HIGH';
  }
  // Keyword additions (especially security-related) are dangerous
  else if (type === 'keyword_addition') {
    const keywords = ['login', 'verify', 'secure', 'confirm', 'update'];
    if (keywords.some(k => lookalike.includes(k))) {
      risk = 'HIGH';
    } else {
      risk = 'MEDIUM';
    }
  }
  // Single character deletions/insertions
  else if (distance === 1 || type === 'deletion' || type === 'insertion') {
    risk = 'MEDIUM';
  }
  // Transpositions are less dangerous
  else if (type === 'transposition') {
    risk = 'MEDIUM';
  }

  return risk;
}

/**
 * Main brand monitoring function
 */
export async function brandMonitor(brandDomain, limit = 20) {
  const { domain: brandName, tld: originalTld } = extractParts(brandDomain);

  try {
    // Generate candidates
    const candidates = generateTyposquatCandidates(brandName);
    const tldVariations = generateTLDVariations();

    // Expand to include TLD variations
    const allCandidates = [];
    for (const candidate of candidates) {
      // Test with multiple TLDs
      for (const tld of tldVariations) {
        allCandidates.push({
          domain: `${candidate.domain}.${tld}`,
          base: candidate.domain,
          tld,
          type: candidate.type,
        });
      }
    }

    // Check which domains actually exist (have DNS records)
    const existingDomains = [];

    // Limit concurrent checks to avoid overwhelming DNS
    const batchSize = 10;
    for (let i = 0; i < allCandidates.length && existingDomains.length < limit; i += batchSize) {
      const batch = allCandidates.slice(i, i + batchSize);

      const results = await Promise.allSettled(
        batch.map(async (candidate) => {
          const exists = await domainExists(candidate.domain);
          return { ...candidate, exists };
        }),
      );

      for (const result of results) {
        if (result.status === 'fulfilled' && result.value.exists) {
          existingDomains.push(result.value);
        }
      }
    }

    // Assess risk and prepare output
    const lookalikes = existingDomains
      .slice(0, limit)
      .map((d) => {
        const tldRisk = getTLDRisk(d.tld);
        let risk = assessRisk(brandName, d.base, d.type);

        // Increase risk if using suspicious TLD
        if (tldRisk.risk === 'HIGH') {
          risk = 'HIGH';
        }

        return {
          domain: d.domain,
          exists: true,
          risk,
          type: d.type,
          tld_risk: tldRisk.risk,
        };
      })
      .sort((a, b) => {
        // Sort by risk level
        const riskOrder = { HIGH: 0, MEDIUM: 1, LOW: 2 };
        return riskOrder[a.risk] - riskOrder[b.risk];
      });

    return {
      brand: brandDomain,
      brand_name: brandName,
      lookalikes_found: lookalikes.length,
      domains: lookalikes,
      analysis_time_ms: Date.now(),
    };
  } catch (error) {
    console.error(`Brand monitor error for ${brandDomain}:`, error);
    return {
      brand: brandDomain,
      lookalikes_found: 0,
      domains: [],
      error: error.message,
    };
  }
}
