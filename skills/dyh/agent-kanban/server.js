const express = require('express');
const path = require('path');
const fs = require('fs');

// 加载配置（优先使用 config.local.js）
let config;
try {
  config = require('./config.local.js');
  console.log('Using config.local.js');
} catch (e) {
  config = require('./config.js');
  console.log('Using config.js (no config.local.js found)');
}

const app = express();
const PORT = config.server.port || 3100;
const HOST = config.server.host || '0.0.0.0';
const GATEWAY_URL = config.gateway.url;

// 获取 Gateway Token（优先使用配置文件，否则从 openclaw.json 读取）
function getGatewayToken() {
  if (config.gateway.token) {
    return config.gateway.token;
  }
  // 自动从 openclaw.json 读取
  try {
    const openclawPath = path.join(
      config.openclaw.homeDir.startsWith('/') 
        ? '' 
        : process.env.HOME, 
      config.openclaw.homeDir.startsWith('/') 
        ? '' 
        : config.openclaw.homeDir,
      config.openclaw.configFilename
    );
    const openclawConfig = JSON.parse(fs.readFileSync(openclawPath, 'utf8'));
    return openclawConfig.gateway?.auth?.token || '';
  } catch (err) {
    console.error('Failed to read gateway token from openclaw.json:', err.message);
    return '';
  }
}

const GATEWAY_TOKEN = getGatewayToken();

// 获取 OpenClaw 主目录
function getOpenClawHome() {
  const homeDir = config.openclaw.homeDir;
  // 如果是绝对路径，直接返回；否则拼接用户主目录
  if (path.isAbsolute(homeDir)) {
    return homeDir;
  }
  return path.join(process.env.HOME, homeDir);
}

const OPENCLAW_HOME = getOpenClawHome();

// 读取 openclaw.json 中的 agent heartbeat 配置
let heartbeatConfig = {};

function loadHeartbeatConfig() {
  try {
    const configPath = path.join(OPENCLAW_HOME, config.openclaw.configFilename);
    const openclawConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    const agentsList = openclawConfig.agents?.list || [];
    
    heartbeatConfig = {};  // 清空旧配置
    for (const agent of agentsList) {
      if (agent.id && agent.heartbeat) {
        heartbeatConfig[agent.id] = {
          enabled: true,
          every: agent.heartbeat.every || ''
        };
      }
    }
    
    console.log(`Loaded heartbeat config for ${Object.keys(heartbeatConfig).length} agents`);
  } catch (err) {
    console.error('Failed to load heartbeat config:', err.message);
  }
}

// 启动时加载配置
loadHeartbeatConfig();

// 记录配置文件修改时间，用于检测变化
let configMtime = 0;
function checkConfigChange() {
  try {
    const configPath = path.join(OPENCLAW_HOME, config.openclaw.configFilename);
    const stats = fs.statSync(configPath);
    if (stats.mtimeMs > configMtime) {
      if (configMtime > 0) {
        console.log('Config file changed, reloading heartbeat config...');
      }
      configMtime = stats.mtimeMs;
      loadHeartbeatConfig();
    }
  } catch (err) {
    console.error('Failed to check config change:', err.message);
  }
}

app.use(express.static('public'));
app.use(express.json());

