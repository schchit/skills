#!/bin/bash

# Team Memory - 创建新成员时间轴
# 用法: bash new-member.sh [姓名] [角色] [入职日期]
# 示例: bash new-member.sh 张三 后端开发工程师 2023-03-15

set -e

SKILL_DIR="$HOME/.config/opencode/skills/team-memory"
MEMBERS_DIR="$SKILL_DIR/data/members"
TEMPLATE_FILE="$SKILL_DIR/data/members/模板-成员时间轴.md"

# 检查参数
if [ -z "$1" ]; then
    echo "❌ 用法: bash new-member.sh [姓名] [角色] [入职日期]"
    echo "   示例: bash new-member.sh 张三 后端开发 2023-03-15"
    exit 1
fi

NAME="$1"
ROLE="${2:-职位未填写}"
JOIN_DATE="${3:-$(date +%Y-%m-%d)}"

# 生成文件名
FILENAME="$MEMBERS_DIR/$NAME-时间轴.md"

# 检查是否已存在
if [ -f "$FILENAME" ]; then
    echo "⚠️  文件已存在: $FILENAME"
    read -p "是否覆盖? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 已取消"
        exit 1
    fi
fi

# 生成成员ID（基于已有文件数量）
MEMBER_COUNT=$(ls -1 "$MEMBERS_DIR"/*.md 2>/dev/null | wc -l || echo "0")
MEMBER_ID=$(printf "member-%03d" $((MEMBER_COUNT + 1)))

echo "📝 创建成员时间轴..."
echo "   姓名: $NAME"
echo "   角色: $ROLE"
echo "   入职: $JOIN_DATE"
echo "   ID: $MEMBER_ID"

# 创建时间轴文件
cat > "$FILENAME" << EOF
# $NAME - 团队记忆时间轴

> **成员ID**: $MEMBER_ID  
> **角色**: $ROLE  
> **入职时间**: $JOIN_DATE  
> **所属团队**:   
> **管理备注**: 

## 📍 快速定位
**最近状态**:   
**重点关注**:   
**下次1:1**:   
**标签云**: 

---

## 🕐 时间轴（从新到旧）

<!-- 从这里开始添加记录 -->

<!-- 示例记录：
### $(date +%Y-%m-%d)
#### 00:00 - 
**事件**:  
**类别**: 
**评价**: 
**标签**: 

**观察笔记**:  
- 

**后续行动**:  
- [ ] 
-->

---

*创建于 $JOIN_DATE*
EOF

echo ""
echo "✅ 已创建: $FILENAME"
echo ""
echo "📝 下一步:"
echo "   1. 编辑 $FILENAME 完善信息"
echo "   2. 更新 skill-config.yaml 添加成员映射"
echo ""
