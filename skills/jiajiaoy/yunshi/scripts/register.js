#!/usr/bin/env node
/**
 * 快速注册脚本
 * 用于命令行快速注册新用户
 */

const fs = require('fs');
const path = require('path');
const { getLunarMonth, isAfterLiChun } = require('./jieqi');
const { runFullAnalysis } = require('./bazi-analysis');

// 天干地支
const tianGan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
const diZhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
const zodiacMap = { '子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔', '辰': '龙', '巳': '蛇', '午': '马', '未': '羊', '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪' };

/**
 * 内置八字计算（使用精确节气算法）
 */
function calculateBazi(birthDate, birthTime, gender, sect = 1) {
  const [year, month, day] = birthDate.split('-').map(Number);
  const [hour] = birthTime.split(':').map(Number);

  // 年柱（以立春精确时刻为界）
  const calcYear = isAfterLiChun(year, month, day) ? year : year - 1;
  const yearGanIndex = ((calcYear - 4) % 10 + 10) % 10;
  const yearZhiIndex = ((calcYear - 4) % 12 + 12) % 12;

  // 月柱（以精确节气为界）
  const lunarMonth = getLunarMonth(year, month, day);
  const monthZhiIndex = (lunarMonth + 1) % 12;
  const monthGanBases = [2, 4, 6, 8, 0]; // 甲己起丙，乙庚起戊，丙辛起庚，丁壬起壬，戊癸起甲
  const monthGanIndex = (monthGanBases[yearGanIndex % 5] + lunarMonth - 1) % 10;

  // 日柱（以2024-01-01甲子日为基准）
  let calcDate = new Date(`${birthDate}T12:00:00`);
  if (sect === 1 && hour === 23) calcDate.setDate(calcDate.getDate() + 1); // 晚子时算次日
  const baseDate = new Date('2024-01-01T12:00:00');
  const diffDays = Math.round((calcDate - baseDate) / (1000 * 60 * 60 * 24));
  const dayGanIndex = (diffDays % 10 + 10) % 10; // 2024-01-01=甲子(甲=0)
  const dayZhiIndex = (diffDays % 12 + 12) % 12; // 2024-01-01=甲子(子=0)

  // 时柱（五鼠遁日）
  const hourZhiIndex = (sect === 1 && hour === 23) ? 0 : Math.floor((hour + 1) / 2) % 12;
  const hourGanBases = [0, 2, 4, 6, 8]; // 甲己起甲，乙庚起丙，丙辛起戊，丁壬起庚，戊癸起壬
  const hourGanIndex = (hourGanBases[dayGanIndex % 5] + hourZhiIndex) % 10;

  return {
    year: tianGan[yearGanIndex] + diZhi[yearZhiIndex],
    month: tianGan[monthGanIndex] + diZhi[monthZhiIndex],
    day: tianGan[dayGanIndex] + diZhi[dayZhiIndex],
    hour: tianGan[hourGanIndex] + diZhi[hourZhiIndex],
    dayStem: tianGan[dayGanIndex],
    zodiac: zodiacMap[diZhi[yearZhiIndex]]
  };
}

/**
 * 生成初始档案
 */
function createProfile(userId, name, gender, birthDate, birthTime, birthPlace, sect = 1) {
  // 计算八字
  const bazi = calculateBazi(birthDate, birthTime, gender === '男' ? 1 : 0, sect);

  const profile = {
    userId,
    name,
    language: 'zh',
    profile: {
      birthDate,
      birthTime,
      birthPlace,
      gender,
      timezone: 'Asia/Shanghai'
    },
    bazi: {
      year: bazi?.year || '',
      month: bazi?.month || '',
      day: bazi?.day || '',
      hour: bazi?.hour || '',
      dayStem: bazi?.dayStem || '',
      zodiac: bazi?.zodiac || '',
      sect: sect === 1 ? '晚子时' : '早子时',
      source: 'verified',
      analysis: bazi ? runFullAnalysis(bazi) : null
    },
    ziwei: {
      mingGong: '',
      mingZhu: '',
      source: 'pending'
    },
    family: {
      spouse: {
        name: '配偶',
        profile: {
          birthDate: '待录入',
          birthTime: '待录入',
          birthPlace: '',
          gender: gender === '男' ? '女' : '男',
          lunarBirth: ''
        },
        bazi: {
          year: '',
          month: '',
          day: '',
          hour: '',
          source: 'pending'
        }
      },
      father: {
        name: '父亲',
        profile: {
          birthDate: '待录入',
          birthTime: '待录入',
          birthPlace: '',
          gender: '男'
        },
        bazi: {
          year: '',
          month: '',
          day: '',
          hour: '',
          source: 'pending'
        }
      },
      mother: {
        name: '母亲',
        profile: {
          birthDate: '待录入',
          birthTime: '待录入',
          birthPlace: '',
          gender: '女'
        },
        bazi: {
          year: '',
          month: '',
          day: '',
          hour: '',
          source: 'pending'
        }
      },
      children: []
    },
    preferences: {
      pushMorning: true,
      pushEvening: false,
      morningTime: '07:00',
      eveningTime: '20:00',
      channels: ['telegram'],
      focusAreas: ['事业', '财运', '健康'],
      riskTolerance: '中等'
    },
    settings: {
      defaultSect: sect,
      lunarCalendar: true,
      notifications: {
        dailyFortune: true,
        riskAlert: true,
        weeklySummary: false
      }
    },
    createdAt: new Date().toISOString().split('T')[0],
    updatedAt: new Date().toISOString().split('T')[0]
  };

  return profile;
}

