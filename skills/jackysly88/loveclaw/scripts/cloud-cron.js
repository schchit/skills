/**
 * LoveClaw - 云端版定时任务
 * 匹配逻辑在本地（skill）计算，FC 只负责存取数据
 */

const path = require('path');
process.chdir(path.join(process.env.HOME || '/root', '.openclaw', 'workspace'));

const cloudData = require('./cloud-data');
const bazi = require('./bazi');

const MATCH_THRESHOLD = 70; // 双向匹配阈值

/**
 * 计算双向匹配分数（使用 match.js 的算法）
 */
function calculateMutualScore(baziA, baziB) {
  if (!baziA || !baziB) return { scoreAToB: 0, scoreBToA: 0, isMutual: false, mutualScore: 0 };
  const scoreAToB = bazi.calculateMatchScore(baziA, baziB);
  const scoreBToA = bazi.calculateMatchScore(baziB, baziA);
  const isMutual = scoreAToB >= MATCH_THRESHOLD && scoreBToA >= MATCH_THRESHOLD;
  const mutualScore = Math.min(scoreAToB, scoreBToA);
  return { scoreAToB, scoreBToA, isMutual, mutualScore };
}

/**
 * 执行每日匹配（基于 TableStore，云端计算）
 */
async function runDailyMatching() {
  console.log('[匹配任务] 开始执行...');

  const profiles = await cloudData.getAllProfiles();
  console.log(`[匹配任务] 当前用户数: ${profiles.length}`);

  const today = new Date(Date.now() + 8 * 3600 * 1000).toISOString().split('T')[0];
  const matchedSet = new Set();
  const results = [];

  for (const profile of profiles) {
    // 跳过已匹配的用户
    if (matchedSet.has(profile.userId)) continue;
    // 跳过今日已匹配的用户
    if (profile.todayMatchDone === '1' && profile.todayMatchDate === today) {
      matchedSet.add(profile.userId);
      continue;
    }
    // 跳过缺少关键信息的用户
    if (!profile.bazi || !profile.city || !profile.gender || !profile.preferredGender) continue;

    // 查找最佳同城双向匹配
    const cands = profiles.filter(p => {
      if (matchedSet.has(p.userId)) return false;
      if (p.userId === profile.userId) return false;
      if (!p.bazi || !p.city) return false;
      // 同城
      if (p.city !== profile.city) return false;
      // 双向喜欢
      if (p.gender !== profile.preferredGender) return false;
      if (p.preferredGender !== profile.gender) return false;
      return true;
    });

    if (!cands.length) continue;

    // 计算每个候选的匹配分数
    const scored = cands.map(c => {
      const score = calculateMutualScore(profile.bazi, c.bazi);
      return { candidate: c, ...score };
    }).filter(s => s.isMutual);

    if (!scored.length) continue;

    // 取分数最高者
    scored.sort((a, b) => b.mutualScore - a.mutualScore);
    const best = scored[0];

    console.log(`[匹配任务] ${profile.name} ↔ ${best.candidate.name} (${best.mutualScore}分, ${profile.city})`);

    // 构建历史记录
    const uHist = Array.isArray(profile.matchedWithHistory) ? profile.matchedWithHistory : [];
    uHist.push({ userId: best.candidate.userId, name: best.candidate.name, city: best.candidate.city, date: today });
    const pHist = Array.isArray(best.candidate.matchedWithHistory) ? best.candidate.matchedWithHistory : [];
    pHist.push({ userId: profile.userId, name: profile.name, city: profile.city, date: today });

    // 保存双方匹配结果
    const [uSave, pSave] = await Promise.all([
      cloudData.saveMatch(profile.userId, best.candidate.userId, uHist),
      cloudData.saveMatch(best.candidate.userId, profile.userId, pHist),
    ]);

    if (uSave.success && pSave.success) {
      console.log(`[匹配任务] ✅ ${profile.name} 和 ${best.candidate.name} 匹配成功（${best.mutualScore}分）`);
      results.push({ user: profile.name, partner: best.candidate.name, score: best.mutualScore });
    } else {
      console.error(`[匹配任务] ❌ 保存失败: ${profile.userId}->${best.candidate.userId}`, uSave.error, pSave.error);
    }

    matchedSet.add(profile.userId);
    matchedSet.add(best.candidate.userId);
  }

  console.log(`[匹配任务] 完成，共 ${results.length} 对匹配`);
  return results;
}

