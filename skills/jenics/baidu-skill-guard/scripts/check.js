'use strict';

const crypto = require('crypto');
const https = require('https');
const http = require('http');
const { URL } = require('url');
const fs = require('fs');
const path = require('path');
const os = require('os');
const zlib = require('zlib');

// ============================================================
// Configuration
// ============================================================

const API_BASE_URL = 'https://skill-sec.baidu.com';
const API_PATH = '/v1/skill/security/results';
const API_UPLOAD_PATH = '/v1/skill/security/upload';
const API_SCAN_PATH = '/v1/skill/security/scan'; // + /{task_id}
const REQUEST_TIMEOUT = 10000; // 10s
const POLL_TIMEOUT = 600000; // 10 min


// ============================================================
// HTTP Client (ported from source/api/client.ts)
// ============================================================

function makeRequest(options, timeout) {
  return new Promise((resolve, reject) => {
    const protocol = options.protocol === 'https:' ? https : http;

    const req = protocol.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        resolve(data);
      });
    });

    req.on('error', (error) => {
      reject(new Error(`请求失败: ${error.message}`));
    });

    req.setTimeout(timeout, () => {
      req.destroy();
      reject(new Error('请求超时'));
    });

    req.end();
  });
}

function makePostRequest(options, bodyBuffer, timeout) {
  return new Promise((resolve, reject) => {
    const protocol = options.protocol === 'https:' ? https : http;
    const req = protocol.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        resolve(data);
      });
    });
    req.on('error', (error) => {
      reject(new Error(`请求失败: ${error.message}`));
    });
    req.setTimeout(timeout, () => {
      req.destroy();
      reject(new Error('请求超时'));
    });
    req.write(bodyBuffer);
    req.end();
  });
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================================
// API: checkSkillSecurity (ported from source/api/client.ts)
// ============================================================

async function checkSkillSecurity(slug, version) {
  // Build query params
  const queryParams = { slug };
  if (version) {
    queryParams.version = version;
  }

  // Build query string
  const queryString = Object.entries(queryParams)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join('&');

  // Parse URL
  const url = new URL(`${API_PATH}?${queryString}`, API_BASE_URL);

  // Build request headers
  const headers = {
    'Host': url.host,
    'Content-Type': 'application/json',
    'Content-Length': '0'
  };

  // Build request options
  const requestOptions = {
    protocol: url.protocol,
    hostname: url.hostname,
    port: url.port || (url.protocol === 'https:' ? 443 : 80),
    path: `${url.pathname}?${queryString}`,
    method: 'GET',
    headers
  };

  const responseText = await makeRequest(requestOptions, REQUEST_TIMEOUT);

  // Parse response
  const response = JSON.parse(responseText);

  if (response.code !== 'success') {
    return null;
  }

  // Return first data item (if exists and has content)
  if (response.data && response.data.length > 0) {
    const item = response.data[0];

    // Check for empty record (uncollected skill)
    if (!item.bd_confidence) {
      return null;
    }

    return {
      bd_confidence: item.bd_confidence,
      bd_describe: item.bd_describe,
      slug: item.slug,
      version: item.version,
      source: item.source,
      sha256: item.sha256,
      scanned_at: item.scanned_at,
      detail: item.detail,
      author: item.detail && item.detail.github ? item.detail.github.name : undefined
    };
  }

  return null;
}

// New function to get full API response
async function checkSkillSecurityFullResponse(slug, version) {
  // Build query params
  const queryParams = { slug };
  if (version) {
    queryParams.version = version;
  }

  // Build query string
  const queryString = Object.entries(queryParams)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join('&');

  // Parse URL
  const url = new URL(`${API_PATH}?${queryString}`, API_BASE_URL);

  // Build request headers
  const headers = {
    'Host': url.host,
    'Content-Type': 'application/json',
    'Content-Length': '0'
  };

  // Build request options
  const requestOptions = {
    protocol: url.protocol,
    hostname: url.hostname,
    port: url.port || (url.protocol === 'https:' ? 443 : 80),
    path: `${url.pathname}?${queryString}`,
    method: 'GET',
    headers
  };

  const responseText = await makeRequest(requestOptions, REQUEST_TIMEOUT);

  // Parse and return full response
  return JSON.parse(responseText);
}

// ============================================================
// Upload & Poll (for Scenario B: scan)
// ============================================================

