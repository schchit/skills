#!/bin/bash
# 外出任务自动配置 - 集成测试脚本

echo "🧪 外出任务自动配置 - 集成测试"
echo "=" | awk '{printf "%0.s=" {1..50}}'; echo ""

# 测试用例
declare -a testMessages=(
  "明天 8 点去闲林职高考务视频拍摄"
  "周六下午 2 点到留家村拿茶叶"
  "今天天气不错"
  "去闲林职高"
)

declare -a expectedResults=(
  "检测到外出"
  "检测到外出"
  "未检测"
  "检测到但不完整"
)

# 运行测试
for i in "${!testMessages[@]}"; do
  message="${testMessages[$i]}"
  expected="${expectedResults[$i]}"
  
  echo ""
  echo "测试 $((i+1)): $message"
  echo "预期：$expected"
  
  # 调用技能
  result=$(node -e "
    const outboundSkill = require('./outbound-auto-setup/index.js');
    outboundSkill.handleUserMessage('$message').then(response => {
      if (response) {
        console.log('检测到外出');
      } else {
        console.log('未检测');
      }
    }).catch(err => {
      console.log('错误：' + err.message);
    });
  " 2>&1)
  
  echo "结果：$result"
  
  if [[ "$result" == *"$expected"* ]]; then
    echo "✅ 通过"
  else
    echo "❌ 失败"
  fi
done

echo ""
echo "=" | awk '{printf "%0.s=" {1..50}}'; echo ""
echo "集成测试完成！"