/**
 * 生成晚8点报告，输出结构化 JSON 供 OpenClaw agent 发送通知
 *
 * 输出格式：
 *   【REPORTS_JSON】[...report items...]【REPORTS_JSON_END】
 *
 * 每条 report item 字段：
 *   channel   - 通知渠道（webchat / feishu 等）
 *   target    - 接收者（手机号 or 飞书 openId）
 *   message   - 发送内容
 *   hasMatch  - 是否匹配成功
 */
async function runEveningReports() {
  console.log('[报告任务] 开始生成...');

  const reports = [];

  try {
    // 1. 获取今日匹配成功的用户
    const data = await cloudData.apiRequest('/api/report');
    const matchedToday = data.matches || [];
    const matchedPhoneSet = new Set(matchedToday.map(m => m.userId));

    for (const m of matchedToday) {
      // 查询匹配对象的姓名和照片
      let partnerName = m.matchedWith;
      let partnerPhotoUrl = '';
      try {
        const partner = await cloudData.getProfile(m.matchedWith);
        if (partner) {
          if (partner.name) partnerName = partner.name;
          if (partner.photoOssUrl) partnerPhotoUrl = partner.photoOssUrl;
        }
      } catch (_) {}

      reports.push({
        channel: m.channel || 'webchat',
        target: m.notificationTarget || m.userId,
        hasMatch: true,
        partnerPhotoUrl,
        message: `🌟 今日缘分已到！\n\n💕 你的有缘人：${partnerName}\n📍 城市：${m.city || '未知'}\n☎️ 联系方式：${m.matchedWith}\n\n快去联系你的有缘人吧！`,
      });
    }

    // 2. 找出今日未匹配的已报名用户，发送安慰通知
    const allProfiles = await cloudData.getAllProfiles();
    for (const p of allProfiles) {
      if (matchedPhoneSet.has(p.userId)) continue;
      // 过滤掉资料不完整的（未完成报名）
      if (!p.name || !p.city || !p.gender || !p.preferredGender) continue;

      reports.push({
        channel: p.channel || 'webchat',
        target: p.notificationTarget || p.userId,
        hasMatch: false,
        message: `🌙 今日缘分未到...\n\n命运的齿轮继续转动，请期待月老明日的光临 ✨\n（无需重新报名，明晚继续自动匹配）`,
      });
    }

    // 输出给 agent 解析的结构化 JSON（单独一行，方便提取）
    console.log('【REPORTS_JSON】' + JSON.stringify(reports) + '【REPORTS_JSON_END】');
    console.log(`[报告任务] 完成：${reports.filter(r => r.hasMatch).length} 份匹配报告，${reports.filter(r => !r.hasMatch).length} 份无匹配通知`);

  } catch (e) {
    console.error('[报告任务] 失败:', e.message);
  }

  return reports;
}

// ========================
// CLI 入口
// ========================
if (require.main === module) {
  const [, , command] = process.argv;

  if (command === 'match') {
    runDailyMatching().then(() => process.exit(0)).catch(e => {
      console.error('[匹配任务异常]', e);
      process.exit(1);
    });
  } else if (command === 'report') {
    runEveningReports().then(() => process.exit(0)).catch(e => {
      console.error('[报告任务异常]', e);
      process.exit(1);
    });
  } else {
    console.log('用法: node cloud-cron.js [match|report]');
    process.exit(1);
  }
}

module.exports = { runDailyMatching, runEveningReports };