function buildMultipartBody(filePath, slug, version) {
  const boundary = '----NodeFormBoundary' + crypto.randomBytes(16).toString('hex');
  const CRLF = '\r\n';
  const parts = [];

  // file field
  const fileName = path.basename(filePath);
  const fileContent = fs.readFileSync(filePath);
  parts.push(
    `--${boundary}${CRLF}` +
    `Content-Disposition: form-data; name="file"; filename="${fileName}"${CRLF}` +
    `Content-Type: application/zip${CRLF}${CRLF}`
  );
  parts.push(fileContent);
  parts.push(CRLF);

  // text fields
  const textFields = { source: 'openclaw' };
  if (slug) {
    textFields.slug = slug;
  }
  if (version) {
    textFields.version = version;
  }

  for (const [key, value] of Object.entries(textFields)) {
    parts.push(
      `--${boundary}${CRLF}` +
      `Content-Disposition: form-data; name="${key}"${CRLF}${CRLF}` +
      `${value}${CRLF}`
    );
  }

  // closing boundary
  parts.push(`--${boundary}--${CRLF}`);

  const buffers = parts.map(p => ((typeof p === 'string') ? Buffer.from(p, 'utf8') : p));
  const bodyBuffer = Buffer.concat(buffers);
  const contentType = `multipart/form-data; boundary=${boundary}`;

  return { bodyBuffer, contentType };
}

// ============================================================
// Pure Node.js ZIP Implementation (replaces shell zip command)
// ============================================================

const CRC32_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
    }
    table[n] = c;
  }
  return table;
})();

function crc32(buf) {
  let crc = 0xFFFFFFFF;
  for (let i = 0; i < buf.length; i++) {
    crc = CRC32_TABLE[(crc ^ buf[i]) & 0xFF] ^ (crc >>> 8);
  }
  return (crc ^ 0xFFFFFFFF) >>> 0;
}

function collectFiles(dirPath, prefix) {
  const results = [];
  const entries = fs.readdirSync(dirPath);
  for (const name of entries) {
    const fullPath = path.join(dirPath, name);
    const relPath = prefix ? prefix + '/' + name : name;
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      results.push(...collectFiles(fullPath, relPath));
    } else if (stat.isFile()) {
      results.push({ relPath, absPath: fullPath });
    }
  }
  return results;
}

function dosDateTime(date) {
  const d = date || new Date();
  const time = ((d.getHours() & 0x1F) << 11) | ((d.getMinutes() & 0x3F) << 5) | ((d.getSeconds() >> 1) & 0x1F);
  const dateVal = (((d.getFullYear() - 1980) & 0x7F) << 9) | (((d.getMonth() + 1) & 0xF) << 5) | (d.getDate() & 0x1F);
  return { time, date: dateVal };
}

function createZipBuffer(dirPath) {
  const files = collectFiles(dirPath, '');
  const localParts = [];
  const centralEntries = [];
  let offset = 0;
  const now = dosDateTime(new Date());

  for (const file of files) {
    const fileData = fs.readFileSync(file.absPath);
    const crc = crc32(fileData);
    const compressed = zlib.deflateRawSync(fileData);
    const useDeflate = compressed.length < fileData.length;
    const storedData = useDeflate ? compressed : fileData;
    const method = useDeflate ? 8 : 0;
    const nameBuffer = Buffer.from(file.relPath, 'utf8');

    // Local File Header (30 bytes + name + data)
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);
    local.writeUInt16LE(0, 6);
    local.writeUInt16LE(method, 8);
    local.writeUInt16LE(now.time, 10);
    local.writeUInt16LE(now.date, 12);
    local.writeUInt32LE(crc, 14);
    local.writeUInt32LE(storedData.length, 18);
    local.writeUInt32LE(fileData.length, 22);
    local.writeUInt16LE(nameBuffer.length, 26);
    local.writeUInt16LE(0, 28);

    const localEntry = Buffer.concat([local, nameBuffer, storedData]);
    localParts.push(localEntry);

    // Central Directory Entry (46 bytes + name)
    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(20, 4);
    central.writeUInt16LE(20, 6);
    central.writeUInt16LE(0, 8);
    central.writeUInt16LE(method, 10);
    central.writeUInt16LE(now.time, 12);
    central.writeUInt16LE(now.date, 14);
    central.writeUInt32LE(crc, 16);
    central.writeUInt32LE(storedData.length, 20);
    central.writeUInt32LE(fileData.length, 24);
    central.writeUInt16LE(nameBuffer.length, 28);
    central.writeUInt16LE(0, 30);
    central.writeUInt16LE(0, 32);
    central.writeUInt16LE(0, 34);
    central.writeUInt16LE(0, 36);
    central.writeUInt32LE(0, 38);
    central.writeUInt32LE(offset, 42);

    centralEntries.push(Buffer.concat([central, nameBuffer]));
    offset += localEntry.length;
  }

  const centralDirBuffer = Buffer.concat(centralEntries);
  const centralDirOffset = offset;
  const centralDirSize = centralDirBuffer.length;

  // End of Central Directory Record (22 bytes)
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(0, 4);
  eocd.writeUInt16LE(0, 6);
  eocd.writeUInt16LE(files.length, 8);
  eocd.writeUInt16LE(files.length, 10);
  eocd.writeUInt32LE(centralDirSize, 12);
  eocd.writeUInt32LE(centralDirOffset, 16);
  eocd.writeUInt16LE(0, 20);

  return Buffer.concat([...localParts, centralDirBuffer, eocd]);
}

