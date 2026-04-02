/**
 * Suspicious TLDs commonly used in phishing attacks
 * Focus on cheap/free TLDs that attract bad actors
 */

export const SUSPICIOUS_TLDS = {
  // Generic cheap TLDs (high abuse)
  'xyz': { risk: 'HIGH', reason: 'Commonly abused, cheap registration' },
  'top': { risk: 'HIGH', reason: 'Commonly abused, cheap registration' },
  'click': { risk: 'HIGH', reason: 'Commonly abused, cheap registration' },
  'bid': { risk: 'HIGH', reason: 'Commonly abused, cheap registration' },
  'download': { risk: 'HIGH', reason: 'Commonly abused, cheap registration' },
  'trade': { risk: 'HIGH', reason: 'Commonly abused, cheap registration' },
  'gdn': { risk: 'HIGH', reason: 'Generic domain network, high abuse' },
  'party': { risk: 'HIGH', reason: 'Commonly abused' },
  'win': { risk: 'HIGH', reason: 'Commonly abused' },
  'racing': { risk: 'HIGH', reason: 'Commonly abused' },
  'men': { risk: 'HIGH', reason: 'Commonly abused' },
  'stream': { risk: 'HIGH', reason: 'Commonly abused' },
  'date': { risk: 'HIGH', reason: 'Commonly abused' },
  'webcam': { risk: 'HIGH', reason: 'Commonly abused' },
  'space': { risk: 'HIGH', reason: 'Commonly abused' },
  'ru': { risk: 'HIGH', reason: 'High concentration of malicious actors' },
  'su': { risk: 'HIGH', reason: 'High concentration of malicious actors' },
  'cc': { risk: 'HIGH', reason: 'Often used for phishing, impersonation' },
  'tk': { risk: 'HIGH', reason: 'Free registration, high abuse' },
  'ml': { risk: 'HIGH', reason: 'Free registration, high abuse' },
  'ga': { risk: 'HIGH', reason: 'Free registration, high abuse' },
  'cf': { risk: 'HIGH', reason: 'Free registration, high abuse' },

  // Typosquat-prone TLDs
  'pw': { risk: 'MEDIUM', reason: 'Password related, sometimes typosquatted' },
  'io': { risk: 'LOW', reason: 'Legitimate tech TLD, some abuse' },
  'co': { risk: 'LOW', reason: 'Legitimate country code, some abuse' },
  'app': { risk: 'LOW', reason: 'Legitimate extension, some abuse' },
  'dev': { risk: 'LOW', reason: 'Legitimate dev community, some abuse' },
  'cloud': { risk: 'LOW', reason: 'Legitimate extension, some abuse' },
  'shop': { risk: 'LOW', reason: 'Legitimate commerce TLD, some abuse' },
  'online': { risk: 'LOW', reason: 'Generic extension, some abuse' },
  'site': { risk: 'LOW', reason: 'Generic extension, some abuse' },
  'services': { risk: 'LOW', reason: 'Generic extension, some abuse' },

  // Cryptocurrency-related (increased risk for scams)
  'btc': { risk: 'MEDIUM', reason: 'Cryptocurrency, attracts scams' },
  'eth': { risk: 'MEDIUM', reason: 'Cryptocurrency, attracts scams' },
  'coin': { risk: 'MEDIUM', reason: 'Cryptocurrency, attracts scams' },
  'crypto': { risk: 'MEDIUM', reason: 'Cryptocurrency, attracts scams' },
  'nft': { risk: 'MEDIUM', reason: 'NFT/crypto, attracts scams' },

  // Country codes with reputation issues
  'ir': { risk: 'HIGH', reason: 'Iran, sanctions concerns' },
  'kp': { risk: 'HIGH', reason: 'North Korea, sanctions concerns' },
  'sy': { risk: 'HIGH', reason: 'Syria, sanctions concerns' },
  'cu': { risk: 'HIGH', reason: 'Cuba, sanctions concerns' },
  'pk': { risk: 'MEDIUM', reason: 'Pakistan, higher phishing activity' },
  'nl': { risk: 'LOW', reason: 'Netherlands, mostly legitimate' },
  'de': { risk: 'LOW', reason: 'Germany, mostly legitimate' },
  'ch': { risk: 'LOW', reason: 'Switzerland, mostly legitimate' },
};

/**
 * Get risk level for a TLD
 */
export function getTLDRisk(tld) {
  const normalizedTld = tld.toLowerCase().replace(/^\./, '');
  return SUSPICIOUS_TLDS[normalizedTld] || { risk: 'LOW', reason: 'Legitimate TLD' };
}

/**
 * Check if TLD is suspicious
 */
export function isSuspiciousTLD(tld) {
  const risk = getTLDRisk(tld);
  return risk.risk === 'HIGH';
}

/**
 * Get all suspicious TLDs
 */
export function getAllSuspiciousTLDs() {
  return Object.entries(SUSPICIOUS_TLDS)
    .filter(([_, info]) => info.risk === 'HIGH')
    .map(([tld, info]) => ({ tld, ...info }));
}