/**
 * 保存档案
 */
function saveProfile(userId, profile) {
  const dir = path.join(__dirname, '../data/profiles');
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const filePath = path.join(dir, `${userId}.json`);
  fs.writeFileSync(filePath, JSON.stringify(profile, null, 2), 'utf8');
  return filePath;
}

// 主入口
const args = process.argv.slice(2);

if (args.length < 5) {
  console.log(`
📝 快速注册用户

用法:
  node register.js <userId> <姓名> <性别> <出生日期> <出生时间> [出生地点] [子时]

参数:
  userId      - 用户ID（telegram id或其他唯一标识）
  姓名        - 用户姓名
  性别        - 男 或 女
  出生日期    - YYYY-MM-DD
  出生时间    - HH:MM（24小时制）
  出生地点    - 省市（可选，默认上海）
  子时        - 1=晚子时(23点后算次日)，2=早子时(可选，默认1)

示例:
  node register.js 123456 张三 男 1990-05-15 14:30 上海
  node register.js 123456 李四 女 1995-08-20 23:45 北京 1

说明:
  子时(23:00-01:00)出生需要特别注意：
  - 晚子时(1): 23:00后算次日日柱
  - 早子时(2): 23:00后算当日日柱
`);
  process.exit(1);
}

const userId = args[0];
const name = args[1];
const gender = args[2];
const birthDate = args[3];
const birthTime = args[4];
const birthPlace = args[5] || '上海';
const sect = parseInt(args[6] || '1');

// 验证
if (!['男', '女'].includes(gender)) {
  console.error('性别必须是"男"或"女"');
  process.exit(1);
}

const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
if (!dateRegex.test(birthDate)) {
  console.error('出生日期格式错误，请使用 YYYY-MM-DD');
  process.exit(1);
}

const timeRegex = /^\d{2}:\d{2}$/;
if (!timeRegex.test(birthTime)) {
  console.error('出生时间格式错误，请使用 HH:MM');
  process.exit(1);
}

console.log('\n📝 正在注册用户...\n');
console.log(`  用户ID: ${userId}`);
console.log(`  姓名: ${name}`);
console.log(`  性别: ${gender}`);
console.log(`  出生: ${birthDate} ${birthTime}`);
console.log(`  地点: ${birthPlace}`);
console.log(`  子时: ${sect === 1 ? '晚子时(23点后算次日)' : '早子时(23点后算当日)'}`);
console.log('');

// 创建档案
const profile = createProfile(userId, name, gender, birthDate, birthTime, birthPlace, sect);

// 保存
const filePath = saveProfile(userId, profile);

console.log('✅ 注册成功！\n');
console.log('📊 八字信息');
console.log(`  年柱: ${profile.bazi.year}`);
console.log(`  月柱: ${profile.bazi.month}`);
console.log(`  日柱: ${profile.bazi.day}`);
console.log(`  时柱: ${profile.bazi.hour}`);
console.log(`  日主: ${profile.bazi.dayStem} (${profile.bazi.zodiac})`);
console.log('');
console.log(`📁 档案已保存: ${filePath}`);
console.log('');

// 自动开启推送（如果指定了 --push 参数）
const pushIdx = args.indexOf('--push');
if (pushIdx !== -1) {
  const channel = args[args.indexOf('--channel') + 1] || 'telegram';
  const morning = args[args.indexOf('--morning') + 1] || '08:00';
  const evening = args[args.indexOf('--evening') + 1] || '20:00';
  console.log('⏳ 正在开启每日推送...');
  try {
    const { enablePush } = require('./push-toggle');
    enablePush(userId, { morning, evening, channel });
  } catch (e) {
    console.error('推送开启失败:', e.message);
  }
} else {
  console.log('💡 提示：运行以下命令开启每日运程推送：');
  console.log(`   node scripts/push-toggle.js on ${userId}`);
  console.log('');
}

module.exports = { createProfile, saveProfile };
