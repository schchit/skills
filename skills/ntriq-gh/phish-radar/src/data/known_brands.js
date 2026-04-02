/**
 * Known trusted brands for typosquatting detection
 * Contains major financial, tech, and e-commerce companies
 */

export const KNOWN_BRANDS = {
  // Financial Services
  'paypal.com': { name: 'PayPal', category: 'payment', risk_level: 'high' },
  'stripe.com': { name: 'Stripe', category: 'payment', risk_level: 'high' },
  'square.com': { name: 'Square', category: 'payment', risk_level: 'high' },
  'apple.com': { name: 'Apple', category: 'tech', risk_level: 'high' },
  'amazon.com': { name: 'Amazon', category: 'ecommerce', risk_level: 'high' },
  'google.com': { name: 'Google', category: 'tech', risk_level: 'high' },
  'microsoft.com': { name: 'Microsoft', category: 'tech', risk_level: 'high' },
  'facebook.com': { name: 'Facebook', category: 'social', risk_level: 'high' },
  'instagram.com': { name: 'Instagram', category: 'social', risk_level: 'high' },
  'twitter.com': { name: 'Twitter', category: 'social', risk_level: 'high' },
  'linkedin.com': { name: 'LinkedIn', category: 'social', risk_level: 'high' },
  'github.com': { name: 'GitHub', category: 'dev', risk_level: 'high' },
  'gitlab.com': { name: 'GitLab', category: 'dev', risk_level: 'high' },
  'slack.com': { name: 'Slack', category: 'productivity', risk_level: 'high' },
  'zoom.com': { name: 'Zoom', category: 'productivity', risk_level: 'high' },
  'dropbox.com': { name: 'Dropbox', category: 'storage', risk_level: 'high' },
  'box.com': { name: 'Box', category: 'storage', risk_level: 'high' },
  'onelogin.com': { name: 'OneLogin', category: 'auth', risk_level: 'high' },
  'okta.com': { name: 'Okta', category: 'auth', risk_level: 'high' },
  'duo.com': { name: 'Duo', category: 'auth', risk_level: 'high' },
  'lastpass.com': { name: 'LastPass', category: 'password', risk_level: 'high' },
  '1password.com': { name: '1Password', category: 'password', risk_level: 'high' },
  'bitwarden.com': { name: 'Bitwarden', category: 'password', risk_level: 'high' },
  'adobe.com': { name: 'Adobe', category: 'software', risk_level: 'high' },
  'autodesk.com': { name: 'Autodesk', category: 'software', risk_level: 'high' },
  'salesforce.com': { name: 'Salesforce', category: 'crm', risk_level: 'high' },
  'hubspot.com': { name: 'HubSpot', category: 'crm', risk_level: 'high' },
  'zendesk.com': { name: 'Zendesk', category: 'support', risk_level: 'high' },
  'intercom.com': { name: 'Intercom', category: 'support', risk_level: 'high' },
  'twilio.com': { name: 'Twilio', category: 'communication', risk_level: 'high' },
  'sendgrid.com': { name: 'SendGrid', category: 'email', risk_level: 'high' },
  'mailchimp.com': { name: 'Mailchimp', category: 'email', risk_level: 'high' },

  // Banks & Financial
  'boa.com': { name: 'Bank of America', category: 'banking', risk_level: 'high' },
  'wellsfargo.com': { name: 'Wells Fargo', category: 'banking', risk_level: 'high' },
  'chase.com': { name: 'Chase Bank', category: 'banking', risk_level: 'high' },
  'bofa.com': { name: 'Bank of America', category: 'banking', risk_level: 'high' },
  'citigroup.com': { name: 'Citigroup', category: 'banking', risk_level: 'high' },
  'usbank.com': { name: 'US Bank', category: 'banking', risk_level: 'high' },
  'td.com': { name: 'TD Bank', category: 'banking', risk_level: 'high' },
  'barclays.com': { name: 'Barclays', category: 'banking', risk_level: 'high' },
  'hsbc.com': { name: 'HSBC', category: 'banking', risk_level: 'high' },
  'commerzbank.de': { name: 'Commerzbank', category: 'banking', risk_level: 'high' },
  'deutsche-boerse.com': { name: 'Deutsche Börse', category: 'banking', risk_level: 'high' },

  // Cryptocurrency
  'coinbase.com': { name: 'Coinbase', category: 'crypto', risk_level: 'high' },
  'kraken.com': { name: 'Kraken', category: 'crypto', risk_level: 'high' },
  'binance.com': { name: 'Binance', category: 'crypto', risk_level: 'high' },
  'gemini.com': { name: 'Gemini', category: 'crypto', risk_level: 'high' },
  'blockchain.com': { name: 'Blockchain.com', category: 'crypto', risk_level: 'high' },
  'metamask.io': { name: 'MetaMask', category: 'wallet', risk_level: 'high' },

  // Cloud Providers
  'aws.amazon.com': { name: 'AWS', category: 'cloud', risk_level: 'high' },
  'azure.microsoft.com': { name: 'Azure', category: 'cloud', risk_level: 'high' },
  'cloud.google.com': { name: 'Google Cloud', category: 'cloud', risk_level: 'high' },
  'heroku.com': { name: 'Heroku', category: 'cloud', risk_level: 'high' },
  'digitalocean.com': { name: 'DigitalOcean', category: 'cloud', risk_level: 'high' },
  'linode.com': { name: 'Linode', category: 'cloud', risk_level: 'high' },
  'vultr.com': { name: 'Vultr', category: 'cloud', risk_level: 'high' },

  // E-commerce
  'ebay.com': { name: 'eBay', category: 'ecommerce', risk_level: 'high' },
  'shopify.com': { name: 'Shopify', category: 'ecommerce', risk_level: 'high' },
  'wix.com': { name: 'Wix', category: 'website', risk_level: 'medium' },
  'squarespace.com': { name: 'Squarespace', category: 'website', risk_level: 'medium' },
  'etsy.com': { name: 'Etsy', category: 'ecommerce', risk_level: 'high' },
  'aliexpress.com': { name: 'AliExpress', category: 'ecommerce', risk_level: 'high' },

  // Travel
  'booking.com': { name: 'Booking.com', category: 'travel', risk_level: 'high' },
  'expedia.com': { name: 'Expedia', category: 'travel', risk_level: 'high' },
  'airbnb.com': { name: 'Airbnb', category: 'travel', risk_level: 'high' },
  'kayak.com': { name: 'Kayak', category: 'travel', risk_level: 'high' },
  'uber.com': { name: 'Uber', category: 'transport', risk_level: 'high' },
  'lyft.com': { name: 'Lyft', category: 'transport', risk_level: 'high' },

  // Email Providers
  'gmail.com': { name: 'Gmail', category: 'email', risk_level: 'high' },
  'outlook.com': { name: 'Outlook', category: 'email', risk_level: 'high' },
  'yahoo.com': { name: 'Yahoo', category: 'email', risk_level: 'high' },
  'protonmail.com': { name: 'ProtonMail', category: 'email', risk_level: 'high' },
  'tutanota.com': { name: 'Tutanota', category: 'email', risk_level: 'medium' },

  // Utilities
  'discord.com': { name: 'Discord', category: 'communication', risk_level: 'high' },
  'reddit.com': { name: 'Reddit', category: 'social', risk_level: 'medium' },
  'youtube.com': { name: 'YouTube', category: 'video', risk_level: 'high' },
  'twitch.tv': { name: 'Twitch', category: 'streaming', risk_level: 'high' },
  'spotify.com': { name: 'Spotify', category: 'music', risk_level: 'high' },
  'netflix.com': { name: 'Netflix', category: 'streaming', risk_level: 'high' },
  'steam.com': { name: 'Steam', category: 'gaming', risk_level: 'high' },
};

/**
 * Get brand by domain
 */
export function getBrandInfo(domain) {
  const normalizedDomain = domain.toLowerCase().trim();
  return KNOWN_BRANDS[normalizedDomain];
}

/**
 * Get all brands
 */
export function getAllBrands() {
  return Object.entries(KNOWN_BRANDS).map(([domain, info]) => ({
    domain,
    ...info,
  }));
}
