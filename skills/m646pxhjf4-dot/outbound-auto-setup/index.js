/**
 * 外出任务自动配置技能
 * 用途：监听用户消息中的外出关键词，自动创建所有提醒
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  enabled: true,
  keywords: ['去', '外出', '出发', '到', '前往'],
  autoSetup: true,
  notifyUser: true
};

// 外出关键词检测
function containsOutboundKeywords(message) {
  return CONFIG.keywords.some(keyword => message.includes(keyword));
}

// 提取外出信息
function extractOutboundInfo(message) {
  const info = {
    date: null,
    time: null,
    location: null,
    task: null,
    type: 'work' // work or life
  };
  
  // 1. 提取日期
  const today = new Date();
  let dateSet = false;
  
  if (message.includes('明天') || message.includes('明日')) {
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    info.date = formatDate(tomorrow);
    dateSet = true;
  } else if (message.includes('后天')) {
    const dayAfter = new Date(today);
    dayAfter.setDate(dayAfter.getDate() + 2);
    info.date = formatDate(dayAfter);
    dateSet = true;
  } else if (message.includes('今天') || message.includes('今日')) {
    info.date = formatDate(today);
    dateSet = true;
  } else if (message.includes('周六') || message.includes('星期六')) {
    // 计算下一个周六
    const dayOfWeek = today.getDay();
    const daysUntilSaturday = (6 - dayOfWeek + 7) % 7;
    const saturday = new Date(today);
    saturday.setDate(today.getDate() + daysUntilSaturday);
    info.date = formatDate(saturday);
    dateSet = true;
  }
  
  if (!dateSet) {
    // 尝试提取具体日期（如 3 月 28 日）
    const dateMatch = message.match(/(\d{1,2}) 月 (\d{1,2}) 日/);
    if (dateMatch) {
      const year = today.getFullYear();
      const month = dateMatch[1].padStart(2, '0');
      const day = dateMatch[2].padStart(2, '0');
      info.date = `${year}-${month}-${day}`;
    }
  }
  
  // 2. 提取时间
  const timeMatch = message.match(/(\d{1,2})[点:：](\d{2})/) || 
                    message.match(/(\d{1,2}) 点/);
  if (timeMatch) {
    let hour = parseInt(timeMatch[1], 10);
    const minute = timeMatch[2] || '00';
    
    // 处理上午/下午
    if (message.includes('下午') || message.includes('晚上')) {
      if (hour < 12) hour += 12;
    } else if (message.includes('上午') || message.includes('早上')) {
      // 上午时间不变
    }
    
    info.time = `${String(hour).padStart(2, '0')}:${minute}`;
  }
  
  // 3. 提取地点（使用字符串方法，不用正则）
  const keywords = ['去', '到', '前往'];
  for (const kw of keywords) {
    const index = message.indexOf(kw);
    if (index !== -1) {
      // 提取地点（从关键词后到下一个动词或句尾）
      const afterKw = message.substring(index + kw.length);
      // 地点通常是 2-10 个字符
      const locationEnd = afterKw.search(/[考拍开会拿取买办了]/);
      if (locationEnd > 1) {
        info.location = afterKw.substring(0, locationEnd).trim();
      } else {
        info.location = afterKw.substring(0, 10).trim();
      }
      break;
    }
  }
  
  // 4. 提取事项
  if (info.location) {
    const locIndex = message.indexOf(info.location);
    if (locIndex !== -1) {
      info.task = message.substring(locIndex + info.location.length).trim();
    }
  }
  
  // 5. 判断类型（工作/生活）
  const lifeKeywords = ['拿', '取', '买', '购物', '访友', '玩'];
  if (lifeKeywords.some(kw => message.includes(kw))) {
    info.type = 'life';
  }
  
  // 验证信息完整性
  if (!info.date || !info.time || !info.location) {
    return null;
  }
  
  return info;
}

// 格式化日期
function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// 自动配置外出提醒
async function setupOutbound(info) {
  const result = {
    success: true,
    appleReminder: false,
    cronJob: false,
    pendingTasks: false,
    error: null
  };
  
  // 计算提醒时间（提前 15 分钟）
  const [hour, minute] = info.time.split(':').map(Number);
  let remindHour = hour;
  let remindMinute = minute - 15;
  if (remindMinute < 0) {
    remindHour--;
    remindMinute += 60;
  }
  const remindTime = `${String(remindHour).padStart(2, '0')}:${String(remindMinute).padStart(2, '0')}`;
  
  // 1. 创建 Apple 提醒事项
  try {
    const typeLabel = info.type === 'work' ? '工作外出' : '生活外出';
    const reminderTitle = `📍 ${typeLabel}：${info.location} - ${info.time}`;
    
    await execPromise(`remindctl add --list "工作" "${reminderTitle}" --due "${info.date} ${remindTime}"`);
    result.appleReminder = true;
  } catch (error) {
    result.error = `Apple 提醒事项创建失败：${error.message}`;
    result.success = false;
  }
  
  // 2. 更新 pending-tasks.md
  try {
    const pendingFile = path.join(process.env.HOME, '.openclaw/workspace/memory/pending-tasks.md');
    const line = `| ${info.date} | ${info.time} | ${info.location} | ${info.task} | ${info.type} | ${new Date().getHours()}:${String(new Date().getMinutes()).padStart(2, '0')} | ✅ 已验证 | ⏳ 待完成 |\n`;
    
    fs.appendFileSync(pendingFile, line);
    result.pendingTasks = true;
  } catch (error) {
    result.error = `pending-tasks.md 更新失败：${error.message}`;
    result.success = false;
  }
  
  return result;
}

// 执行 Promise 包装
function execPromise(command) {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        reject(error);
      } else {
        resolve(stdout);
      }
    });
  });
}

// 格式化报告
function formatReport(info, result) {
  const typeLabel = info.type === 'work' ? '工作外出 ✅' : '生活外出 🏠';
  
  let report = `🚀 **检测到外出任务，正在自动配置...**\n\n`;
  report += `**提取信息**：\n`;
  report += `- 日期：${info.date}\n`;
  report += `- 时间：${info.time}\n`;
  report += `- 地点：${info.location}\n`;
  report += `- 事项：${info.task || '未指定'}\n`;
  report += `- 类型：${typeLabel}\n\n`;
  
  if (result.success) {
    report += `**配置提醒**：\n`;
    report += `- ${result.appleReminder ? '✅' : '❌'} Apple 提醒事项：${info.date} ${result.appleReminder ? '已创建' : '创建失败'}\n`;
    report += `- ${result.pendingTasks ? '✅' : '❌'} pending-tasks.md：${result.pendingTasks ? '已记录' : '记录失败'}\n\n`;
    report += `**状态**：✅ 配置完成`;
  } else {
    report += `**错误**：${result.error}\n\n`;
    report += `**状态**：❌ 配置失败，请手动配置`;
  }
  
  return report;
}

// 主函数：处理用户消息
async function handleUserMessage(message) {
  if (!CONFIG.enabled) {
    return null;
  }
  
  // 检测外出关键词
  if (!containsOutboundKeywords(message)) {
    return null;
  }
  
  // 提取外出信息
  const info = extractOutboundInfo(message);
  if (!info) {
    return '⚠️ 检测到外出关键词，但未识别到完整信息。请提供：日期、时间、地点、事项';
  }
  
  // 自动配置提醒
  const result = await setupOutbound(info);
  
  // 返回报告
  return formatReport(info, result);
}

// 导出
module.exports = {
  handleUserMessage,
  containsOutboundKeywords,
  extractOutboundInfo,
  setupOutbound
};
