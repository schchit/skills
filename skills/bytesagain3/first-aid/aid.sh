#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  guide) cat << 'PROMPT'
You are an expert. Help with: 急救总览. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  burn) cat << 'PROMPT'
You are an expert. Help with: 烧伤处理. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  wound) cat << 'PROMPT'
You are an expert. Help with: 伤口护理. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  choking) cat << 'PROMPT'
You are an expert. Help with: 噎住急救. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  cpr) cat << 'PROMPT'
You are an expert. Help with: 心肺复苏步骤. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  kit) cat << 'PROMPT'
You are an expert. Help with: 急救包清单. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  First Aid Guide — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  guide           急救总览
  burn            烧伤处理
  wound           伤口护理
  choking         噎住急救
  cpr             心肺复苏步骤
  kit             急救包清单

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