function zipDirectory(dirPath) {
  const tmpZip = path.join(os.tmpdir(), `skill-scan-${Date.now()}.zip`);
  const zipBuffer = createZipBuffer(dirPath);
  fs.writeFileSync(tmpZip, zipBuffer);
  return tmpZip;
}

async function uploadSkillForScan(filePath, slug, version) {
  let actualFilePath = filePath;
  let tmpZip = null;

  if (fs.statSync(filePath).isDirectory()) {
    tmpZip = zipDirectory(filePath);
    actualFilePath = tmpZip;
  }

  try {
    const { bodyBuffer, contentType } = buildMultipartBody(actualFilePath, slug, version);
    const url = new URL(API_UPLOAD_PATH, API_BASE_URL);

    const headers = {
      'Host': url.host,
      'Content-Type': contentType,
      'Content-Length': String(bodyBuffer.length)
    };

    const requestOptions = {
      protocol: url.protocol,
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname,
      method: 'POST',
      headers
    };

    const responseText = await makePostRequest(requestOptions, bodyBuffer, REQUEST_TIMEOUT);
    const response = JSON.parse(responseText);

    if (response.code !== 'success' || !response.data || !response.data.task_id) {
      throw new Error(response.message || response.msg || '上传失败，未返回 task_id');
    }

    return response.data.task_id;
  } finally {
    if (tmpZip && fs.existsSync(tmpZip)) {
      fs.unlinkSync(tmpZip);
    }
  }
}

async function pollScanResult(taskId) {
  const startTime = Date.now();
  let attempt = 0;

  while (Date.now() - startTime < POLL_TIMEOUT) {
    attempt++;
    await sleep(attempt === 1 ? 1000 : 5000);

    const apiPath = `${API_SCAN_PATH}/${encodeURIComponent(taskId)}`;
    const url = new URL(apiPath, API_BASE_URL);

    const headers = {
      'Host': url.host,
      'Content-Type': 'application/json',
      'Content-Length': '0'
    };

    const requestOptions = {
      protocol: url.protocol,
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname,
      method: 'GET',
      headers
    };

    try {
      const responseText = await makeRequest(requestOptions, REQUEST_TIMEOUT);
      const response = JSON.parse(responseText);

      if (response.code !== 'success') {
        continue;
      }

      const status = response.data && response.data.status;
      if (status === 'done') {
        return response.data;
      } else if (status === 'failed' || status === 'error') {
        throw new Error(`扫描任务失败，状态：${status}`);
      }
      // pending/processing: continue polling
    } catch (err) {
      if (err.message.includes('扫描任务失败')) {
        throw err;
      }
      // network errors: continue polling
    }
  }

  throw new Error('扫描任务超时（超过 10 分钟）');
}

// ============================================================
// Format & Main Logic (ported from source/index.ts)
// ============================================================

function formatMessage(riskLevel, result) {
  if (!result) {
    return '⚠️ 该 skill 尚未被安全系统收录，无法获取安全评估信息，建议谨慎安装。';
  }

  const skillName = result.slug;

  switch (riskLevel) {
    case 'safe':
      return `✅ ${skillName} 已通过安全检查，可以放心安装。\n` +
             `评估详情：${result.bd_describe || '该 skill 经过安全评估，未发现风险。'}`;

    case 'caution':
      return `⚠️ 警告：${skillName} 存在潜在风险！\n\n` +
             '🔍 风险等级：灰名单（需谨慎）\n' +
             `📋 风险详情：${result.bd_describe || '部分信息无法完全验证'}\n\n` +
             '建议人工审查后再决定是否安装。\n' +
             '是否继续安装？';

    case 'dangerous':
      return `🚫 危险：${skillName} 存在严重安全风险！\n\n` +
             '🔍 风险等级：黑名单（不可信）\n' +
             `📋 风险详情：${result.bd_describe || '检测到安全威胁'}\n\n` +
             '强烈建议不要安装此 skill！\n' +
             '是否仍要继续安装？';

    default:
      return `⚠️ ${skillName} 的安全状态未知，建议谨慎安装。`;
  }
}

