/**
 * OpenClaw 消息处理钩子 - 外出任务自动配置
 * 
 * 用途：在收到用户消息时，自动检测外出关键词并配置提醒
 * 集成方式：作为消息中间件，在消息处理前调用
 */

const path = require('path');
const outboundSkill = require('./outbound-auto-setup/index.js');

// 配置
const CONFIG = {
  enabled: true,
  priority: 1, // 优先级（数字越小优先级越高）
  logFile: path.join(process.env.HOME, '.openclaw/logs/outbound-auto-setup.log')
};

// 日志函数
function log(message) {
  const timestamp = new Date().toISOString();
  const logLine = `[${timestamp}] ${message}\n`;
  console.log(logLine.trim());
  
  // 写入日志文件
  const fs = require('fs');
  fs.appendFileSync(CONFIG.logFile, logLine);
}

// 消息处理钩子
async function onUserMessage(context) {
  if (!CONFIG.enabled) {
    return null;
  }
  
  const { message, userId, channelId } = context;
  
  // 记录收到的消息
  log(`收到消息：${message} (用户：${userId}, 频道：${channelId})`);
  
  try {
    // 调用外出任务自动配置技能
    const response = await outboundSkill.handleUserMessage(message);
    
    if (response) {
      log(`外出任务配置完成：${response.substring(0, 100)}...`);
      return {
        reply: response,
        auto: true,
        skill: 'outbound-auto-setup'
      };
    }
    
    log('未检测到外出任务');
    return null;
  } catch (error) {
    log(`❌ 错误：${error.message}`);
    console.error('外出任务自动配置失败:', error);
    return null;
  }
}

// 导出钩子函数
module.exports = {
  name: 'outbound-auto-setup',
  version: '1.0.0',
  description: '外出任务自动配置',
  hooks: {
    'message:receive': onUserMessage
  },
  config: CONFIG,
  enable: () => { CONFIG.enabled = true; log('技能已启用'); },
  disable: () => { CONFIG.enabled = false; log('技能已禁用'); }
};
