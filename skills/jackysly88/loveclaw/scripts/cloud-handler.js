/**
 * 八字缘分匹配 - 云端版会话处理 v2.0.0
 * 简化流程：手机号即账号，匹配后才能看到对方信息
 * v2.0.0: 多channel支持 - 用户通过什么渠道报名，就通过什么渠道收到通知
 */

const cloudData = require('./cloud-data');
const bazi = require('./bazi');
const match = require('./match');
const fs = require('fs');
const os = require('os');

// ==================== SESSION MANAGEMENT ====================
const SESSION_FILE = os.homedir() + '/.openclaw/workspace/skills/loveclaw/sessions.json';
let userSessions = new Map(); // userId -> { state, data }
let idMap = {}; // phone -> userId

// Session states
const UserState = {
  NONE: 0,
  PHONE: 1,      // waiting for phone
  NAME: 2,      // waiting for name
  GENDER: 3,    // waiting for gender
  PREFERRED_GENDER: 4,
  BIRTH_DATE: 5,
  BIRTH_HOUR: 6,
  CITY: 7,
  PHOTO: 8,
  CONFIRM: 9,
};

// Load sessions from file
function loadSessionsFromFile() {
  try {
    const dataStr = fs.readFileSync(SESSION_FILE, 'utf-8');
    const loaded = JSON.parse(dataStr);
    delete loaded._idMap;
    loaded._idMap = JSON.parse(dataStr)._idMap || {};
    return loaded;
  } catch {
    return { _idMap: {} };
  }
}

// Save sessions to file
function saveSessionsToFile(sessionList) {
  try {
    const allData = loadSessionsFromFile();
    for (const { userId, session } of sessionList) {
      if (userId) {
        allData[userId] = session;
      }
    }
    allData._idMap = idMap;
    fs.writeFileSync(SESSION_FILE, JSON.stringify(allData, null, 2));
  } catch (e) {
    console.error('Save error:', e.message);
  }
}

// Get or create user session - NEVER overwrites existing session data
function getUserSession(userId) {
  if (userSessions.has(userId)) {
    return userSessions.get(userId);
  }
  // New user - load from file
  const loaded = loadSessionsFromFile();
  const idMapLoad = loaded._idMap || {};
  delete loaded._idMap;
  for (const [k, v] of Object.entries(loaded)) {
    v._idMap = idMapLoad[k];
    userSessions.set(k, v);
  }
  if (idMapLoad[userId] && userSessions.has(idMapLoad[userId])) {
    return userSessions.get(idMapLoad[userId]);
  } else if (userSessions.has(userId)) {
    return userSessions.get(userId);
  }
  const newSession = { state: UserState.NONE, data: {} };
  userSessions.set(userId, newSession);
  // Persist immediately so session survives process restarts
  saveSessionsToFile([{ userId, session: newSession }]);
  return newSession;
}

// ==================== HANDLER ====================

/**
 * @param {string} userId - User identifier
 * @param {string} message - User message  
 * @param {string} channel - User's channel (feishu/webchat/etc), defaults to webchat
 */