async function checkSkillSecurityMain(slug, version) {
  // Parameter validation
  if (!slug || slug.trim() === '') {
    return {
      safe: false,
      riskLevel: 'unknown',
      message: '❌ 错误：skill 标识符（slug）不能为空',
      details: null,
      requireConfirmation: true
    };
  }

  try {
    // Call security check API
    const result = await checkSkillSecurity(slug.trim(), version ? version.trim() : undefined);

    // Handle uncollected case
    if (!result) {
      return {
        safe: false,
        riskLevel: 'unknown',
        message: formatMessage('unknown', null),
        details: null,
        requireConfirmation: true
      };
    }

    // Map bd_confidence to internal risk level
    const bdConfidence = (result.bd_confidence || '').toLowerCase();
    let riskLevel;

    switch (bdConfidence) {
      case 'trusted':
      case 'safe':
        riskLevel = 'safe';
        break;
      case 'caution':
        riskLevel = 'caution';
        break;
      case 'dangerous':
        riskLevel = 'dangerous';
        break;
      default:
        riskLevel = 'unknown';
    }

    return {
      safe: riskLevel === 'safe',
      riskLevel,
      message: formatMessage(riskLevel, result),
      details: result,
      requireConfirmation: riskLevel !== 'safe'
    };

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误';

    return {
      safe: false,
      riskLevel: 'error',
      message: `🚫 安全检查服务调用失败：${errorMessage}\n` +
               `无法获取 ${slug} 的安全评估信息。\n` +
               '建议稍后重试，不建议在未通过安全检查的情况下安装。',
      details: null,
      requireConfirmation: true
    };
  }
}

// ============================================================
// Scan: Full Response (for Scenario B: scan)
// ============================================================

async function scanSkillSecurityFullResponse(filePath, slug, version) {
  if (!filePath || !fs.existsSync(filePath)) {
    return {
      code: 'error',
      msg: `❌ 错误：文件路径不存在 -- ${filePath || '(空)'}`,
      ts: Date.now(),
      data: null
    };
  }

  try {
    // 1. Upload
    const taskId = await uploadSkillForScan(filePath, slug, version);

    // 2. Poll
    const scanData = await pollScanResult(taskId);

    // 3. Return full response
    return {
      code: 'success',
      msg: 'success',
      ts: Date.now(),
      data: scanData
    };

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    return {
      code: 'error',
      msg: `🚫 扫描服务调用失败：${errorMessage}`,
      ts: Date.now(),
      data: null
    };
  }
}

// ============================================================
// ScanFull: Batch scan all subdirectories (for Scenario C: scanfull)
// ============================================================