// CORS - 只允许本地访问
app.use((req, res, next) => {
  const allowedOrigins = ['http://localhost:3100', 'http://127.0.0.1:3100'];
  const origin = req.headers.origin;
  if (allowedOrigins.includes(origin)) {
    res.header('Access-Control-Allow-Origin', origin);
  }
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// Gateway 健康状态
let gatewayHealthy = true;

// 检查 Gateway 是否可用
async function checkGatewayHealth() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    
    const response = await fetch(`${GATEWAY_URL}/health`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return response.ok;
  } catch {
    return false;
  }
}

// 调用 Gateway HTTP API
async function gatewayInvoke(tool, args = {}) {
  // 安全检查：允许本地地址和局域网 IP
  try {
    const gatewayHost = new URL(GATEWAY_URL).hostname;
    const isLocalhost = ['127.0.0.1', 'localhost', '::1'].includes(gatewayHost);
    const isPrivateIP = gatewayHost.startsWith('192.168.') || 
                        gatewayHost.startsWith('10.') || 
                        gatewayHost.startsWith('172.');
    if (!isLocalhost && !isPrivateIP) {
      const error = new Error(`Security: Gateway URL must be localhost or private IP, got ${gatewayHost}`);
      error.code = 'SECURITY_VIOLATION';
      throw error;
    }
  } catch (err) {
    if (err.code === 'SECURITY_VIOLATION') throw err;
    const error = new Error(`Invalid Gateway URL: ${GATEWAY_URL}`);
    error.code = 'INVALID_URL';
    throw error;
  }
  
  // 检查 Token
  if (!GATEWAY_TOKEN) {
    const error = new Error('Gateway Token 未配置');
    error.code = 'TOKEN_MISSING';
    throw error;
  }
  
  // 发送请求（带超时）
  let response;
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 秒超时
    
    response = await fetch(`${GATEWAY_URL}/tools/invoke`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${GATEWAY_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ tool, args }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    gatewayHealthy = true;
    
  } catch (err) {
    gatewayHealthy = false;
    
    // 网络错误（Gateway 未启动）
    if (err.name === 'AbortError') {
      const error = new Error('Gateway 响应超时');
      error.code = 'GATEWAY_TIMEOUT';
      throw error;
    }
    if (err.cause?.code === 'ECONNREFUSED' || err.code === 'ECONNREFUSED') {
      const error = new Error('Gateway 未启动');
      error.code = 'GATEWAY_NOT_RUNNING';
      throw error;
    }
    // 其他网络错误
    const error = new Error(`网络错误: ${err.message}`);
    error.code = 'NETWORK_ERROR';
    throw error;
  }
  
  // 处理 HTTP 状态码
  if (response.status === 401 || response.status === 403) {
    const error = new Error('Gateway Token 无效');
    error.code = 'TOKEN_INVALID';
    throw error;
  }
  if (response.status === 503) {
    gatewayHealthy = false;
    const error = new Error('Gateway 服务不可用');
    error.code = 'GATEWAY_UNAVAILABLE';
    throw error;
  }
  if (!response.ok) {
    const error = new Error(`Gateway 错误: HTTP ${response.status}`);
    error.code = 'GATEWAY_ERROR';
    error.status = response.status;
    throw error;
  }
  
  // 解析响应
  let data;
  try {
    data = await response.json();
  } catch (err) {
    const error = new Error('Gateway 返回无效 JSON');
    error.code = 'INVALID_RESPONSE';
    throw error;
  }
  
  if (!data.ok) {
    const error = new Error(data.error?.message || 'Unknown error');
    error.code = 'API_ERROR';
    throw error;
  }
  
  return data.result;
}

// 解析 sessions_list 结果，提取前端需要的字段
function parseSessionsList(result) {
  const sessions = [];
  
  // result 可能是 { content: [{ type: "text", text: "..." }] }
  // 也可能是直接的对象
  let data = result;
  if (result.content && Array.isArray(result.content)) {
    const textContent = result.content.find(c => c.type === 'text');
    if (textContent) {
      try {
        data = JSON.parse(textContent.text);
      } catch (e) {
        console.error('Failed to parse sessions_list result:', e);
        return { sessions: [] };
      }
    }
  }
  
  const rawSessions = data.sessions || data.details?.sessions || [];
  
  // 检查 agent 是否有变化，有变化则刷新配置
  const currentAgentIds = new Set(rawSessions.map(s => (s.key || '').split(':')[1]).filter(id => id));
  const configAgentIds = new Set(Object.keys(heartbeatConfig));
  
  // 判断是否有新增或删除的 agent
  const hasNewAgent = [...currentAgentIds].some(id => !configAgentIds.has(id));
  const hasRemovedAgent = [...configAgentIds].some(id => !currentAgentIds.has(id));
  
  if (hasNewAgent || hasRemovedAgent) {
    const newAgents = [...currentAgentIds].filter(id => !configAgentIds.has(id));
    const removedAgents = [...configAgentIds].filter(id => !currentAgentIds.has(id));
    if (newAgents.length > 0) console.log(`New agents detected: ${newAgents.join(', ')}`);
    if (removedAgents.length > 0) console.log(`Agents removed: ${removedAgents.join(', ')}`);
    loadHeartbeatConfig();
  }
  
  for (const s of rawSessions) {
    // 提取 agent ID
    const parts = (s.key || '').split(':');
    const agentId = parts[1] || 'unknown';
    
    // 获取 heartbeat 配置
    const hbConfig = heartbeatConfig[agentId] || null;
    
    sessions.push({
      key: s.key,
      agentId: agentId,
      sessionId: s.sessionId,
      channel: s.channel,
      displayName: s.displayName,
      model: s.model,
      contextTokens: s.contextTokens,
      updatedAt: s.updatedAt,
      age: s.updatedAt ? Date.now() - s.updatedAt : Infinity,
      heartbeat: hbConfig,
      lastMessage: null,  // 需要从 history 获取
      lastMessageTime: s.updatedAt
    });
  }
  
  return { sessions };
}

// 解析 sessions_history 结果
function parseSessionHistory(result) {
  // result 可能是 { content: [{ type: "text", text: "..." }] }
  // 也可能是直接的对象
  let data = result;
  if (result.content && Array.isArray(result.content)) {
    const textContent = result.content.find(c => c.type === 'text');
    if (textContent) {
      try {
        data = JSON.parse(textContent.text);
      } catch (e) {
        console.error('Failed to parse sessions_history result:', e);
        return { messages: [] };
      }
    }
  }
  
  const messages = [];
  const rawMessages = data.messages || data.details?.messages || [];
  
  for (const msg of rawMessages) {
    // 处理 content 字段
    let content = msg.content || '';
    
    // 如果 content 是数组，提取文本
    if (Array.isArray(content)) {
      const textParts = [];
      for (const item of content) {
        if (item.type === 'text') {
          textParts.push(item.text || '');
        } else if (item.type === 'thinking') {
          textParts.push('[思考] ' + (item.thinking || ''));
        } else if (item.type === 'toolCall') {
          textParts.push('[工具] ' + (item.name || ''));
        }
      }
      content = textParts.join('\n');
    }
    
    messages.push({
      role: msg.role,
      content: content,
      timestamp: msg.timestamp
    });
  }
  
  return { messages };
}

// 获取 agent 的 jsonl 文件大小（KB）
function getAgentJsonlSize(agentId) {
  const sessionDir = path.join(OPENCLAW_HOME, 'agents', agentId, 'sessions');
  
  if (!fs.existsSync(sessionDir)) return 0;
  
  let totalSize = 0;
  const files = fs.readdirSync(sessionDir).filter(f => f.endsWith('.jsonl'));
  
  for (const file of files) {
    const filePath = path.join(sessionDir, file);
    const stats = fs.statSync(filePath);
    totalSize += stats.size;
  }
  
  return Math.round(totalSize / 1024); // KB
}

// API: 获取 Gateway 健康状态
app.get('/api/health', async (req, res) => {
  const healthy = await checkGatewayHealth();
  gatewayHealthy = healthy;
  res.json({ 
    kanban: true,
    gateway: healthy,
    gatewayUrl: GATEWAY_URL
  });
});

// API: 获取所有 sessions
app.get('/api/sessions', async (req, res) => {
  try {
    // 检查配置文件是否有变化
    checkConfigChange();
    
    const result = await gatewayInvoke('sessions_list', {});
    const data = parseSessionsList(result);
    
    // 添加每个 agent 的 jsonl 文件大小
    for (const s of data.sessions) {
      s.jsonlSizeKB = getAgentJsonlSize(s.agentId);
    }
    
    res.json(data);
  } catch (err) {
    console.error('Failed to get sessions:', err.message);
    
    // 根据错误类型返回不同的状态码和提示
    const errorResponse = {
      error: err.message,
      code: err.code || 'UNKNOWN'
    };
    
    switch (err.code) {
      case 'GATEWAY_NOT_RUNNING':
        return res.status(503).json({
          ...errorResponse,
          hint: '请运行 openclaw gateway start'
        });
      case 'GATEWAY_TIMEOUT':
        return res.status(504).json(errorResponse);
      case 'TOKEN_INVALID':
      case 'TOKEN_MISSING':
        return res.status(401).json(errorResponse);
      case 'GATEWAY_UNAVAILABLE':
        return res.status(503).json(errorResponse);
      case 'NETWORK_ERROR':
        return res.status(502).json(errorResponse);
      default:
        return res.status(500).json(errorResponse);
    }
  }
});

// API: 获取指定 session 的历史
app.get('/api/sessions/:key/history', async (req, res) => {
  try {
    const sessionKey = decodeURIComponent(req.params.key);
    const result = await gatewayInvoke('sessions_history', { 
      sessionKey,
      limit: 100
    });
    const data = parseSessionHistory(result);
    res.json(data);
  } catch (err) {
    console.error('Failed to get session history:', err.message);
    
    const errorResponse = {
      error: err.message,
      code: err.code || 'UNKNOWN'
    };
    
    // 复用相同的错误处理逻辑
    if (['GATEWAY_NOT_RUNNING', 'GATEWAY_UNAVAILABLE'].includes(err.code)) {
      return res.status(503).json(errorResponse);
    }
    if (err.code === 'GATEWAY_TIMEOUT') {
      return res.status(504).json(errorResponse);
    }
    if (['TOKEN_INVALID', 'TOKEN_MISSING'].includes(err.code)) {
      return res.status(401).json(errorResponse);
    }
    if (err.code === 'NETWORK_ERROR') {
      return res.status(502).json(errorResponse);
    }
    
    res.status(500).json(errorResponse);
  }
});

// API: 获取 agent 的文件（SOUL.md, HEARTBEAT.md）
app.get('/api/agents/:agentId/files', async (req, res) => {
  try {
    const agentId = decodeURIComponent(req.params.agentId);
    const workspaceDir = path.join(OPENCLAW_HOME, `workspace-${agentId}`);
    
    const files = {};
    const fileNames = ['SOUL.md', 'HEARTBEAT.md'];
    
    for (const fileName of fileNames) {
      const filePath = path.join(workspaceDir, fileName);
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');
        files[fileName] = {
          exists: true,
          content: content,
          lines: content.split('\n').length,
          size: Math.round(content.length / 1024) + 'KB'
        };
      } else {
        files[fileName] = {
          exists: false,
          content: '',
          lines: 0,
          size: '0KB'
        };
      }
    }
    
    res.json({ agentId, files });
  } catch (err) {
    console.error('Failed to get agent files:', err);
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, HOST, async () => {
  console.log(`Agent Kanban running at http://${HOST}:${PORT}`);
  console.log(`Using Gateway HTTP API: ${GATEWAY_URL}`);
  
  // 检查 Gateway 是否可用
  const healthy = await checkGatewayHealth();
  gatewayHealthy = healthy;
  
  if (!healthy) {
    console.warn('⚠️  Gateway 未响应，请确保 Gateway 已启动：openclaw gateway start');
  } else {
    console.log('✅ Gateway 连接正常');
  }
  
  // 检查 Token
  if (!GATEWAY_TOKEN) {
    console.warn('⚠️  Gateway Token 未配置，请在 config.local.js 中设置或确保 openclaw.json 中有 token');
  }
});