async function handleMessage(userId, message, channel = 'webchat') {
  const session = getUserSession(userId);
  
  // Ensure channel is stored in session for notification routing
  if (channel && !session.data.channel) {
    session.data.channel = channel;
  }
  
  try {
    // ==================== GLOBAL COMMANDS (any state) ====================
    if (message === '我的档案' || message === '查看档案') {
      const phoneOrId = session.data.phone || userId;
      const profile = await cloudData.getProfile(phoneOrId);
      if (!profile) return { text: '你还没有报名，请先发送「开启匹配」' };
      return formatProfile(profile);
    }
    if (message === '今日匹配' || message === '查看匹配') {
      const phoneOrId = session.data.phone || userId;
      const profile = await cloudData.getProfile(phoneOrId);
      if (!profile) return { text: '你还没有报名，请先发送「开启匹配」\n\n💡 如果你已经报名，可能是因为换了新对话导致找不到记录。请直接输入你报名时的手机号，即可查到你的匹配情况。' };
      const today = new Date(Date.now() + 8 * 3600 * 1000).toISOString().split('T')[0];
      if (profile.matchedWith && profile.todayMatchDate === today) {
        // 已匹配，查询对方信息
        let partnerName = profile.matchedWith;
        let partnerCity = '';
        let partnerPhotoUrl = '';
        try {
          const partner = await cloudData.getProfile(profile.matchedWith);
          if (partner) {
            if (partner.name) partnerName = partner.name;
            if (partner.city) partnerCity = partner.city;
            if (partner.photoOssUrl) partnerPhotoUrl = partner.photoOssUrl;
          }
        } catch (_) {}
        const cityStr = partnerCity ? `📍 城市：${partnerCity}\n` : '';
        const photoStr = partnerPhotoUrl ? `\n\n${partnerPhotoUrl}` : '';
        return {
          text: `🌟 今日缘分已到！\n\n💕 你的有缘人：${partnerName}\n${cityStr}☎️ 联系方式：${profile.matchedWith}\n\n快去联系你的有缘人吧！${photoStr}`
        };
      }
      return { text: '🌙 今日缘分还未到...\n\n系统每天 19:50 自动匹配，20:00 出结果。匹配后你会收到通知，也可以 20:00 后再回复「今日匹配」查看结果 🔮' };
    }
    if (message === '取消报名') {
      const phoneOrId = session.data.phone || userId;
      const profile = await cloudData.getProfile(phoneOrId);
      if (!profile) return { text: '你还没有报名，无需取消' };
      await cloudData.deleteProfile(phoneOrId);
      resetUserSession(userId);
      resetUserSession(phoneOrId);
      return { text: '已取消报名，你的所有信息已删除。如需重新报名，请发送「开启匹配」。' };
    }
    if (message === '开启匹配') {
      // If first time (no _greeted), show welcome + start registration in one shot
      if (!session.data._greeted) {
        session.data._greeted = true;
        session.state = UserState.PHONE;
        saveSessionsToFile([{ userId, session }]);
        return {
          text: `💕 欢迎使用 LoveClaw 八字缘分匹配！\n\n我会根据你的八字，在同城寻找五行相配的有缘人，每天晚上8点通知你匹配结果。\n\n让我们开始吧 🔮\n\n请输入你的手机号（用于登录和匹配通知）`
        };
      }
      // Already greeted or returning user — reset and restart registration
      session.state = UserState.PHONE;
      session.data = { channel: session.data.channel, _greeted: true };
      saveSessionsToFile([{ userId, session }]);
      return { text: '请输入你的手机号（用于登录和匹配通知）' };
    }

    // ==================== PHONE LOOKUP (NONE state, not in registration) ====================
    if (/^1\d{10}$/.test(message) && session.state === UserState.NONE) {
      const profile = await cloudData.getProfile(message);
      if (profile) {
        // 绑定手机号到当前 session，后续命令可直接查到档案
        session.data.phone = message;
        saveSessionsToFile([{ userId, session }]);
        return { text: `✅ 已找到你的档案！\n\n发送「今日匹配」查看今天的匹配结果，或「我的档案」查看个人信息。` };
      }
      return { text: '未找到该手机号的报名记录。请发送「开启匹配」开始报名。' };
    }

    // ==================== STATE: NONE (start) ====================
    if (session.state === UserState.NONE) {
      // 首次使用：先显示欢迎语，不论用户发了什么消息
      if (!session.data._greeted) {
        session.data._greeted = true;
        saveSessionsToFile([{ userId, session }]);
        return {
          text: `💕 欢迎使用 LoveClaw 八字缘分匹配！\n\n我会根据你的八字，在同城寻找五行相配的有缘人，每天晚上8点通知你匹配结果。\n\n📌 使用方法：\n• 发送「开启匹配」→ 填写信息报名\n• 发送「我的档案」→ 查看个人信息和匹配历史\n• 发送「取消报名」→ 删除全部数据\n\n准备好了吗？发送「开启匹配」开始吧 🔮`
        };
      }
      return { text: '发送「开启匹配」开始缘分匹配，或「查看档案」查看你的信息' };
    }

    // ==================== PHONE ====================
    if (/^1\d{10}$/.test(message) && session.state === UserState.PHONE) {
      // If phone already taken, reject (getProfile is async!)
      const existing = await cloudData.getProfile(message);
      if (existing) {
        return { text: '该手机号已报名，请联系管理员或换一个手机号' };
      }
      session.data.phone = message;
      // Keep BOTH keys (old userId AND phone) so subsequent messages from either ID work
      const oldUserId = [...userSessions.entries()].find(([k, v]) => v === session)?.[0];
      if (oldUserId && oldUserId !== message) {
        idMap[message] = oldUserId; // phone -> original userId
        userSessions.set(message, session); // also store under phone
        // Do NOT delete old key - keep both mappings active
      }
      session.state = UserState.NAME;
      saveSessionsToFile([{ userId, session }]);
      return { text: `手机号 ${message} 已绑定\n请输入你的姓名（或昵称）` };
    }

    // ==================== NAME ====================
    if (session.state === UserState.NAME) {
      session.data.name = message;
      session.state = UserState.GENDER;
      saveSessionsToFile([{ userId, session }]);
      return { text: '请选择你的性别：男 / 女' };
    }

    // ==================== GENDER ====================
    if (session.state === UserState.GENDER) {
      if (!['男', '女'].includes(message)) {
        return { text: '请回复「男」或「女」' };
      }
      session.data.gender = message;
      session.state = UserState.PREFERRED_GENDER;
      saveSessionsToFile([{ userId, session }]);
      return { text: `你的性别是${message}，喜欢什么性别？` };
    }

    // ==================== PREFERRED GENDER ====================
    if (session.state === UserState.PREFERRED_GENDER) {
      if (!['男', '女', '不限'].includes(message)) {
        return { text: '请回复「男」「女」或「不限」' };
      }
      session.data.preferredGender = message;
      session.state = UserState.BIRTH_DATE;
      saveSessionsToFile([{ userId, session }]);
      return { text: '请输入你的出生日期\n格式：YYYY-MM-DD\n例如：1995-05-20' };
    }

    // ==================== BIRTH DATE ====================
    if (session.state === UserState.BIRTH_DATE) {
      const bdMatch = message.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
      if (!bdMatch) {
        return { text: '日期格式不正确，请使用 YYYY-MM-DD，例如：1995-05-20' };
      }
      const date = new Date(message);
      if (isNaN(date.getTime())) {
        return { text: '日期无效，请检查后重试' };
      }
      session.data.birthDate = message;
      session.data.birthDateObj = date;
      session.state = UserState.BIRTH_HOUR;
      saveSessionsToFile([{ userId, session }]);
      return { text: '请输入出生时辰（小时 0-23）\n例如：14 代表下午2点\n或输入地支：子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥' };
    }

    // ==================== BIRTH HOUR ====================
    if (session.state === UserState.BIRTH_HOUR) {
      const diZhiMap = { '子': 23, '丑': 1, '寅': 3, '卯': 5, '辰': 7, '巳': 9, '午': 11, '未': 13, '申': 15, '酉': 17, '戌': 19, '亥': 21 };
      const input = message.trim();
      let hour;
      if (/^\d{1,2}$/.test(input) && parseInt(input) >= 0 && parseInt(input) <= 23) {
        hour = parseInt(input);
      } else if (diZhiMap.hasOwnProperty(input)) {
        hour = diZhiMap[input];
      } else {
        return { text: '请输入 0-23 之间的数字，或地支（子丑寅卯辰巳午未申酉戌亥）' };
      }
      session.data.birthHour = hour;
      session.state = UserState.CITY;
      saveSessionsToFile([{ userId, session }]);
      return { text: '请输入你所在城市' };
    }

    // ==================== CITY ====================
    if (session.state === UserState.CITY) {
      session.data.city = message;
      session.state = UserState.PHOTO;
      saveSessionsToFile([{ userId, session }]);
      return { text: '请发送一张照片用于匹配展示\n（可上传图片，或回复「跳过」不展示照片）' };
    }

    // ==================== PHOTO ====================
    if (session.state === UserState.PHOTO) {
      if (message !== '跳过') {
        session.data.photo = message; // store photo URL or path
      }
      session.state = UserState.CONFIRM;
      saveSessionsToFile([{ userId, session }]);
      return formatSummary(session.data);
    }

    // ==================== CONFIRM ====================
    if (message === '确认' && session.state === UserState.CONFIRM) {
      // Channel from the current call's parameter (most reliable)
      const notifyChannel = session.data.channel || channel || 'webchat';
      try {
        // Calculate bazi
        const baziResult = bazi.calculateBazi(session.data.birthDate, session.data.birthHour);
        const profile = {
          ...session.data,
          userId: session.data.phone, // phone as primary ID
          channel: notifyChannel, // USE THE CHANNEL FROM SESSION (set during registration flow)
          notificationTarget: userId, // original channel user ID (open_id for feishu, etc.)
          bazi: baziResult,
          createdAt: new Date().toISOString(),
          todayMatchDone: false,
          todayMatchDate: '',
          matchedWith: '',
          matchedWithHistory: []
        };
        await cloudData.saveProfile(profile);
        // Clear session
        const phone = session.data.phone;
        saveSessionsToFile([{ userId, session: { state: UserState.NONE, data: { phone } } }]);
        delete idMap[phone];
        userSessions.delete(userId);
        userSessions.delete(phone);
        const webchatTip = notifyChannel === 'webchat'
          ? '\n• 📱 你通过对话框报名，每晚 20:00 后请手动回复「今日匹配」查看结果（对话框暂不支持自动推送）'
          : '';
        return {
          text: `报名成功！🎉\n\n你的八字已纳入缘分匹配池。系统每天 19:50 自动匹配，20:00 推送结果——今天 19:50 前报名，今晚就有机会收到你的第一个匹配！\n\n📌 温馨提示：\n• 无需重复报名，每日自动匹配，有缘人会准时送达 🔮\n• 回复「我的档案」可查看个人信息和匹配历史\n• 如需退出匹配，回复「取消报名」删除全部数据${webchatTip}`
        };
      } catch (e) {
        return { text: '保存失败: ' + e.message };
      }
    }

    // CONFIRM not matched but session is CONFIRM - show summary again
    if (session.state === UserState.CONFIRM) {
      return formatSummary(session.data);
    }

    // Fallback
    return { text: '请完成当前步骤，或发送「开启匹配」重新开始' };

  } catch (e) {
    return { text: '处理出错: ' + e.message };
  }
}

