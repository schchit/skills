#!/usr/bin/env node

const { readFile } = require('node:fs/promises')
const path = require('node:path')
const { createPublicClient, createWalletClient, defineChain, formatEther, http, isAddress, parseEther } = require('viem')
const { mnemonicToAccount, privateKeyToAccount } = require('viem/accounts')
const { decryptSecret } = require('./secret-crypto')

const walletDir = path.resolve(__dirname, '..', 'wallet')
const configPath = path.join(walletDir, 'config.json')
const signerPath = path.join(walletDir, 'signer.json')

main().catch((error) => fail(error.message))

async function main() {
  const args = parseArgs(process.argv.slice(2))
  const to = args.to
  const amount = args.amount
  const confirm = toBool(args.confirm)

  if (!to || !isAddress(to)) {
    fail('Provide a valid --to recipient address.')
  }
  if (!amount || Number(amount) <= 0) {
    fail('Provide a positive --amount value in native units.')
  }
  if (!confirm) {
    fail('Broadcast requires explicit --confirm=true.')
  }

  const currentNetwork = await readCurrentNetwork()
  const account = await readSignerAccount()
  const chain = buildChain(currentNetwork)

  const publicClient = createPublicClient({
    chain,
    transport: http(currentNetwork.rpc_url),
  })
  const walletClient = createWalletClient({
    account,
    chain,
    transport: http(currentNetwork.rpc_url),
  })

  const value = parseEther(String(amount))
  const balance = await publicClient.getBalance({ address: account.address })
  if (balance < value) {
    fail(
      `Insufficient funds. Balance ${formatEther(balance)} is lower than transfer amount ${amount}.`
    )
  }

  const txHash = await walletClient.sendTransaction({
    account,
    to,
    value,
  })

  console.log(
    JSON.stringify(
      {
        action: 'send',
        chain: currentNetwork.chain_id,
        address: account.address,
        to,
        amount,
        txHash,
        status: 'success',
        next_step: 'Track transaction confirmation using the tx hash.',
      },
      null,
      2
    )
  )
}

function parseArgs(rawArgs) {
  const parsed = {}
  for (const arg of rawArgs) {
    if (!arg.startsWith('--')) continue
    const [k, ...rest] = arg.slice(2).split('=')
    parsed[k] = rest.length ? rest.join('=') : 'true'
  }
  return parsed
}

function toBool(value) {
  return String(value).toLowerCase() === 'true'
}

async function readCurrentNetwork() {
  const raw = await readFile(configPath, 'utf8').catch((error) => {
    if (error && error.code === 'ENOENT') {
      fail('wallet/config.json is missing. Configure default network first.')
    }
    fail(`Unable to read wallet/config.json: ${error.message}`)
  })

  let list
  try {
    list = JSON.parse(raw)
  } catch (error) {
    fail(`wallet/config.json is invalid JSON: ${error.message}`)
  }

  if (!Array.isArray(list)) {
    fail('wallet/config.json must be an array of network objects.')
  }

  const currentEntries = list.filter((entry) => entry && entry.current === true)
  if (currentEntries.length !== 1) {
    fail('wallet/config.json must contain exactly one network with current=true.')
  }

  const current = currentEntries[0]
  if (!current.rpc_url || !current.chain_id) {
    fail('Current network must include rpc_url and chain_id.')
  }
  return current
}

async function readSignerAccount() {
  const raw = await readFile(signerPath, 'utf8').catch((error) => {
    if (error && error.code === 'ENOENT') {
      fail('wallet/signer.json is missing. Generate or import wallet first.')
    }
    fail(`Unable to read wallet/signer.json: ${error.message}`)
  })

  let signer
  try {
    signer = JSON.parse(raw)
  } catch (error) {
    fail(`wallet/signer.json is invalid JSON: ${error.message}`)
  }

  if (signer.method === 'seed_phrase') {
    if (!signer.encryptedSeedPhrase) {
      fail('wallet/signer.json seed_phrase entry is missing encryptedSeedPhrase.')
    }
    const seedPhrase = decryptSecret(String(signer.encryptedSeedPhrase))
    return mnemonicToAccount(seedPhrase)
  }

  if (signer.method === 'private_key') {
    if (!signer.encryptedPrivateKey) {
      fail('wallet/signer.json private_key entry is missing encryptedPrivateKey.')
    }
    const privateKey = decryptSecret(String(signer.encryptedPrivateKey))
    const normalized = privateKey.startsWith('0x') ? privateKey : `0x${privateKey}`
    return privateKeyToAccount(normalized)
  }

  fail('wallet/signer.json method must be "seed_phrase" or "private_key".')
}

function buildChain(currentNetwork) {
  const id = Number(currentNetwork.chain_id)
  if (!Number.isFinite(id) || id <= 0) {
    fail(`Invalid chain_id: ${currentNetwork.chain_id}`)
  }

  return defineChain({
    id,
    name: `chain-${currentNetwork.chain_id}`,
    network: `chain-${currentNetwork.chain_id}`,
    nativeCurrency: {
      name: 'Native Token',
      symbol: 'NATIVE',
      decimals: 18,
    },
    rpcUrls: {
      default: {
        http: [currentNetwork.rpc_url],
      },
      public: {
        http: [currentNetwork.rpc_url],
      },
    },
  })
}

function fail(message) {
  console.error(JSON.stringify({ status: 'failed', error: message }, null, 2))
  process.exit(1)
}
