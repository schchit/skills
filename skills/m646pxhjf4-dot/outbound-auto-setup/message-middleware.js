/**
 * 外出任务自动配置 - 消息中间件
 * 用途：在 OpenClaw 处理消息前，先检测外出任务并自动配置
 */

const outboundSkill = require('./index.js');
const fs = require('fs');
const path = require('path');

// 日志文件
const LOG_FILE = path.join(process.env.HOME, '.openclaw/logs/outbound-auto-setup.log');

// 日志函数
function log(message) {
  const timestamp = new Date().toISOString();
  const logLine = `[${timestamp}] ${message}\n`;
  fs.appendFileSync(LOG_FILE, logLine);
}

// 处理用户消息
async function handleUserMessage(message) {
  try {
    log(`收到消息：${message}`);
    
    // 调用外出技能
    const response = await outboundSkill.handleUserMessage(message);
    
    if (response) {
      log(`外出任务配置完成`);
      return response;
    }
    
    log('未检测到外出任务');
    return null;
  } catch (error) {
    log(`错误：${error.message}`);
    console.error('外出任务自动配置失败:', error);
    return null;
  }
}

// 导出
module.exports = {
  handleUserMessage,
  log
};
