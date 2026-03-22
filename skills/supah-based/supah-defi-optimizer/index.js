#!/usr/bin/env node
const https = require('https');
const API = process.env.SUPAH_API_BASE || 'https://api.supah.ai';

function api(path, params = {}) {
  return new Promise((resolve, reject) => {
    const qs = new URLSearchParams(params).toString();
    https.get(`${API}${path}${qs?'?'+qs:''}`, res => {
      let d=''; res.on('data', c=>d+=c);
      res.on('end', ()=>{try{resolve(JSON.parse(d))}catch(e){resolve({error:'Invalid'})}});
    }).on('error', reject);
  });
}

async function main() {
  const args = process.argv.slice(2);
  if (!args[0]) {
    console.log('\nSUPAH DeFi Optimizer v1.0.0\n');
    console.log('Commands:');
    console.log('  positions <wallet>  - View positions (FREE)');
    console.log('  optimize <wallet>   - Auto-optimize ($5/mo)');
    console.log('  yields              - Compare APYs (FREE top 5)');
    console.log('  rebalance <wallet>  - Suggestions ($1)');
    console.log('  il <position>       - IL calculator ($0.50)\n');
    return;
  }
  
  const cmd = args[0];
  if (cmd === 'positions' || cmd === 'yields') {
    console.log(`\n📊 ${cmd}\n`);
    console.log('⚠️  Upgrade for full optimization\n');
  } else {
    console.log(`\n💳 ${cmd} requires payment\n`);
  }
}

main().catch(console.error);
