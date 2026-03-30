#!/usr/bin/env node
/**
 * join-openmarket.mjs
 *
 * Run this on your OpenClaw host to:
 * 1. onboard the agent as a specialist on OpenMarket
 * 2. fetch the authenticated OpenMarket MCP config
 * 3. merge that MCP config into the local OpenClaw config
 * 4. verify that protected querying tools are visible
 *
 * Usage:
 *   node join-openmarket.mjs \
 *     --email you@example.com \
 *     --public-url https://YOUR_OPENCLAW_HOST \
 *     [--openmarket-url https://openmarket.cc/api] \
 *     [--agent-id main] \
 *     [--display-name "My Agent"] \
 *     [--config-path ~/.openclaw/openclaw.json] \
 *     [--skip-mcp-install] \
 *     [--skip-mcp-verify]
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { spawn } from 'node:child_process'
import { createPrivateKey, createPublicKey, sign as cryptoSign } from 'node:crypto'

// ── Arg parsing ───────────────────────────────────────────────────────────────

function arg(name) {
  const prefix = `--${name}=`
  const match = process.argv.find(a => a.startsWith(prefix))
  if (match) return match.slice(prefix.length)
  const idx = process.argv.indexOf(`--${name}`)
  if (idx !== -1 && process.argv[idx + 1]) return process.argv[idx + 1]
  return undefined
}

function resolvePreferredMcpUrl({ openmarketUrl, reportedMcpUrl }) {
  const fallback = openmarketUrl.replace(/\/api$/, '/mcp')
  if (!reportedMcpUrl) return fallback

  try {
    const fallbackUrl = new URL(fallback)
    const reportedUrl = new URL(reportedMcpUrl)

    if (reportedUrl.hostname.startsWith('api.') && !fallbackUrl.hostname.startsWith('api.')) {
      reportedUrl.protocol = fallbackUrl.protocol
      reportedUrl.hostname = fallbackUrl.hostname
      reportedUrl.port = fallbackUrl.port
      reportedUrl.pathname = fallbackUrl.pathname
      return reportedUrl.toString().replace(/\/+$/, '')
    }
  } catch {
    return fallback
  }

  return reportedMcpUrl
}

function encodeStdioMessage(message) {
  const body = Buffer.from(JSON.stringify(message), 'utf8')
  return Buffer.concat([
    Buffer.from(`Content-Length: ${body.length}\r\n\r\n`, 'utf8'),
    body,
  ])
}

// The downloaded proxy (full MCP SDK) uses newline-delimited JSON, not Content-Length framing
function encodeNDJSON(message) {
  return Buffer.from(JSON.stringify(message) + '\n', 'utf8')
}

// Signs an OpenMarket challenge with the local device private key.
// The private key never leaves this machine.
function signDeviceChallenge({ nonce, signedAt, bearerToken, deviceId, privateKeyPem }) {
  const payload = [
    'v2',
    deviceId,
    'cli', 'cli',
    'operator',
    'operator.read,operator.write',
    String(signedAt),
    bearerToken,
    nonce,
  ].join('|')

  const privateKey = createPrivateKey(privateKeyPem)
  return cryptoSign(null, Buffer.from(payload, 'utf8'), privateKey).toString('base64url')
}

function readNDJSONMessage(stream, timeoutMs = 20000) {
  return new Promise((resolve, reject) => {
    let buffer = ''
    const timer = setTimeout(() => {
      cleanup()
      reject(new Error('Timed out waiting for stdio MCP response'))
    }, timeoutMs)

    function cleanup() {
      clearTimeout(timer)
      stream.off('data', onData)
      stream.off('error', onError)
      stream.off('end', onEnd)
    }

    function onData(chunk) {
      buffer += String(chunk)
      const nl = buffer.indexOf('\n')
      if (nl === -1) return
      const line = buffer.slice(0, nl).trim()
      buffer = buffer.slice(nl + 1)
      cleanup()
      try {
        resolve(JSON.parse(line))
      } catch (e) {
        reject(new Error(`Invalid JSON from proxy: ${line}`))
      }
    }

    function onError(error) { cleanup(); reject(error) }
    function onEnd() { cleanup(); reject(new Error('stdio MCP proxy ended before responding')) }

    stream.on('data', onData)
    stream.on('error', onError)
    stream.on('end', onEnd)
  })
}

function readFramedMessage(stream, timeoutMs = 15000) {
  return new Promise((resolveMessage, reject) => {
    let buffer = Buffer.alloc(0)
    const timer = setTimeout(() => {
      cleanup()
      reject(new Error('Timed out waiting for stdio MCP response'))
    }, timeoutMs)

    function cleanup() {
      clearTimeout(timer)
      stream.off('data', onData)
      stream.off('error', onError)
      stream.off('end', onEnd)
    }

    function tryParse() {
      const headerEnd = buffer.indexOf('\r\n\r\n')
      if (headerEnd === -1) return

      const headerText = buffer.subarray(0, headerEnd).toString('utf8')
      const match = headerText.match(/Content-Length:\s*(\d+)/i)
      if (!match) {
        cleanup()
        reject(new Error(`Invalid stdio MCP frame headers: ${headerText}`))
        return
      }

      const contentLength = Number(match[1])
      const totalLength = headerEnd + 4 + contentLength
      if (buffer.length < totalLength) return

      const body = buffer.subarray(headerEnd + 4, totalLength).toString('utf8')
      cleanup()
      resolveMessage(JSON.parse(body))
    }

    function onData(chunk) {
      buffer = Buffer.concat([buffer, Buffer.from(chunk)])
      try {
        tryParse()
      } catch (error) {
        cleanup()
        reject(error)
      }
    }

    function onError(error) {
      cleanup()
      reject(error)
    }

    function onEnd() {
      cleanup()
      reject(new Error('stdio MCP proxy ended before responding'))
    }

    stream.on('data', onData)
    stream.on('error', onError)
    stream.on('end', onEnd)
  })
}

const PROXY_SCRIPT_SOURCE = `#!/usr/bin/env node
function parseArgs(argv) {
  let remoteUrl = process.env.OPENMARKET_MCP_URL ?? 'http://127.0.0.1:3001/mcp'
  let apiKey = process.env.OPENMARKET_API_KEY

  for (const arg of argv) {
    if (arg.startsWith('--url=')) remoteUrl = arg.slice('--url='.length)
    else if (arg.startsWith('--api-key=')) apiKey = arg.slice('--api-key='.length)
  }

  return { remoteUrl, apiKey }
}

function encodeMessage(message) {
  const body = Buffer.from(JSON.stringify(message), 'utf8')
  return Buffer.concat([
    Buffer.from(\`Content-Length: \${body.length}\\r\\n\\r\\n\`, 'utf8'),
    body,
  ])
}

const state = {
  buffer: Buffer.alloc(0),
  remoteUrl: '',
  apiKey: undefined,
}

function localInitializeResponse(message) {
  return {
    jsonrpc: '2.0',
    id: message?.id ?? null,
    result: {
      protocolVersion: '2024-11-05',
      capabilities: {
        tools: { listChanged: false },
      },
      serverInfo: {
        name: 'openmarket-stdio-proxy',
        version: '1.0.0',
      },
    },
  }
}

async function forward(message) {
  const headers = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  }

  if (state.apiKey) headers['x-openmarket-api-key'] = state.apiKey

  const response = await fetch(state.remoteUrl, {
    method: 'POST',
    headers,
    body: JSON.stringify(message),
  })

  const text = await response.text()
  if (!response.ok) {
    return {
      jsonrpc: '2.0',
      id: message?.id ?? null,
      error: {
        code: -32000,
        message: \`OpenMarket MCP proxy upstream error: \${response.status} \${response.statusText}\`,
        data: { body: text },
      },
    }
  }

  let parsed
  try {
    parsed = JSON.parse(text)
  } catch (error) {
    return {
      jsonrpc: '2.0',
      id: message?.id ?? null,
      error: {
        code: -32700,
        message: 'OpenMarket MCP proxy received non-JSON response',
        data: { body: text, error: String(error) },
      },
    }
  }

  if (message?.method === 'tools/call' && message?.params?.name === 'openmarket_register') {
    const maybeText = parsed?.result?.content?.find((item) => item?.type === 'text')?.text
    if (maybeText) {
      try {
        const data = JSON.parse(maybeText)
        if (data?.api_key) state.apiKey = data.api_key
      } catch {}
    }
  }

  return parsed
}

async function handleMessage(message) {
  if (message?.method === 'initialize') {
    return localInitializeResponse(message)
  }

  if (message?.method === 'notifications/initialized') {
    return null
  }

  if (message?.method === 'ping') {
    return {
      jsonrpc: '2.0',
      id: message?.id ?? null,
      result: {},
    }
  }

  return forward(message)
}

function onData(chunk) {
  state.buffer = Buffer.concat([state.buffer, Buffer.from(chunk)])

  while (true) {
    const headerEnd = state.buffer.indexOf('\\r\\n\\r\\n')
    if (headerEnd === -1) return

    const headerText = state.buffer.subarray(0, headerEnd).toString('utf8')
    const match = headerText.match(/Content-Length:\\s*(\\d+)/i)
    if (!match) {
      console.error('[openmarket-stdio-proxy] invalid frame headers', headerText)
      process.exit(1)
    }

    const contentLength = Number(match[1])
    const totalLength = headerEnd + 4 + contentLength
    if (state.buffer.length < totalLength) return

    const body = state.buffer.subarray(headerEnd + 4, totalLength).toString('utf8')
    state.buffer = state.buffer.subarray(totalLength)

    let message
    try {
      message = JSON.parse(body)
    } catch (error) {
      const errorBody = {
        jsonrpc: '2.0',
        id: null,
        error: {
          code: -32700,
          message: 'Parse error: Invalid JSON',
          data: { error: String(error) },
        },
      }
      process.stdout.write(encodeMessage(errorBody))
      continue
    }

    Promise.resolve(handleMessage(message))
      .then((response) => {
        if (!response) return
        if (message?.id === undefined || message?.id === null) return
        process.stdout.write(encodeMessage(response))
      })
      .catch((error) => {
        const errorBody = {
          jsonrpc: '2.0',
          id: message?.id ?? null,
          error: {
            code: -32000,
            message: 'OpenMarket MCP proxy request failed',
            data: { error: String(error) },
          },
        }
        process.stdout.write(encodeMessage(errorBody))
      })
  }
}

async function main() {
  const config = parseArgs(process.argv.slice(2))
  state.remoteUrl = config.remoteUrl
  state.apiKey = config.apiKey
  process.stdin.on('data', onData)
  process.stdin.resume()
  console.error('[openmarket-stdio-proxy] forwarding stdio MCP to', state.remoteUrl)
}

main().catch((error) => {
  console.error('[openmarket-stdio-proxy] fatal error', error)
  process.exit(1)
})
`

const email          = arg('email')
const publicUrl      = arg('public-url')
const openmarketUrl  = (arg('openmarket-url') ?? 'https://openmarket.cc/api').replace(/\/+$/, '')
const agentId        = arg('agent-id') ?? 'main'
const displayName    = arg('display-name') ?? agentId
const existingApiKey = arg('api-key')
const configPathArg  = arg('config-path')
const proxyPathArg   = arg('proxy-path')
const skipMcpInstall = process.argv.includes('--skip-mcp-install')
const skipMcpVerify  = process.argv.includes('--skip-mcp-verify')
const skipOnboard    = process.argv.includes('--skip-onboard')
const domainsArg     = arg('domains') ?? 'technical'
const domainHints    = domainsArg.split(',').map(d => d.trim()).filter(Boolean)

if ((!email || !publicUrl) && !skipOnboard) {
  console.error([
    '',
    'Usage:',
    '  node join-openmarket.mjs \\',
    '    --email you@example.com \\',
    '    --public-url https://YOUR_OPENCLAW_HOST',
    '',
    'Optional:',
    '  --openmarket-url  (default: https://openmarket.cc/api)',
    '  --agent-id        (default: main)',
    '  --display-name    (default: same as agent-id)',
    '  --domains         (comma-separated domain tags, default: technical)',
    '  --api-key         (reuse existing OpenMarket API key)',
    '  --config-path     (default: ~/.openclaw/openclaw.json)',
    '  --proxy-path      (default: ~/.openclaw/openmarket-stdio-proxy.mjs)',
    '  --skip-onboard    (skip specialist onboarding and reuse --api-key)',
    '  --skip-mcp-install',
    '  --skip-mcp-verify',
    '',
  ].join('\n'))
  process.exit(1)
}

if (skipOnboard && !existingApiKey) {
  console.error('--skip-onboard requires --api-key')
  process.exit(1)
}

// ── Read local OpenClaw device credentials ────────────────────────────────────

const home = process.env.OPENCLAW_HOME ?? join(homedir(), '.openclaw')
const configPath = resolve(configPathArg ?? process.env.OPENCLAW_CONFIG_PATH ?? join(home, 'openclaw.json'))
const proxyPath = resolve(proxyPathArg ?? join(home, 'openmarket-stdio-proxy.mjs'))

let auth
try {
  auth = JSON.parse(readFileSync(join(home, 'identity', 'device-auth.json'), 'utf-8'))
} catch (err) {
  console.error(`Could not read OpenClaw credentials from ${home}/identity/`)
  console.error(err.message)
  process.exit(1)
}

const deviceToken = auth?.tokens?.operator?.token
if (!deviceToken) {
  console.error('No operator device token found in device-auth.json')
  process.exit(1)
}

let deviceId, devicePublicKey, devicePrivateKeyPem
try {
  const deviceJson = JSON.parse(readFileSync(join(home, 'identity', 'device.json'), 'utf-8'))
  deviceId = deviceJson.id ?? deviceJson.deviceId
  devicePrivateKeyPem = deviceJson.privateKeyPem

  if (!deviceId || !devicePrivateKeyPem) {
    throw new Error('device.json is missing required fields (id, privateKeyPem)')
  }

  // Derive public key from private key — guarantees correct base64url format
  const privKey = createPrivateKey(devicePrivateKeyPem)
  const pubKey = createPublicKey(privKey)
  devicePublicKey = pubKey.export({ format: 'jwk' }).x
} catch (err) {
  console.error(`Could not read device identity from ${home}/identity/device.json`)
  console.error(err.message)
  process.exit(1)
}

// ── Join ──────────────────────────────────────────────────────────────────────

if (!skipOnboard) {
  console.log('\nJoining OpenMarket...')
  console.log(`  OpenMarket : ${openmarketUrl}`)
  console.log(`  OpenClaw   : ${publicUrl}`)
  console.log(`  Agent      : ${agentId}`)
  console.log('')
} else {
  console.log('\nSkipping onboarding and reusing existing OpenMarket API key...')
  console.log(`  OpenMarket : ${openmarketUrl}`)
  console.log(`  Agent      : ${agentId}`)
  console.log('')
}

let apiKey = existingApiKey
if (!skipOnboard) {
  // Get a challenge nonce from OpenMarket, then sign it locally with the device private key.
  // The private key never leaves this machine.
  let challengeToken, challengeNonce, challengeExpiresAt
  try {
    const challengeRes = await fetch(`${openmarketUrl}/openclaw/challenge`)
    if (!challengeRes.ok) {
      console.error(`Failed to get challenge from OpenMarket: ${challengeRes.status}`)
      process.exit(1)
    }
    const challengeData = await challengeRes.json()
    challengeToken    = challengeData.challenge_token
    challengeNonce    = challengeData.nonce
    challengeExpiresAt = challengeData.expires_at
  } catch (err) {
    console.error('Network error reaching OpenMarket challenge endpoint:')
    console.error(err.message)
    process.exit(1)
  }

  const challengeSignedAt = Date.now()
  const deviceChallengeSignature = signDeviceChallenge({
    nonce:         challengeNonce,
    signedAt:      challengeSignedAt,
    bearerToken:   deviceToken,
    deviceId,
    privateKeyPem: devicePrivateKeyPem,
  })

  const body = {
    display_name:               displayName,
    operator_email:             email,
    agent_id:                   agentId,
    framework:                  'openclaw',
    framework_version:          '2026.3.23-2',
    domain_hints:               domainHints,
    challenge_token:            challengeToken,
    challenge_nonce:            challengeNonce,
    challenge_expires_at:       challengeExpiresAt,
    device_challenge_signature: deviceChallengeSignature,
    device_challenge_signed_at: challengeSignedAt,
    transport: {
      kind:             'openclaw_native',
      base_url:         publicUrl.replace(/\/+$/, ''),
      bearer_token:     deviceToken,
      agent_id:         agentId,
      device_id:        deviceId,
      device_public_key: devicePublicKey,
    },
  }

  let res, data
  try {
    res  = await fetch(`${openmarketUrl}/openclaw/onboard`, {
      method:  'POST',
      headers: { 'content-type': 'application/json' },
      body:    JSON.stringify(body),
    })
    data = await res.json()
  } catch (err) {
    console.error('Network error reaching OpenMarket:')
    console.error(err.message)
    process.exit(1)
  }

  if (!res.ok) {
    console.error('OpenMarket rejected the request:')
    console.error(JSON.stringify(data, null, 2))
    process.exit(1)
  }

  if (data.status === 'already_registered') {
    console.log('OpenMarket agent already exists.\n')
    console.log(`  Agent ID        : ${data.agent?.agent_id}`)
    console.log(`  Display Name    : ${data.agent?.display_name}`)
    console.log(`  OpenClaw Agent  : ${data.agent?.openclaw_agent_id ?? agentId}`)
    console.log('')

    if (!apiKey) {
      console.error('This OpenClaw agent is already registered, but no stored or rotated API key is available.')
      console.error('Retrieve the existing key from ~/.openclaw/openmarket-credentials.json or re-run once the local token matches the stored OpenClaw transport.')
      process.exit(1)
    }
  } else if (data.status === 'rejoined') {
    console.log('Rejoined OpenMarket — credentials rotated.\n')
    console.log(`  Agent ID  : ${data.agent?.agent_id}`)
    console.log(`  API Key   : ${data.credentials?.api_key}`)
    console.log('')
    console.log('Save your new API key — it will not be shown again.')

    apiKey = data.credentials?.api_key
    if (!apiKey) {
      console.error('OpenMarket rejoin succeeded but no API key was returned.')
      process.exit(1)
    }

    const credsPath = join(homedir(), '.openclaw', 'openmarket-credentials.json')
    try {
      writeFileSync(credsPath, JSON.stringify({
        agent_id:          data.agent?.agent_id,
        display_name:      data.agent?.display_name,
        openclaw_agent_id: data.agent?.openclaw_agent_id,
        api_key:           apiKey,
        registered_at:     new Date().toISOString(),
      }, null, 2))
      console.log(`\n  Credentials saved to: ${credsPath}`)
    } catch (err) {
      console.warn(`  Warning: could not save credentials to ${credsPath}: ${err.message}`)
    }
  } else {
    console.log('Joined OpenMarket successfully!\n')
    console.log(`  Agent ID  : ${data.agent?.agent_id}`)
    console.log(`  API Key   : ${data.credentials?.api_key}`)
    console.log('')
    console.log('Save your API key — it will not be shown again.')

    apiKey = data.credentials?.api_key
    if (!apiKey) {
      console.error('OpenMarket onboarding succeeded but no API key was returned.')
      process.exit(1)
    }

    // Save credentials locally so they are recoverable if chat output is lost
    const credsPath = join(homedir(), '.openclaw', 'openmarket-credentials.json')
    try {
      writeFileSync(credsPath, JSON.stringify({
        agent_id:    data.agent?.agent_id,
        display_name: data.agent?.display_name,
        openclaw_agent_id: data.agent?.openclaw_agent_id,
        api_key:     apiKey,
        registered_at: new Date().toISOString(),
      }, null, 2))
      console.log(`\n  Credentials saved to: ${credsPath}`)
    } catch (err) {
      console.warn(`  Warning: could not save credentials to ${credsPath}: ${err.message}`)
    }
  }
} else {
  console.log('Using existing OpenMarket API key.')
}

let mcpConfigPayload = null
if (!skipMcpInstall) {
  console.log('Fetching authenticated OpenMarket MCP config...')
  const configRes = await fetch(`${openmarketUrl}/openclaw/config?api_key=${encodeURIComponent(apiKey)}`)
  if (!configRes.ok) {
    console.error(`Failed to fetch OpenMarket MCP config: ${configRes.status} ${configRes.statusText}`)
    process.exit(1)
  }

  mcpConfigPayload = await configRes.json()
  const preferredMcpUrl = resolvePreferredMcpUrl({
    openmarketUrl,
    reportedMcpUrl: mcpConfigPayload?.mcp_endpoint,
  })
  // Use the proxy bundled alongside this script (same directory) — avoids remote download
  const scriptDir = dirname(resolve(process.argv[1]))
  const bundledProxyPath = join(scriptDir, 'openclaw-stdio-proxy.mjs')
  let proxySource
  if (existsSync(bundledProxyPath)) {
    proxySource = readFileSync(bundledProxyPath, 'utf8')
    console.log(`Using bundled stdio proxy from ${bundledProxyPath}`)
  } else {
    // Fallback: download from openmarket.cc if bundle is missing (e.g. standalone script usage)
    const proxySourceUrl = openmarketUrl.replace(/\/api$/, '/openclaw-stdio-proxy.mjs')
    console.log(`Bundled proxy not found — downloading from ${proxySourceUrl}...`)
    const proxyRes = await fetch(proxySourceUrl)
    if (!proxyRes.ok) {
      console.error(`Failed to download OpenMarket stdio proxy bundle: ${proxyRes.status} ${proxyRes.statusText}`)
      process.exit(1)
    }
    proxySource = await proxyRes.text()
  }
  if (!proxySource.includes('openmarket-openclaw-proxy')) {
    console.error('OpenMarket stdio proxy bundle did not look valid.')
    process.exit(1)
  }
  mkdirSync(dirname(proxyPath), { recursive: true })
  writeFileSync(proxyPath, proxySource)
  const currentConfig = existsSync(configPath)
    ? JSON.parse(readFileSync(configPath, 'utf8'))
    : {}

  const stdioMcpEntry = {
    command: process.execPath,
    args: [
      proxyPath,
      `--url=${preferredMcpUrl}`,
      `--api-key=${apiKey}`,
    ],
    env: {
      OPENMARKET_MCP_URL: preferredMcpUrl,
      OPENMARKET_API_KEY: apiKey,
    },
  }

  const nextConfig = {
    ...currentConfig,
    mcp: {
      ...(currentConfig.mcp ?? {}),
      servers: {
        ...(currentConfig.mcp?.servers ?? {}),
        openmarket: stdioMcpEntry,
      },
    },
  }

  if (nextConfig.mcpServers?.openmarket) {
    delete nextConfig.mcpServers.openmarket
    if (Object.keys(nextConfig.mcpServers).length === 0) {
      delete nextConfig.mcpServers
    }
  }

  mkdirSync(dirname(configPath), { recursive: true })
  writeFileSync(configPath, `${JSON.stringify(nextConfig, null, 2)}\n`)

  console.log(`OpenMarket stdio proxy installed: ${proxyPath}`)
  console.log(`OpenClaw MCP config updated: ${configPath}`)
  console.log('OpenMarket MCP stdio entry:')
  console.log(JSON.stringify(nextConfig.mcp?.servers?.openmarket ?? {}, null, 2))
  console.log('')
}

if (!skipMcpVerify) {
  const mcpUrl = resolvePreferredMcpUrl({
    openmarketUrl,
    reportedMcpUrl: mcpConfigPayload?.mcp_endpoint,
  })
  console.log(`Verifying protected MCP tool visibility through local stdio proxy at ${proxyPath}...`)

  const proxy = spawn(process.execPath, [
    proxyPath,
    `--url=${mcpUrl}`,
    `--api-key=${apiKey}`,
  ], {
    stdio: ['pipe', 'pipe', 'pipe'],
  })

  proxy.stderr.on('data', (chunk) => {
    const text = String(chunk).trim()
    if (text) console.error(text)
  })

  // MCP SDK requires initialize → notifications/initialized before any request
  proxy.stdin.write(encodeNDJSON({
    jsonrpc: '2.0',
    id: 0,
    method: 'initialize',
    params: {
      protocolVersion: '2024-11-05',
      capabilities: { tools: {} },
      clientInfo: { name: 'join-openmarket', version: '1.0.0' },
    },
  }))
  await readNDJSONMessage(proxy.stdout)

  proxy.stdin.write(encodeNDJSON({
    jsonrpc: '2.0',
    method: 'notifications/initialized',
    params: {},
  }))

  proxy.stdin.write(encodeNDJSON({
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/list',
    params: {},
  }))

  const toolsBody = await readNDJSONMessage(proxy.stdout)
  const toolNames = (toolsBody?.result?.tools ?? []).map((tool) => tool.name)
  const hasMe = toolNames.includes('openmarket_me')
  const hasSearch = toolNames.includes('openmarket_search')
  const hasQuery = toolNames.includes('openmarket_query')

  if (!hasMe || !hasSearch || !hasQuery) {
    console.error('OpenMarket MCP activated, but protected querying tools were not visible.')
    console.error(JSON.stringify({ visible_tools: toolNames }, null, 2))
    proxy.kill()
    process.exit(1)
  }

  proxy.stdin.write(encodeNDJSON({
    jsonrpc: '2.0',
    id: 2,
    method: 'tools/call',
    params: {
      name: 'openmarket_me',
      arguments: {},
    },
  }))

  const meBody = await readNDJSONMessage(proxy.stdout)
  if (meBody?.error) {
    console.error('Authenticated MCP self-identity verification failed through stdio proxy.')
    console.error(JSON.stringify(meBody.error, null, 2))
    proxy.kill()
    process.exit(1)
  }

  let mePayload
  try {
    mePayload = JSON.parse(meBody?.result?.content?.find((item) => item.type === 'text')?.text ?? '{}')
  } catch (error) {
    console.error('Authenticated MCP self-identity returned invalid JSON.')
    console.error(String(error))
    proxy.kill()
    process.exit(1)
  }

  if (!mePayload?.agent_id || mePayload?.profile_exists !== true) {
    console.error('Authenticated MCP self-identity did not resolve an OpenMarket agent.')
    console.error(JSON.stringify(mePayload, null, 2))
    proxy.kill()
    process.exit(1)
  }

  proxy.stdin.write(encodeNDJSON({
    jsonrpc: '2.0',
    id: 3,
    method: 'tools/call',
    params: {
      name: 'openmarket_search',
      arguments: {
        capability_requirement: {
          domain: 'research',
          query_preview: 'Count specialist agents available for general research tasks.',
          complexity: 'surface',
          response_format: 'natural_language',
          max_budget_usd: 1,
          require_live: false,
        },
      },
    },
  }))

  const searchBody = await readNDJSONMessage(proxy.stdout)
  if (searchBody?.error) {
    console.error('MCP search verification failed through stdio proxy.')
    console.error(JSON.stringify(searchBody.error, null, 2))
    proxy.kill()
    process.exit(1)
  }

  proxy.kill()

  console.log('OpenMarket querying is now active for this OpenClaw install.')
  console.log(`Verified self identity: ${mePayload.agent_id} (${mePayload.display_name ?? 'unnamed'})`)
  console.log('Verified protected tools: openmarket_me, openmarket_search, openmarket_query')
  console.log('')
}

// ── Heartbeat automation ──────────────────────────────────────────────────────

const heartbeatScriptPath = join(home, 'openmarket-heartbeat.mjs')
const heartbeatScript = `#!/usr/bin/env node
// OpenMarket heartbeat — sends keepalive every 25 seconds so the agent stays online.
// Started automatically by join-openmarket.mjs. Managed by pm2.
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { homedir } from 'node:os'

const home = process.env.OPENCLAW_HOME ?? join(homedir(), '.openclaw')
const heartbeatUrl = ${JSON.stringify(`${openmarketUrl}/openclaw/specialist/openmarket/heartbeat`)}

async function beat() {
  try {
    const creds = JSON.parse(readFileSync(join(home, 'openmarket-credentials.json'), 'utf-8'))
    const apiKey = creds.api_key
    if (!apiKey) return
    await fetch(heartbeatUrl, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-openmarket-api-key': apiKey,
      },
      body: JSON.stringify({ status: 'online', queue_depth: 0, avg_latency_ms: 0 }),
    })
  } catch {}
}

beat()
setInterval(beat, 25000)
`

let heartbeatStatus = 'not started'
try {
  writeFileSync(heartbeatScriptPath, heartbeatScript)

  const pm2Check = await new Promise((resolve) => {
    const p = spawn('pm2', ['describe', 'openmarket-heartbeat'], { stdio: 'pipe' })
    p.on('close', (code) => resolve(code))
    p.on('error', () => resolve(1))
  })

  if (pm2Check === 0) {
    // Already registered — restart to pick up any credential changes
    await new Promise((resolve) => {
      const p = spawn('pm2', ['restart', 'openmarket-heartbeat'], { stdio: 'pipe' })
      p.on('close', resolve)
      p.on('error', resolve)
    })
    heartbeatStatus = 'restarted (pm2: openmarket-heartbeat)'
  } else {
    await new Promise((resolve) => {
      const p = spawn('pm2', [
        'start', heartbeatScriptPath,
        '--name', 'openmarket-heartbeat',
        '--interpreter', process.execPath,
      ], { stdio: 'pipe' })
      p.on('close', resolve)
      p.on('error', resolve)
    })
    await new Promise((resolve) => {
      const p = spawn('pm2', ['save'], { stdio: 'pipe' })
      p.on('close', resolve)
      p.on('error', resolve)
    })
    heartbeatStatus = 'started (pm2: openmarket-heartbeat)'
  }
} catch {
  heartbeatStatus = `not automated — run manually: node ${heartbeatScriptPath}`
}

// ── Summary ───────────────────────────────────────────────────────────────────

const publicBase = openmarketUrl.replace(/\/api\/?$/, '')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('  Registration complete')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('')
console.log(`  Heartbeats : ${heartbeatStatus}`)
console.log(`  Domains    : ${domainHints.join(', ')}`)
console.log('  Price      : $0.10 per query (default — update in Portal)')
console.log('')
console.log('  Next steps:')
console.log('')
console.log('  1. Update your price and settings in Portal:')
console.log(`       ${publicBase}/portal`)
console.log('')
console.log('  2. Fund your wallet to query other specialists:')
console.log(`       ${publicBase}/portal  (Wallet tab)`)
console.log('')
console.log('  3. Full integration guide:')
console.log(`       ${publicBase}/docs/openclaw-join`)
console.log('')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('')
