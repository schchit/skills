const { containsOutboundKeywords, extractOutboundInfo } = require('../index.js');

// 测试用例
const testCases = [
  {
    name: '工作外出 - 明天',
    message: '明天 8 点去闲林职高考务视频拍摄',
    expect: {
      detected: true,
      date: '2026-03-28',
      time: '08:00',
      location: '闲林职高',
      type: 'work'
    }
  },
  {
    name: '生活外出 - 周六',
    message: '周六下午 2 点到留家村拿茶叶',
    expect: {
      detected: true,
      date: '2026-03-28',
      time: '14:00',
      location: '留家村',
      type: 'life'
    }
  },
  {
    name: '非外出消息',
    message: '今天天气不错',
    expect: {
      detected: false
    }
  },
  {
    name: '模糊时间',
    message: '去闲林职高',
    expect: {
      detected: true,
      date: null,
      time: null
    }
  }
];

// 运行测试
console.log('🧪 外出任务自动配置技能测试\n');
console.log('='.repeat(50));

let passed = 0;
let failed = 0;

testCases.forEach((testCase, index) => {
  console.log(`\n测试 ${index + 1}: ${testCase.name}`);
  
  const detected = containsOutboundKeywords(testCase.message);
  const info = extractOutboundInfo(testCase.message);
  
  if (testCase.expect.detected && !detected) {
    console.log(`  ❌ 失败：应检测到外出关键词`);
    failed++;
    return;
  }
  
  if (!testCase.expect.detected && detected) {
    console.log(`  ❌ 失败：不应检测到外出关键词`);
    failed++;
    return;
  }
  
  if (testCase.expect.detected) {
    if (testCase.expect.date && (!info || info.date !== testCase.expect.date)) {
      console.log(`  ❌ 失败：日期不匹配 (期望：${testCase.expect.date}, 实际：${info ? info.date : 'null'})`);
      failed++;
      return;
    }
    
    if (testCase.expect.time && (!info || info.time !== testCase.expect.time)) {
      console.log(`  ❌ 失败：时间不匹配 (期望：${testCase.expect.time}, 实际：${info ? info.time : 'null'})`);
      failed++;
      return;
    }
    
    if (testCase.expect.location && (!info || info.location !== testCase.expect.location)) {
      console.log(`  ❌ 失败：地点不匹配 (期望：${testCase.expect.location}, 实际：${info ? info.location : 'null'})`);
      failed++;
      return;
    }
    
    if (testCase.expect.type && (!info || info.type !== testCase.expect.type)) {
      console.log(`  ❌ 失败：类型不匹配 (期望：${testCase.expect.type}, 实际：${info ? info.type : 'null'})`);
      failed++;
      return;
    }
  }
  
  console.log(`  ✅ 通过`);
  passed++;
});

console.log('\n' + '='.repeat(50));
console.log(`\n测试结果：${passed} 通过，${failed} 失败\n`);

if (failed === 0) {
  console.log('🎉 所有测试通过！\n');
  process.exit(0);
} else {
  console.log('❌ 部分测试失败，请修复\n');
  process.exit(1);
}