function formatSummary(data) {
  const genderText = data.gender === '男' ? '女性' : '男性';
  const bd = data.birthDate;
  const hour = data.birthHour;
  const baziPreview = tryBazi(data);
  return {
    text: `📋 信息确认\n\n姓名：${data.name}\n性别：${data.gender}，希望认识：${data.preferredGender}\n生日：${bd} ${data.birthHour}时\n城市：${data.city}\n${baziPreview}\n\n以上信息确认无误？确认报名请回复「确认」，修改请重新发送对应信息。`
  };
}

function tryBazi(data) {
  try {
    const result = bazi.calculateBazi(data.birthDate, data.birthHour);
    return `八字：${result.year}年 ${result.month}月 ${result.day}日 ${result.hour}时`;
  } catch {
    return '';
  }
}

function formatProfile(profile) {
  // bazi 可能是嵌套对象（注册时传入），也可能是分开字段（从云端读取）
  let baziStr = '未知';
  if (profile.bazi && profile.bazi.year) {
    baziStr = `${profile.bazi.year}年 ${profile.bazi.month}月 ${profile.bazi.day}日 ${profile.bazi.hour}时`;
  } else if (profile.baziYear) {
    baziStr = `${profile.baziYear}年 ${profile.baziMonth}月 ${profile.baziDay}日 ${profile.baziHour || ''}时`;
  }
  const matched = profile.matchedWithHistory || [];
  const matchedList = matched.length > 0
    ? matched.map(m => `  • ${m.name || m.userId}（${m.city || ''}）${m.date ? ' · ' + m.date : ''}`).join('\n')
    : '暂无';
  return {
    text: `📋 你的档案\n\n姓名：${profile.name}\n性别：${profile.gender}，喜欢：${profile.preferredGender}\n生日：${profile.birthDate} ${profile.birthHour}时\n城市：${profile.city}\n八字：${baziStr}\n\n匹配历史：\n${matchedList}\n\n发送「开启匹配」可重新报名`
  };
}