async function scanFullDirectory(dirPath) {
  if (!dirPath || !fs.existsSync(dirPath)) {
    return {
      code: 'error',
      msg: `❌ 错误：目录路径不存在 -- ${dirPath || '(空)'}`,
      ts: Date.now(),
      total: 0,
      safe_count: 0,
      danger_count: 0,
      caution_count: 0,
      error_count: 0,
      results: []
    };
  }

  const stat = fs.statSync(dirPath);
  if (!stat.isDirectory()) {
    return {
      code: 'error',
      msg: `❌ 错误：路径不是目录 -- ${dirPath}`,
      ts: Date.now(),
      total: 0,
      safe_count: 0,
      danger_count: 0,
      caution_count: 0,
      error_count: 0,
      results: []
    };
  }

  // List immediate subdirectories, skip hidden dirs
  const entries = fs.readdirSync(dirPath).filter(name => {
    if (name.startsWith('.')) {
      return false;
    }
    const fullPath = path.join(dirPath, name);
    return fs.statSync(fullPath).isDirectory();
  });

  if (entries.length === 0) {
    return {
      code: 'success',
      msg: 'scanfull completed, no skill subdirectories found',
      ts: Date.now(),
      total: 0,
      safe_count: 0,
      danger_count: 0,
      caution_count: 0,
      error_count: 0,
      results: []
    };
  }

  const results = [];
  let safeCount = 0;
  let dangerCount = 0;
  let cautionCount = 0;
  let errorCount = 0;

  for (const name of entries) {
    const skillDir = path.join(dirPath, name);
    const response = await scanSkillSecurityFullResponse(skillDir, name, undefined);

    // Classify this skill's result
    if (response.code === 'success' && response.data && response.data.results) {
      const allSafe = response.data.results.every(item => {
        const c = (item.bd_confidence || '').toLowerCase();
        return c === 'safe' || c === 'trusted';
      });
      if (allSafe) {
        safeCount++;
      } else {
        const hasDangerous = response.data.results.some(item => {
          return (item.bd_confidence || '').toLowerCase() === 'dangerous';
        });
        const hasCaution = response.data.results.some(item => {
          return (item.bd_confidence || '').toLowerCase() === 'caution';
        });
        if (hasDangerous) {
          dangerCount++;
        } else if (hasCaution) {
          cautionCount++;
        } else {
          errorCount++;
        }
      }
    } else {
      errorCount++;
    }

    results.push({
      skill: name,
      ...response
    });
  }

  return {
    code: 'success',
    msg: 'scanfull completed',
    ts: Date.now(),
    total: entries.length,
    safe_count: safeCount,
    danger_count: dangerCount,
    caution_count: cautionCount,
    error_count: errorCount,
    results
  };
}

// ============================================================
// Scan: Format & Main Logic (for Scenario B: scan)
// ============================================================

function formatScanMessage(riskLevel, result) {
  const skillName = result.slug || 'unknown';

  switch (riskLevel) {
    case 'safe':
      return `✅ ${skillName} 扫描通过，未发现安全风险。\n` +
             `评估详情：${result.bd_describe || '扫描完成，未发现威胁。'}`;

    case 'caution':
      return `⚠️ 警告：${skillName} 扫描发现潜在风险！\n\n` +
             '🔍 风险等级：灰名单（需谨慎）\n' +
             `📋 风险详情：${result.bd_describe || '部分信息无法完全验证'}\n\n` +
             '建议人工审查后再决定是否使用。';

    case 'dangerous':
      return `🚫 危险：${skillName} 扫描发现严重安全风险！\n\n` +
             '🔍 风险等级：黑名单（不可信）\n' +
             `📋 风险详情：${result.bd_describe || '检测到安全威胁'}\n\n` +
             '强烈建议不要使用此 skill！';

    default:
      return `⚠️ ${skillName} 的扫描结果未知，建议谨慎处理。`;
  }
}

async function scanSkillSecurityMain(filePath, slug, version) {
  if (!filePath || !fs.existsSync(filePath)) {
    return {
      safe: false,
      riskLevel: 'error',
      message: `❌ 错误：文件路径不存在 -- ${filePath || '(空)'}`,
      details: null,
      requireConfirmation: true
    };
  }

  try {
    // 1. Upload
    const taskId = await uploadSkillForScan(filePath, slug, version);

    // 2. Poll
    const scanData = await pollScanResult(taskId);

    // 3. Parse results
    const results = scanData.results || [];
    if (results.length === 0) {
      return {
        safe: false,
        riskLevel: 'unknown',
        message: '⚠️ 扫描完成但未返回结果，建议谨慎处理。',
        details: scanData,
        requireConfirmation: true
      };
    }

    // Map each result item
    const processedResults = results.map(item => {
      const bdConfidence = (item.bd_confidence || '').toLowerCase();
      let riskLevel;
      switch (bdConfidence) {
        case 'trusted':
        case 'safe':
          riskLevel = 'safe';
          break;
        case 'caution':
          riskLevel = 'caution';
          break;
        case 'dangerous':
          riskLevel = 'dangerous';
          break;
        default:
          riskLevel = 'unknown';
      }
      return {
        safe: riskLevel === 'safe',
        riskLevel,
        message: formatScanMessage(riskLevel, item),
        details: item,
        requireConfirmation: riskLevel !== 'safe'
      };
    });

    // Single result
    if (processedResults.length === 1) {
      return processedResults[0];
    }

    // Multiple results: overall safe = all safe, worst level wins
    const allSafe = processedResults.every(r => r.safe);
    const order = { error: 5, dangerous: 4, caution: 3, unknown: 2, safe: 1 };
    const worstLevel = processedResults.reduce((worst, r) => {
      return (order[r.riskLevel] || 0) > (order[worst] || 0) ? r.riskLevel : worst;
    }, 'safe');

    return {
      safe: allSafe,
      riskLevel: worstLevel,
      message: `扫描完成，共 ${processedResults.length} 个 skill`,
      details: processedResults,
      requireConfirmation: !allSafe
    };

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    return {
      safe: false,
      riskLevel: 'error',
      message: `🚫 扫描服务调用失败：${errorMessage}\n建议稍后重试。`,
      details: null,
      requireConfirmation: true
    };
  }
}

