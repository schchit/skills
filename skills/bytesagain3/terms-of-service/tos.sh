#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  generate) cat << 'PROMPT'
You are an expert. Help with: 生成服务条款. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  saas) cat << 'PROMPT'
You are an expert. Help with: SaaS服务条款. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  ecommerce) cat << 'PROMPT'
You are an expert. Help with: 电商条款. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  app) cat << 'PROMPT'
You are an expert. Help with: App用户协议. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  update) cat << 'PROMPT'
You are an expert. Help with: 更新通知模板. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  plain) cat << 'PROMPT'
You are an expert. Help with: 白话版解读. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Terms of Service — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  generate        生成服务条款
  saas            SaaS服务条款
  ecommerce       电商条款
  app             App用户协议
  update          更新通知模板
  plain           白话版解读

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
