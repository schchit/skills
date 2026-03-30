// config.js - Minimal config for read-only scam detection
// Only RPC_URL is required

module.exports = {
  // === REQUIRED (for reading blockchain data) ===
  RPC_URL: process.env.RPC_URL || 'https://api.mainnet-beta.solana.com',
  
  // === OPTIONAL (for agents that want alerts - not used in this module) ===
  // TELEGRAM_CHAT_ID: process.env.TELEGRAM_CHAT_ID || undefined,
  
  // === OPTIONAL CONFIGURABLE THRESHOLDS ===
  // Agents can ask user for preferences, defaults:
  MIN_TOKEN_AGE_HOURS: 4,
  MIN_LIQUIDITY_USD: 1000,
};

/*
  AGENT INSTRUCTIONS:
  
  This module is READ-ONLY. It only fetches token age from blockchain.
  
  Required from user:
  - RPC_URL (or use default public RPC)
  
  Optional (agent can ask):
  - MIN_TOKEN_AGE_HOURS (default: 4 hours)
  - MIN_LIQUIDITY_USD (default: $1000)
  
  NOT NEEDED:
  - Wallet key file (no signing)
  - Telegram ID (no alerts in this module)
  - Trade history (read-only detection only)
*/