// ============================================================
// CLI Entry Point
// ============================================================

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--slug' && i + 1 < argv.length) {
      args.slug = argv[++i];
    } else if (argv[i] === '--version' && i + 1 < argv.length) {
      args.version = argv[++i];
    } else if (argv[i] === '--action' && i + 1 < argv.length) {
      args.action = argv[++i];
    } else if (argv[i] === '--file' && i + 1 < argv.length) {
      args.file = argv[++i];
    }
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv);

  if (args.action === 'scan') {
    // Upload + poll flow
    if (!args.file) {
      const output = {
        code: 'error',
        msg: '❌ 错误：--action scan 需要提供 --file 参数\n' +
          '用法：node check.js --action scan --file "/path/to/skill.zip" [--slug "xxx"] [--version "yyy"]',
        ts: Date.now(),
        data: null
      };
      console.log(JSON.stringify(output, null, 2));
      process.exit(1);
    }

    const response = await scanSkillSecurityFullResponse(args.file, args.slug, args.version);
    console.log(JSON.stringify(response, null, 2));

    // Determine exit code based on scan results
    if (response.code === 'success' && response.data && response.data.results) {
      const results = response.data.results;
      const allSafe = results.every(item => {
        const bdConfidence = (item.bd_confidence || '').toLowerCase();
        return bdConfidence === 'safe' || bdConfidence === 'trusted';
      });
      process.exit(allSafe ? 0 : 1);
    } else {
      process.exit(1);
    }
  } else if (args.action === 'scanfull') {
    // Batch scan all subdirectories under a skills parent directory
    if (!args.file) {
      const output = {
        code: 'error',
        msg: '❌ 错误：--action scanfull 需要提供 --file 参数（skills 父目录）\n' +
          '用法：node check.js --action scanfull --file "/path/to/skills"',
        ts: Date.now(),
        total: 0,
        safe_count: 0,
        danger_count: 0,
        caution_count: 0,
        error_count: 0,
        results: []
      };
      console.log(JSON.stringify(output, null, 2));
      process.exit(1);
    }

    const response = await scanFullDirectory(args.file);
    console.log(JSON.stringify(response, null, 2));

    // Exit code: 0 if all safe and total > 0, 1 otherwise
    const allSafe = response.code === 'success'
      && response.total > 0
      && response.safe_count === response.total;
    process.exit(allSafe ? 0 : 1);

  } else {
    // Original query flow
    if (!args.slug) {
      const output = {
        code: 'error',
        msg: '❌ 错误：缺少必填参数 --slug\n用法：node check.js --slug \'skill-slug\' [--version \'1.0.0\']',
        ts: Date.now(),
        data: []
      };
      console.log(JSON.stringify(output, null, 2));
      process.exit(1);
    }

    try {
      const response = await checkSkillSecurityFullResponse(args.slug, args.version);
      console.log(JSON.stringify(response, null, 2));

      // Determine exit code based on bd_confidence
      if (response.code === 'success' && response.data && response.data.length > 0) {
        const item = response.data[0];
        const bdConfidence = (item.bd_confidence || '').toLowerCase();
        const safe = bdConfidence === 'safe' || bdConfidence === 'trusted';
        process.exit(safe ? 0 : 1);
      } else {
        process.exit(1);
      }
    } catch (error) {
      const output = {
        code: 'error',
        msg: `🚫 安全检查服务调用失败：${error.message || '未知错误'}`,
        ts: Date.now(),
        data: []
      };
      console.log(JSON.stringify(output, null, 2));
      process.exit(1);
    }
  }
}

main().catch((err) => {
  const output = {
    code: 'error',
    msg: `❌ 脚本执行异常：${err.message || '未知错误'}`,
    ts: Date.now(),
    data: []
  };
  console.log(JSON.stringify(output, null, 2));
  process.exit(1);
});