function resetUserSession(userId) {
  userSessions.delete(userId);
}

// ==================== CRON AUTO-REGISTER ====================
// Run once on skill load to ensure cron jobs exist.
// Uses `openclaw cron list --json` to check before adding (idempotent).
(function ensureLoveClawCronJobs() {
  try {
    const { execSync } = require('child_process');
    const openclawBin = process.env.OPENCLAW_BIN || 'openclaw';

    let existingNames = [];
    try {
      const out = execSync(`${openclawBin} cron list --json 2>/dev/null`, { encoding: 'utf-8', timeout: 12000 });
      // Output may contain [plugins] warning lines before the JSON — extract only the JSON object
      const jsonMatch = out.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        existingNames = (parsed.jobs || []).map(j => j.name || '');
      }
    } catch (_) {}

    if (!existingNames.includes('LoveClaw-每日匹配')) {
      execSync(
        `${openclawBin} cron add` +
        ` --name "LoveClaw-每日匹配"` +
        ` --cron "50 19 * * *"` +
        ` --tz "Asia/Shanghai"` +
        ` --session isolated` +
        ` --no-deliver` +
        ` --message "执行每日八字匹配任务。请运行: cd ~/.openclaw/workspace/skills/loveclaw/scripts && node cloud-cron.js match。匹配结果已存入云端。"`,
        { timeout: 15000, stdio: 'ignore' }
      );
    }

    if (!existingNames.includes('LoveClaw-晚间报告')) {
      execSync(
        `${openclawBin} cron add` +
        ` --name "LoveClaw-晚间报告"` +
        ` --cron "0 20 * * *"` +
        ` --tz "Asia/Shanghai"` +
        ` --session isolated` +
        ` --no-deliver` +
        ` --message "执行每日八字匹配晚间报告，步骤如下：\n\n1. 运行命令：cd ~/.openclaw/workspace/skills/loveclaw/scripts && node cloud-cron.js report\n2. 从命令输出中找到 【REPORTS_JSON】 和 【REPORTS_JSON_END】 之间的内容，解析为 JSON 数组\n3. 对数组中的每一条记录，使用 message 工具发送通知：\n   - channel：使用 item.channel 字段（如 webchat、feishu）\n   - target：使用 item.target 字段（用户手机号或渠道 ID）\n   - 内容：直接使用 item.message 字段，不要修改\n4. 若该条记录的 item.partnerPhotoUrl 不为空字符串，则在发送文字消息之后，额外再发一条图片消息到同一个 channel 和 target，内容为该图片 URL\n5. 若 JSON 数组为空，则不发送任何消息，静默退出"`,
        { timeout: 15000, stdio: 'ignore' }
      );
    }
  } catch (_) {}
})();

module.exports = {
  handleMessage,
  resetUserSession,
  getUserSession: (uid) => userSessions.get(uid),
  runEveningReports: () => require('./cron.js').runEveningReports()
};
