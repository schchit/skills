#!/bin/bash
# 抖音工作流环境配置助手
# 配置所有必需的环境变量

echo "🔧 抖音工作流环境配置"
echo "======================"
echo ""
echo "⚠️  注意：您的输入将被保存到 ~/.bashrc"
echo ""

# 检查是否已经配置
if grep -q "DOUYIN_WORKFLOW_CONFIG" ~/.bashrc 2>/dev/null; then
    echo "⚠️  检测到已有配置"
    read -p "是否覆盖现有配置？(y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "已取消配置"
        exit 0
    fi
    # 删除旧配置
    sed -i '/# === DOUYIN_WORKFLOW_CONFIG/,/# === END_DOUYIN_WORKFLOW_CONFIG/d' ~/.bashrc
fi

echo ""
echo "📋 请输入阿里云OSS配置："
echo "------------------------------"
read -p "Access Key ID: " access_key_id
read -sp "Access Key Secret (输入时不会显示): " access_key_secret
echo ""
read -p "Endpoint [https://oss-cn-beijing.aliyuncs.com]: " endpoint
endpoint=${endpoint:-https://oss-cn-beijing.aliyuncs.com}
read -p "Bucket名称: " bucket

echo ""
echo "📋 请输入飞书多维表格配置（可选，按回车跳过）："
echo "------------------------------------------------"
read -p "App Token (可选): " app_token
read -p "Table ID (可选): " table_id

# 写入 .bashrc
cat << EOF >> ~/.bashrc

# === DOUYIN_WORKFLOW_CONFIG ===
# 抖音视频工作流配置
# 生成时间: $(date '+%Y-%m-%d %H:%M:%S')
export ALIYUN_OSS_ACCESS_KEY_ID="$access_key_id"
export ALIYUN_OSS_ACCESS_KEY_SECRET="$access_key_secret"
export ALIYUN_OSS_ENDPOINT="$endpoint"
export ALIYUN_OSS_BUCKET="$bucket"
EOF

if [ -n "$app_token" ]; then
    echo "export FEISHU_BITABLE_APP_TOKEN=\"$app_token\"" >> ~/.bashrc
fi

if [ -n "$table_id" ]; then
    echo "export FEISHU_BITABLE_TABLE_ID=\"$table_id\"" >> ~/.bashrc
fi

cat << EOF >> ~/.bashrc
# === END_DOUYIN_WORKFLOW_CONFIG ===
EOF

echo ""
echo "✅ 配置已保存到 ~/.bashrc"
echo ""
echo "⚠️  请运行以下命令使配置生效："
echo "   source ~/.bashrc"
echo ""
echo "📝 验证配置："
echo "   python3 ~/.openclaw/workspace/skills/douyin-workflow/scripts/workflow.py"
echo "   （不输入链接时会显示环境检查）
