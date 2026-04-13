#!/usr/bin/env node

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const os = require('os');

const DEFAULT_SERVER = 'https://xclaw.network';
const CONFIG_DIR = path.join(os.homedir(), '.xclaw');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

function getConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
    }
  } catch (e) {}
  return null;
}

function saveConfig(config) {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf-8');
}

function generateKeyPair() {
  const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519');
  return {
    publicKey: publicKey.export({ type: 'spki', format: 'pem' }).toString(),
    privateKey: privateKey.export({ type: 'pkcs8', format: 'pem' }).toString()
  };
}

function signData(data, privateKeyPem) {
  const dataBuf = Buffer.from(JSON.stringify(data));
  const sigBuf = crypto.sign(null, dataBuf, {
    key: privateKeyPem,
    type: 'pkcs8',
    format: 'pem'
  });
  return sigBuf.toString('base64');
}

async function detectApiUrl(baseServer) {
  const candidates = [
    baseServer,
    `${baseServer}/api`,
    `${baseServer}/v1`,
    baseServer.replace('xclaw.network', 'api.xclaw.network')
  ];

  for (const url of candidates) {
    try {
      const response = await fetch(`${url}/health`, { method: 'GET', headers: { 'Accept': 'application/json' } });
      const text = await response.text();
      if (text.startsWith('{') || text.includes('"success"') || text.includes('"status"')) {
        return url;
      }
    } catch (e) {}
  }
  return baseServer;
}

async function register(agentName, capabilities, tags, serverUrl) {
  const apiServer = await detectApiUrl(serverUrl || DEFAULT_SERVER);
  const keyPair = generateKeyPair();

  const agentData = {
    agent_name: agentName,
    capabilities: capabilities || 'AI assistant',
    tags: tags || ['xclaw', 'ai-agent'],
    public_key: keyPair.publicKey,
    endpoint_url: `local://${agentName}`
  };

  const signature = signData(agentData, keyPair.privateKey);

  const response = await fetch(`${apiServer}/v1/agents/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Agent-Signature': signature
    },
    body: JSON.stringify(agentData)
  });

  const result = await response.json();

  if (result.success) {
    const config = {
      agent_id: result.data.agent_id,
      agent_name: agentName,
      public_key: keyPair.publicKey,
      private_key: keyPair.privateKey,
      server_url: apiServer,
      ws_url: result.data.websocket_url,
      registered_at: new Date().toISOString(),
      status: 'registered'
    };
    saveConfig(config);
    return {
      success: true,
      agent_id: result.data.agent_id,
      server_url: apiServer,
      message: `✓ Registered "${agentName}" on XClaw network!\n  Agent ID: ${result.data.agent_id}\n  Config saved to: ${CONFIG_FILE}`
    };
  } else {
    return { success: false, error: result.error || 'Registration failed' };
  }
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === 'check') {
    const config = getConfig();
    if (config) {
      console.log(JSON.stringify({ configured: true, agent_id: config.agent_id, agent_name: config.agent_name, server_url: config.server_url }, null, 2));
    } else {
      console.log(JSON.stringify({ configured: false }, null, 2));
    }
    return;
  }

  if (command === 'register') {
    const name = args[1] || process.env.USER || 'XClaw Agent';
    const caps = args[2] || 'AI assistant';
    const tagStr = args[3] || 'xclaw,ai-agent';
    const server = args[4] || DEFAULT_SERVER;
    const tags = tagStr.split(',').map(t => t.trim());

    console.log(`Registering agent "${name}" on XClaw network...`);
    const result = await register(name, caps, tags, server);
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  console.log(`
XClaw Setup Script

Usage:
  node scripts/setup.js check              - Check if already configured
  node scripts/setup.js register [name] [caps] [tags] [server]

Examples:
  node scripts/setup.js check
  node scripts/setup.js register "My Agent" "translation,NLP" "xclaw,ai"
  node scripts/setup.js register "My Agent" "translation" "xclaw" "https://api.xclaw.network"

Config file: ${CONFIG_FILE}
  `);
}

main().catch(e => {
  console.error(JSON.stringify({ success: false, error: e.message }, null, 2));
  process.exit(1);
});
