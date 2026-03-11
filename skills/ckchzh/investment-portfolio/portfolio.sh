#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  allocate) cat << 'PROMPT'
You are an expert. Help with: 资产配置建议. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  risk) cat << 'PROMPT'
You are an expert. Help with: 风险评估. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  rebalance) cat << 'PROMPT'
You are an expert. Help with: 再平衡策略. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  return) cat << 'PROMPT'
You are an expert. Help with: 收益分析. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  diversify) cat << 'PROMPT'
You are an expert. Help with: 分散化检查. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  backtest) cat << 'PROMPT'
You are an expert. Help with: 历史回测. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Investment Portfolio — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  allocate        资产配置建议
  risk            风险评估
  rebalance       再平衡策略
  return          收益分析
  diversify       分散化检查
  backtest        历史回测

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
